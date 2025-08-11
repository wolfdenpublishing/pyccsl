#!/usr/bin/env python3
"""
pyccsl - Python Claude Code Status Line
Generates a customizable status line for Claude Code showing performance metrics,
git status, session information, and cost calculations.
"""

import sys
import json
import os
import subprocess
from datetime import datetime, timedelta
import argparse

__version__ = "0.2.13"

# Pricing data embedded from https://docs.anthropic.com/en/docs/about-claude/pricing
# All prices in USD per million tokens
PRICING_DATA = {
    "claude-opus-4-1-20250805": {
        "name": "Claude Opus 4.1",
        "input": 15.00,
        "cache_write_5m": 18.75,
        "cache_write_1h": 30.00,
        "cache_read": 1.50,
        "output": 75.00
    },
    "claude-opus-4-20250514": {
        "name": "Claude Opus 4",
        "input": 15.00,
        "cache_write_5m": 18.75,
        "cache_write_1h": 30.00,
        "cache_read": 1.50,
        "output": 75.00
    },
    "claude-sonnet-4-20250514": {
        "name": "Claude Sonnet 4",
        "input": 3.00,
        "cache_write_5m": 3.75,
        "cache_write_1h": 6.00,
        "cache_read": 0.30,
        "output": 15.00
    },
    "claude-3-7-sonnet-20250219": {
        "name": "Claude Sonnet 3.7",
        "input": 3.00,
        "cache_write_5m": 3.75,
        "cache_write_1h": 6.00,
        "cache_read": 0.30,
        "output": 15.00
    },
    "claude-3-5-sonnet-20241022": {
        "name": "Claude Sonnet 3.5",
        "input": 3.00,
        "cache_write_5m": 3.75,
        "cache_write_1h": 6.00,
        "cache_read": 0.30,
        "output": 15.00
    },
    "claude-3-5-sonnet-20240620": {
        "name": "Claude Sonnet 3.5",
        "input": 3.00,
        "cache_write_5m": 3.75,
        "cache_write_1h": 6.00,
        "cache_read": 0.30,
        "output": 15.00
    },
    "claude-3-5-haiku-20241022": {
        "name": "Claude Haiku 3.5",
        "input": 0.80,
        "cache_write_5m": 1.00,
        "cache_write_1h": 1.60,
        "cache_read": 0.08,
        "output": 4.00
    },
    "claude-3-haiku-20240307": {
        "name": "Claude Haiku 3",
        "input": 0.25,
        "cache_write_5m": 0.30,
        "cache_write_1h": 0.50,
        "cache_read": 0.03,
        "output": 1.25
    }
}

# Default field list
DEFAULT_FIELDS = ["badge", "folder", "git", "model", "context", "cost"]

# All available fields in display order
FIELD_ORDER = [
    "badge",
    "folder", 
    "git",
    "model",
    "perf-cache-rate",
    "perf-response-time",
    "perf-session-time",
    "perf-token-rate",
    "perf-message-count",
    "perf-all-metrics",
    "input",
    "output",
    "context",
    "cost"
]

