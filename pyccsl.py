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

__version__ = "0.1.1"

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

def main():
    """Main entry point."""
    # Parse arguments
    config = parse_arguments()
    
    # For now, just print the parsed configuration
    print(f"pyccsl v{__version__} - Configuration parsed successfully")
    print(f"Theme: {config['theme']}")
    print(f"Fields: {', '.join(config['fields'])}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())