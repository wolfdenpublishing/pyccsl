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

__version__ = "0.2.5"

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
DEFAULT_FIELDS = ["badge", "folder", "git", "model", "input", "output", "cost"]

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

def format_output(config, model_info, input_data):
    """Format the output based on selected fields and configuration.
    
    Args:
        config: Configuration dict from parse_arguments()
        model_info: Model information dict with display_name and id
        input_data: Full input JSON data
    
    Returns:
        Formatted string for output
    """
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
            
        # For now, only handle model field
        if field == "model":
            output_parts.append(model_info["display_name"])
        # Other fields will be implemented in future phases
        # For now, skip them silently
    
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
    
    # Load transcript if provided
    transcript_path = input_data.get("transcript_path", None)
    transcript_entries = load_transcript(transcript_path)
    
    # Calculate metrics from transcript
    metrics = {}
    if transcript_entries:
        token_totals = calculate_token_usage(transcript_entries)
        metrics.update(token_totals)
    
    # Format and output
    output = format_output(config, model_info, input_data)
    print(output)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())