def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Claude Code status line generator",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Theme option
    parser.add_argument(
        "--theme",
        choices=["default", "solarized", "nord", "dracula", "gruvbox", 
                 "tokyo", "catppuccin", "minimal", "none"],
        default=os.environ.get("PYCCSL_THEME", "default"),
        help="Color theme (default: default)"
    )
    
    # Number formatting option
    parser.add_argument(
        "--numbers",
        choices=["compact", "full", "raw"],
        default=os.environ.get("PYCCSL_NUMBERS", "compact"),
        help="Number formatting (default: compact)"
    )
    
    # Style option
    parser.add_argument(
        "--style",
        choices=["powerline", "simple", "arrows", "pipes", "dots"],
        default=os.environ.get("PYCCSL_STYLE", "simple"),
        help="Separator style (default: simple)"
    )
    
    # No emoji option
    parser.add_argument(
        "--no-emoji",
        action="store_true",
        default=os.environ.get("PYCCSL_NO_EMOJI", "false").lower() == "true",
        help="Disable emoji in output"
    )
    
    # Performance thresholds - cache
    parser.add_argument(
        "--perf-cache",
        default=os.environ.get("PYCCSL_PERF_CACHE", "60,40,20"),
        help="Cache hit rate thresholds (green,yellow,orange) (default: 60,40,20)"
    )
    
    # Performance thresholds - response
    parser.add_argument(
        "--perf-response",
        default=os.environ.get("PYCCSL_PERF_RESPONSE", "3,5,8"),
        help="Response time thresholds (green,yellow,orange) (default: 3,5,8)"
    )
    
    # Fields to display (positional argument)
    parser.add_argument(
        "fields",
        nargs="?",
        default=os.environ.get("PYCCSL_FIELDS", None),
        help="Comma-separated list of fields to display"
    )
    
    args = parser.parse_args()
    
    # Parse fields
    if args.fields:
        # Split comma-separated fields and strip whitespace
        fields = [f.strip() for f in args.fields.split(",")]
    else:
        fields = DEFAULT_FIELDS.copy()
    
    # Parse threshold values
    try:
        cache_thresholds = [float(x) for x in args.perf_cache.split(",")]
        if len(cache_thresholds) != 3:
            raise ValueError("Need exactly 3 cache thresholds")
    except (ValueError, AttributeError):
        print("Error: Invalid cache thresholds format", file=sys.stderr)
        sys.exit(1)
    
    try:
        response_thresholds = [float(x) for x in args.perf_response.split(",")]
        if len(response_thresholds) != 3:
            raise ValueError("Need exactly 3 response thresholds")
    except (ValueError, AttributeError):
        print("Error: Invalid response thresholds format", file=sys.stderr)
        sys.exit(1)
    
    return {
        "theme": args.theme,
        "numbers": args.numbers,
        "style": args.style,
        "no_emoji": args.no_emoji,
        "cache_thresholds": cache_thresholds,
        "response_thresholds": response_thresholds,
        "fields": fields
    }

def read_input():
    """Read and parse JSON input from stdin."""
    try:
        # Check if stdin has data (not a terminal)
        if sys.stdin.isatty():
            print("Error: No input provided. Expected JSON via stdin.", file=sys.stderr)
            sys.exit(2)
        
        # Read from stdin
        input_data = sys.stdin.read()
        
        if not input_data.strip():
            print("Error: Empty input received.", file=sys.stderr)
            sys.exit(2)
        
        # Parse JSON
        try:
            data = json.loads(input_data)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
            sys.exit(2)
        
        return data
        
    except Exception as e:
        print(f"Error reading input: {e}", file=sys.stderr)
        sys.exit(2)

def extract_model_info(data):
    """Extract model information from input data."""
    try:
        # Try to get model display_name
        if "model" in data and isinstance(data["model"], dict):
            display_name = data["model"].get("display_name", "Unknown")
            model_id = data["model"].get("id", None)
            return {"display_name": display_name, "id": model_id}
        else:
            # Fallback if model not present
            return {"display_name": "Unknown", "id": None}
    except Exception:
        return {"display_name": "Unknown", "id": None}

def extract_git_status(input_data):
    """Extract git status information from the current directory.
    
    Returns a dict with:
    - branch: Current branch name or None
    - modified_count: Number of modified/staged files or 0
    """
    try:
        # Get working directory from input or use current
        cwd = input_data.get("cwd", os.getcwd())
        
        # Get current branch name
        branch_result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=2
        )
        
        if branch_result.returncode != 0:
            # Not a git repository
            return {"branch": None, "modified_count": 0}
        
        branch = branch_result.stdout.strip()
        
        # Get modified file count using porcelain format
        status_result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=2
        )
        
        # Count non-empty lines (each represents a modified file)
        modified_count = 0
        if status_result.returncode == 0:
            modified_count = len([line for line in status_result.stdout.splitlines() if line.strip()])
        
        return {"branch": branch, "modified_count": modified_count}
        
    except (subprocess.TimeoutExpired, FileNotFoundError):
        # Git not available or timeout
        return {"branch": None, "modified_count": 0}
    except Exception:
        # Any other error - fail silently
        return {"branch": None, "modified_count": 0}

