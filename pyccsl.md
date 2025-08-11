# pyccsl - Python Claude Code Status Line

> **GitHub Repository**: [https://github.com/wolfdenpublishing/pyccsl](https://github.com/wolfdenpublishing/pyccsl)

## Overview

`pyccsl` (pronounced "pixel") is a Python-based status line generator for Claude Code that analyzes transcript files to provide performance metrics, session information, and cost calculations. It reads JSON input from stdin and outputs a formatted status line to stdout.

## Installation

1. Copy `pyccsl.py` to your Claude home directory:
   ```bash
   cp pyccsl.py ~/.claude/
   ```

2. Add to your Claude Code settings file (`~/.claude/settings.json`):
   ```json
   {
     "statusLine": {
       "type": "command",
       "command": "python3 ~/.claude/pyccsl.py"
     }
   }
   ```

## Prerequisites

- Python 3.8 or higher
- No external dependencies (uses only Python standard library modules: `sys`, `json`, `os`, `subprocess`, `datetime`, `argparse`)

## Usage

```bash
pyccsl [OPTIONS] [FIELDS]
```

Options must come first, followed by an optional comma-separated list of fields to display.

## Command Line Options

### `--theme THEME`
Set color theme. Options:
- `default` - Vibrant colors (default)
- `solarized` - Solarized color scheme
- `nord` - Nord theme
- `dracula` - Dracula theme
- `gruvbox` - Gruvbox theme
- `tokyo` - Tokyo Night theme
- `catppuccin` - Catppuccin theme
- `minimal` - Grayscale theme
- `none` - No colors

### `--numbers FORMAT`
Set number formatting:
- `compact` - 1.2K (default)
- `full` - 1,234
- `raw` - 1234

### `--style STYLE`
Set separator style:
- `powerline` - Powerline arrows (requires Powerline fonts)
- `simple` - Plain text separators (default)
- `arrows` - Arrow separators (→)
- `pipes` - Pipe separators (|)
- `dots` - Dot separators (·)

### `--no-emoji`
Disable emoji in output (useful for terminals without emoji support).

### `--perf-cache GREEN,YELLOW,ORANGE`
Set cache hit rate thresholds (percentages).
- Default: `60,40,20`
- Example: `--perf-cache 70,50,30`
- Interpretation: ≥70% = green, ≥50% = yellow, ≥30% = orange, <30% = red

### `--perf-response GREEN,YELLOW,ORANGE`
Set response time thresholds (seconds).
- Default: `3,5,8`
- Example: `--perf-response 2,4,6`
- Interpretation: ≤2s = green, ≤4s = yellow, ≤6s = orange, >6s = red

## Display Fields

Fields are specified as a comma-separated list at the end of the command. If no fields are specified, the default fields (marked with *) are shown.

Fields are always displayed in this order, regardless of how they're specified:

| Field | Description | Default |
|-------|-------------|---------|
| `badge` | Performance indicator (●○○○ style) | ✓ |
| `folder` | Current working directory name | ✓ |
| `git` | Git branch and status | ✓ |
| `model` | Claude model name (display_name from hook) | ✓ |
| `perf-cache-rate` | Cache hit percentage (⚡85%) | |
| `perf-response-time` | Average response time (⏱1.5s) | |
| `perf-session-time` | Session duration (🕐45m) | |
| `perf-token-rate` | Token generation rate (⚙94 t/s) | |
| `perf-message-count` | Number of messages (💬12) | |
| `perf-all-metrics` | All performance metrics | |
| `input` | Input tokens as tuple: (base, cache_write, cache_read) | |
| `output` | Output token count | |
| `context` | Context size (input + cache_write + output) | ✓ |
| `cost` | Session cost in USD | ✓ |

## Examples

### Default Configuration
```bash
# Shows: badge, folder, git, model, context, cost
python3 ~/.claude/pyccsl.py

# Output: ●○○○ my-project > main ● > Sonnet 3.5 > ⧉ 16.5K > 48¢
```

### Token Display
```bash
# Show model with detailed token breakdown
python3 ~/.claude/pyccsl.py model,input,output,context

# Output: Sonnet 3.5 > ↑ (53,54.8K,251.0K) > ↓ 2.6K > ⧉ 57.5K
# Input shows: (base, cache_write, cache_read)
# Context shows: base + cache_write + output
```

### Performance Monitoring
```bash
# Show all performance metrics
python3 ~/.claude/pyccsl.py badge,model,perf_all_metrics,cost

# Output: ○○●○ Sonnet 3.5 │ ⚡85% ⏱2.5s 🕐45m ⚙94t/s 💬12 > 48¢
```

### Custom Theme and Format
```bash
# Nord theme with full numbers
python3 ~/.claude/pyccsl.py --theme nord --numbers full

# Output: ●○○○ my-project > main ● > Sonnet 3.5 > ↑ 1,234 > ↓ 15,234 > 48¢
```

### No Emoji
```bash
# For terminals without emoji support
python3 ~/.claude/pyccsl.py --no-emoji badge,model,perf_cache_rate,cost

# Output: ●○○○ Sonnet 3.5 | Cache: 85% > 48¢
```

### Custom Performance Thresholds
```bash
# Adjust thresholds based on your typical performance
python3 ~/.claude/pyccsl.py --perf-cache 70,50,30 --perf-response 2,4,6

# Output: ○●○○ my-project > main ● > Sonnet 3.5 > ↑ 1.2K > ↓ 15.3K > 48¢
```

## Claude Code Settings Examples

### Basic Configuration
```json
{
  "statusLine": {
    "type": "command",
    "command": "python3 ~/.claude/pyccsl.py"
  }
}
```

### Show Performance Metrics
```json
{
  "statusLine": {
    "type": "command",
    "command": "python3 ~/.claude/pyccsl.py badge,folder,git,model,perf_all_metrics,input,output,cost"
  }
}
```

### Custom Theme
```json
{
  "statusLine": {
    "type": "command",
    "command": "python3 ~/.claude/pyccsl.py --theme nord --style powerline"
  }
}
```

### Minimal Status Line
```json
{
  "statusLine": {
    "type": "command",
    "command": "python3 ~/.claude/pyccsl.py --theme none --style pipes model,input,output"
  }
}
```

### Custom Thresholds
```json
{
  "statusLine": {
    "type": "command",
    "command": "python3 ~/.claude/pyccsl.py --perf-cache 70,50,30 --perf-response 2,4,6"
  }
}
```

## Performance Badge Interpretation

The performance badge (●○○○) provides a quick visual indicator of session performance:

- **●○○○** (Green) - Excellent performance: High cache usage, fast responses
- **○●○○** (Yellow) - Good performance: Moderate cache usage, acceptable response times
- **○○●○** (Orange) - Fair performance: Low cache usage, slower responses
- **○○○●** (Red) - Poor performance: Minimal cache usage, slow responses

The badge is calculated based on:
1. **Cache hit rate**: Higher percentages mean more token reuse (cost savings)
2. **Response time**: Lower times mean faster interactions

## Input Format

The script expects JSON input via stdin from Claude Code:

```json
{
  "hook_event_name": "Status",
  "session_id": "abc123...",
  "transcript_path": "/path/to/transcript.json",
  "cwd": "/current/working/directory",
  "model": {
    "id": "claude-opus-4-1",
    "display_name": "Opus"
  },
  "workspace": {
    "current_dir": "/current/working/directory",
    "project_dir": "/original/project/directory"
  }
}
```

Where:
- `model`: The Claude model identifier (required)
- `transcript_path`: Path to the Claude Code transcript file (optional)

If no transcript path is provided, performance metrics and cost cannot be calculated.

## Environment Variables

As an alternative to command line options, you can set defaults using environment variables:

- `PYCCSL_THEME` - Default theme
- `PYCCSL_NUMBERS` - Default number format
- `PYCCSL_STYLE` - Default separator style
- `PYCCSL_NO_EMOJI` - Disable emoji (set to "true")
- `PYCCSL_PERF_CACHE` - Default cache thresholds (e.g., "70,50,30")
- `PYCCSL_PERF_RESPONSE` - Default response thresholds (e.g., "2,4,6")
- `PYCCSL_FIELDS` - Default fields to display (e.g., "badge,model,cost")

Command line options override environment variables.

## Exit Codes

- `0` - Success
- `1` - Invalid command line arguments
- `2` - Invalid input JSON
- `3` - Transcript file not found or unreadable
- `4` - Calculation error

## Notes

- The script embeds pricing data from https://docs.anthropic.com/en/docs/about-claude/pricing
- All cost calculations assume 5-minute cache TTL (the default for Claude Code)
- Tool use tokens are already included in the reported usage metrics
- Performance metrics are calculated from the entire transcript, not just recent messages
- Git information requires the script to be run in a git repository
- The script is standalone with no external dependencies