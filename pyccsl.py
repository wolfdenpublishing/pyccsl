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

__version__ = "0.1.2"

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

def main():
    """Main entry point."""
    # Parse arguments
    config = parse_arguments()
    
    # Read input
    input_data = read_input()
    
    # Extract model info
    model_info = extract_model_info(input_data)
    
    # For now, just print the model name
    print(model_info["display_name"])
    
    return 0

if __name__ == "__main__":
    sys.exit(main())