def get_model_pricing(model_id):
    """Get pricing information for a model ID.
    
    Returns a dict with pricing info or None if model not found.
    """
    if model_id and model_id in PRICING_DATA:
        return PRICING_DATA[model_id]
    return None

def load_transcript(transcript_path):
    """Load and parse a Claude Code transcript JSONL file.
    
    Args:
        transcript_path: Path to the transcript file
    
    Returns:
        List of parsed JSON entries, or empty list on error
    """
    if not transcript_path:
        return []
    
    try:
        entries = []
        with open(transcript_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue  # Skip empty lines
                try:
                    entry = json.loads(line)
                    entries.append(entry)
                except json.JSONDecodeError as e:
                    # Log error but continue processing other lines
                    print(f"Warning: Invalid JSON at line {line_num} in transcript: {e}", file=sys.stderr)
                    continue
        return entries
    except FileNotFoundError:
        # Transcript file not found - this is expected sometimes
        return []
    except Exception as e:
        # Other errors reading file
        print(f"Warning: Error reading transcript file: {e}", file=sys.stderr)
        return []

def calculate_token_usage(transcript_entries):
    """Calculate total token usage from transcript entries.
    
    Args:
        transcript_entries: List of parsed transcript entries
    
    Returns:
        Dict with token totals: input_tokens, output_tokens, 
        cache_creation_tokens, cache_read_tokens
    """
    totals = {
        "input_tokens": 0,
        "output_tokens": 0,
        "cache_creation_tokens": 0,
        "cache_read_tokens": 0
    }
    
    for entry in transcript_entries:
        usage = None
        
        # Check for usage in assistant messages
        if entry.get("type") == "assistant" and "message" in entry:
            usage = entry["message"].get("usage", {})
        
        # Check for usage in tool use results (only if it's a dict)
        elif "toolUseResult" in entry and isinstance(entry["toolUseResult"], dict):
            usage = entry["toolUseResult"].get("usage", {})
        
        if usage:
            # Add tokens to totals
            totals["input_tokens"] += usage.get("input_tokens", 0)
            totals["output_tokens"] += usage.get("output_tokens", 0)
            totals["cache_creation_tokens"] += usage.get("cache_creation_input_tokens", 0)
            totals["cache_read_tokens"] += usage.get("cache_read_input_tokens", 0)
    
    return totals

def get_model_from_transcript(transcript_entries):
    """Extract the model ID from transcript entries.
    
    Looks for the first assistant message with a model ID.
    
    Args:
        transcript_entries: List of parsed transcript entries
    
    Returns:
        Model ID string or None if not found
    """
    for entry in transcript_entries:
        if entry.get("type") == "assistant" and "message" in entry:
            model_id = entry["message"].get("model")
            if model_id:
                return model_id
    return None

def calculate_cost(token_totals, model_id):
    """Calculate session cost from token totals and model pricing.
    
    Args:
        token_totals: Dict with input_tokens, output_tokens, 
                      cache_creation_tokens, cache_read_tokens
        model_id: Model ID string for pricing lookup
    
    Returns:
        Cost in dollars (float) or 0.0 if model not found
    """
    pricing = get_model_pricing(model_id)
    if not pricing:
        return 0.0
    
    # Calculate cost using the formula (all rates are per million tokens)
    # Using 5-minute cache write rate (Claude Code default)
    cost = (
        token_totals.get("input_tokens", 0) * pricing.get("input", 0) +
        token_totals.get("cache_creation_tokens", 0) * pricing.get("cache_write_5m", 0) +
        token_totals.get("cache_read_tokens", 0) * pricing.get("cache_read", 0) +
        token_totals.get("output_tokens", 0) * pricing.get("output", 0)
    ) / 1_000_000
    
    return cost

def format_cost(cost):
    """Format cost as dollars or cents.
    
    Args:
        cost: Cost in dollars (float)
    
    Returns:
        Formatted string (e.g., "$1.25" or "48¢")
    """
    if cost >= 1.0:
        return f"${cost:.2f}"
    else:
        cents = int(round(cost * 100))
        return f"{cents}¢"

def format_number(value, style="compact"):
    """Format a number based on style preference.
    
    Args:
        value: Number to format
        style: "compact" (1.2K), "full" (1,234), or "raw" (1234)
    
    Returns:
        Formatted string
    """
    if style == "compact":
        if value >= 1_000_000:
            return f"{value/1_000_000:.1f}M"
        elif value >= 1_000:
            return f"{value/1_000:.1f}K"
        else:
            return str(value)
    elif style == "full":
        return f"{value:,}"
    else:  # raw
        return str(value)

def calculate_performance_badge(cache_hit_rate, avg_response_time, cache_thresholds, response_thresholds):
    """Calculate performance badge based on metrics and thresholds.
    
    Args:
        cache_hit_rate: Cache hit rate (0.0 to 1.0)
        avg_response_time: Average response time in seconds
        cache_thresholds: List of [green, yellow, orange] thresholds for cache hit rate
        response_thresholds: List of [green, yellow, orange] thresholds for response time
    
    Returns:
        Badge string (e.g., "●○○○", "○●○○", "○○●○", "○○○●")
    """
    # Calculate performance level for cache hit rate (higher is better)
    cache_percent = cache_hit_rate * 100
    if cache_percent >= cache_thresholds[0]:
        cache_level = 0  # Green
    elif cache_percent >= cache_thresholds[1]:
        cache_level = 1  # Yellow
    elif cache_percent >= cache_thresholds[2]:
        cache_level = 2  # Orange
    else:
        cache_level = 3  # Red
    
    # Calculate performance level for response time (lower is better)
    if avg_response_time <= response_thresholds[0]:
        response_level = 0  # Green
    elif avg_response_time <= response_thresholds[1]:
        response_level = 1  # Yellow
    elif avg_response_time <= response_thresholds[2]:
        response_level = 2  # Orange
    else:
        response_level = 3  # Red
    
    # Combine metrics (take the worse of the two)
    overall_level = max(cache_level, response_level)
    
    # Generate badge string
    badges = ["●○○○", "○●○○", "○○●○", "○○○●"]
    return badges[overall_level]

def calculate_performance_metrics(transcript_entries, token_totals):
    """Calculate performance metrics from transcript.
    
    Args:
        transcript_entries: List of parsed transcript entries
        token_totals: Dict with token usage totals
    
    Returns:
        Dict with performance metrics
    """
    metrics = {}
    
    # Calculate cache hit rate
    total_input = (token_totals.get("input_tokens", 0) + 
                   token_totals.get("cache_creation_tokens", 0) + 
                   token_totals.get("cache_read_tokens", 0))
    if total_input > 0:
        cache_hit_rate = token_totals.get("cache_read_tokens", 0) / total_input
        metrics["cache_hit_rate"] = cache_hit_rate
    else:
        metrics["cache_hit_rate"] = 0.0
    
    # Calculate response times, token rates, and count messages
    user_timestamps = []
    assistant_timestamps = []
    response_times = []
    token_rates = []  # Token generation rates per response
    
    for entry in transcript_entries:
        timestamp_str = entry.get("timestamp")
        if not timestamp_str:
            continue
            
        entry_type = entry.get("type")
        if entry_type == "user":
            try:
                # Parse ISO format timestamp
                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                user_timestamps.append(timestamp)
            except:
                pass
        elif entry_type == "assistant":
            try:
                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                assistant_timestamps.append(timestamp)
                
                # Calculate response time if we have a preceding user message
                if user_timestamps and len(assistant_timestamps) <= len(user_timestamps):
                    # Match with the most recent user message
                    user_time = user_timestamps[len(assistant_timestamps) - 1]
                    response_time = (timestamp - user_time).total_seconds()
                    if response_time >= 0:  # Sanity check
                        response_times.append(response_time)
                        
                        # Calculate token generation rate for this response
                        if "message" in entry and "usage" in entry["message"]:
                            output_tokens = entry["message"]["usage"].get("output_tokens", 0)
                            if response_time > 0 and output_tokens > 0:
                                token_rate = output_tokens / response_time
                                token_rates.append(token_rate)
            except:
                pass
    
    # Average response time
    if response_times:
        metrics["avg_response_time"] = sum(response_times) / len(response_times)
    else:
        metrics["avg_response_time"] = 0.0
    
    # Average token generation rate (per response, not per session)
    if token_rates:
        metrics["token_rate"] = sum(token_rates) / len(token_rates)
    else:
        metrics["token_rate"] = 0.0
    
    # Message count
    metrics["message_count"] = len(user_timestamps)
    
    # Session duration
    all_timestamps = user_timestamps + assistant_timestamps
    if len(all_timestamps) >= 2:
        all_timestamps.sort()
        session_duration = (all_timestamps[-1] - all_timestamps[0]).total_seconds()
        metrics["session_duration"] = session_duration
    else:
        metrics["session_duration"] = 0.0
    
    return metrics

def format_duration(seconds):
    """Format duration in seconds to human-readable format."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.0f}m"
    else:
        hours = seconds / 3600
        if hours < 24:
            return f"{hours:.1f}h"
        else:
            days = hours / 24
            return f"{days:.0f}d"

def format_output(config, model_info, input_data, metrics=None):
    """Format the output based on selected fields and configuration.
    
    Args:
        config: Configuration dict from parse_arguments()
        model_info: Model information dict with display_name and id
        input_data: Full input JSON data
        metrics: Dict with calculated metrics (cost, tokens, etc.)
    
    Returns:
        Formatted string for output
    """
    if metrics is None:
        metrics = {}
    
    output_parts = []
    
    # Get separator based on style
    if config["style"] == "pipes":
        separator = " | "
    elif config["style"] == "arrows":
        separator = " → "
    elif config["style"] == "dots":
        separator = " · "
    elif config["style"] == "powerline":
        separator = " > "  # Will be enhanced in future phases
    else:  # simple
        separator = " > "
    
    # Process fields in FIELD_ORDER sequence
    for field in FIELD_ORDER:
        if field not in config["fields"]:
            continue
            
        # Handle different fields
        if field == "badge" and "badge" in metrics:
            output_parts.append(metrics["badge"])
        elif field == "model":
            output_parts.append(model_info["display_name"])
        elif field == "folder":
            # Extract folder name from cwd
            cwd = input_data.get("cwd", os.getcwd())
            folder_name = os.path.basename(cwd)
            # Handle root directory
            if not folder_name:
                folder_name = "/" if cwd == "/" else os.path.basename(os.path.dirname(cwd))
            # Truncate if too long
            if len(folder_name) > 20:
                folder_name = folder_name[:17] + "..."
            output_parts.append(folder_name)
        elif field == "input" and any(k in metrics for k in ["input_tokens", "cache_creation_tokens", "cache_read_tokens"]):
            # Display as tuple: (base, cache_write, cache_read)
            base = format_number(metrics.get("input_tokens", 0), config["numbers"])
            cache_write = format_number(metrics.get("cache_creation_tokens", 0), config["numbers"])
            cache_read = format_number(metrics.get("cache_read_tokens", 0), config["numbers"])
            output_parts.append(f"↑ ({base}, {cache_write}, {cache_read})")
        elif field == "output" and "output_tokens" in metrics:
            output_parts.append(f"↓ {format_number(metrics['output_tokens'], config['numbers'])}")
        elif field == "context" and "context_size" in metrics:
            output_parts.append(f"⧉ {format_number(metrics['context_size'], config['numbers'])}")
        elif field == "cost" and "cost_formatted" in metrics:
            output_parts.append(metrics["cost_formatted"])
        elif field == "git" and "git_info" in metrics:
            # Format git status: "branch ●" if modified, "branch" if clean
            branch = metrics["git_info"]["branch"]
            modified = metrics["git_info"]["modified_count"]
            if modified > 0:
                output_parts.append(f"{branch} ●")
            else:
                output_parts.append(branch)
        elif field == "perf-cache-rate" and "cache_hit_rate" in metrics:
            # Format cache hit rate as percentage
            rate = metrics["cache_hit_rate"] * 100
            if config["no_emoji"]:
                output_parts.append(f"Cache: {rate:.0f}%")
            else:
                output_parts.append(f"⚡{rate:.0f}%")
        elif field == "perf-response-time" and "avg_response_time" in metrics:
            # Format average response time
            time_str = format_duration(metrics["avg_response_time"])
            if config["no_emoji"]:
                output_parts.append(f"Response: {time_str}")
            else:
                output_parts.append(f"⏱{time_str}")
        elif field == "perf-session-time" and "session_duration" in metrics:
            # Format session duration
            time_str = format_duration(metrics["session_duration"])
            if config["no_emoji"]:
                output_parts.append(f"Session: {time_str}")
            else:
                output_parts.append(f"🕐{time_str}")
        elif field == "perf-token-rate" and "token_rate" in metrics:
            # Format token generation rate
            rate = metrics["token_rate"]
            if config["no_emoji"]:
                output_parts.append(f"Rate: {rate:.0f} t/s")
            else:
                output_parts.append(f"⚙{rate:.0f} t/s")
        elif field == "perf-message-count" and "message_count" in metrics:
            # Format message count
            count = metrics["message_count"]
            if config["no_emoji"]:
                output_parts.append(f"Messages: {count}")
            else:
                output_parts.append(f"💬{count}")
        elif field == "perf-all-metrics":
            # Show all performance metrics together
            perf_parts = []
            if "cache_hit_rate" in metrics:
                rate = metrics["cache_hit_rate"] * 100
                perf_parts.append(f"⚡{rate:.0f}%" if not config["no_emoji"] else f"Cache: {rate:.0f}%")
            if "avg_response_time" in metrics:
                time_str = format_duration(metrics["avg_response_time"])
                perf_parts.append(f"⏱{time_str}" if not config["no_emoji"] else f"Response: {time_str}")
            if "session_duration" in metrics:
                time_str = format_duration(metrics["session_duration"])
                perf_parts.append(f"🕐{time_str}" if not config["no_emoji"] else f"Session: {time_str}")
            if "token_rate" in metrics:
                rate = metrics["token_rate"]
                perf_parts.append(f"⚙{rate:.0f} t/s" if not config["no_emoji"] else f"Rate: {rate:.0f} t/s")
            if "message_count" in metrics:
                count = metrics["message_count"]
                perf_parts.append(f"💬{count}" if not config["no_emoji"] else f"Messages: {count}")
            if perf_parts:
                output_parts.append(" ".join(perf_parts))
        # All fields have been implemented
    
    # Join parts with separator
    return separator.join(output_parts)

def main():
    """Main entry point."""
    # Parse arguments
    config = parse_arguments()
    
    # Read input
    input_data = read_input()
    
    # Extract model info
    model_info = extract_model_info(input_data)
    
    # Extract git status
    git_info = extract_git_status(input_data)
    
    # Load transcript if provided
    transcript_path = input_data.get("transcript_path", None)
    transcript_entries = load_transcript(transcript_path)
    
    # Calculate metrics from transcript
    metrics = {}
    if transcript_entries:
        # Calculate token usage
        token_totals = calculate_token_usage(transcript_entries)
        metrics.update(token_totals)
        
        # Calculate context size (everything except cache reads)
        context_size = (token_totals.get("input_tokens", 0) + 
                       token_totals.get("cache_creation_tokens", 0) + 
                       token_totals.get("output_tokens", 0))
        metrics["context_size"] = context_size
        
        # Get model ID (from transcript or input)
        model_id = get_model_from_transcript(transcript_entries) or model_info.get("id")
        
        # Calculate cost
        if model_id:
            cost = calculate_cost(token_totals, model_id)
            metrics["cost"] = cost
            metrics["cost_formatted"] = format_cost(cost)
        
        # Calculate performance metrics
        perf_metrics = calculate_performance_metrics(transcript_entries, token_totals)
        metrics.update(perf_metrics)
        
        # Calculate performance badge
        if "cache_hit_rate" in metrics and "avg_response_time" in metrics:
            badge = calculate_performance_badge(
                metrics["cache_hit_rate"],
                metrics["avg_response_time"],
                config["cache_thresholds"],
                config["response_thresholds"]
            )
            metrics["badge"] = badge
    
    # Add git info to metrics
    if git_info["branch"]:
        metrics["git_info"] = git_info
    
    # Format and output (pass metrics for field display)
    output = format_output(config, model_info, input_data, metrics)
    print(output)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())