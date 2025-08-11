# 🎯 pyccsl - Python Claude Code Status Line

<div align="center">

[![Python](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.4.17-orange)](https://github.com/wolfdenpublishing/pyccsl/releases)
[![Dependencies](https://img.shields.io/badge/dependencies-zero-brightgreen)](pyccsl.py)
[![Lines](https://img.shields.io/badge/lines-~1000-lightgrey)](pyccsl.py)

**PYCCSL (Pronounced "Pixel") - An information-rich status line for Claude Code.**

![Hero Screenshot](images/hero-default.png)

*Real-time metrics • Cost tracking • Git status • Token usage • 9 themes • Zero dependencies*

📖 **[User Guide](pyccsl.md)** | 🔗 **[GitHub](https://github.com/wolfdenpublishing/pyccsl)** | 📝 **[Issues](https://github.com/wolfdenpublishing/pyccsl/issues)**

</div>

---

## Features

<table>
<tr>
<td width="50%">

### Implementation
- Single Python file (~1000 lines)
- No external dependencies
- Python 3.8+ standard library only
- Embedded Anthropic pricing data

### Performance Metrics
- Cache hit rate tracking
- Response time analysis
- Token generation speed
- Session duration monitoring

</td>
<td width="50%">

### Customization
- 9 color themes
- 5 separator styles  
- Optional emoji display
- Configurable field selection

### Token & Cost Analysis
- Input token breakdown (base, cache_write, cache_read)
- Output token counting
- Real-time cost calculation
- Context size tracking

</td>
</tr>
</table>

---

## Available Themes

<div align="center">
<table>
<tr>
<td align="center">
<img src="images/theme-nord.png" width="280" alt="Nord Theme"><br>
<b>Nord</b>
</td>
<td align="center">
<img src="images/theme-dracula.png" width="280" alt="Dracula Theme"><br>
<b>Dracula</b>
</td>
<td align="center">
<img src="images/theme-tokyo.png" width="280" alt="Tokyo Night"><br>
<b>Tokyo Night</b>
</td>
</tr>
<tr>
<td align="center">
<img src="images/theme-catppuccin.png" width="280" alt="Catppuccin"><br>
<b>Catppuccin</b>
</td>
<td align="center">
<img src="images/theme-solarized.png" width="280" alt="Solarized"><br>
<b>Solarized</b>
</td>
<td align="center">
<img src="images/theme-gruvbox.png" width="280" alt="Gruvbox"><br>
<b>Gruvbox</b>
</td>
</tr>
</table>
</div>

---

## Display Options

### Performance Metrics Display
All performance metrics in a single view:

![Performance Metrics](images/feature-performance.png)

Shows cache hit rate, response time, session duration, token generation speed, and message count.

### Token Usage Breakdown
Detailed token analysis with tuple format:

![Token Analysis](images/feature-tokens.png)

Input tokens displayed as (base, cache_write, cache_read) for complete visibility into token usage.

### Separator Styles
Five different separator options:

![Powerline Style](images/style-powerline.png)

Available styles: powerline (requires compatible fonts), simple, arrows, pipes, dots.

### Performance Badge Indicators
Four-level performance indicator:

![Performance Badge Levels](images/badge-all-levels.png)

- ●○○○ = High cache usage, fast responses
- ○●○○ = Moderate cache, acceptable response times
- ○○●○ = Low cache usage, slower responses  
- ○○○● = Minimal cache usage, slow responses

---

## Installation

### Requirements
- Python 3.8 or higher
- Claude Code

### Setup

1. Download the script:
```bash
curl -O https://raw.githubusercontent.com/wolfdenpublishing/pyccsl/main/pyccsl.py
chmod +x pyccsl.py
```

2. Copy to Claude directory:
```bash
cp pyccsl.py ~/.claude/
```

3. Configure Claude Code by editing `~/.claude/settings.json`:
```json
{
  "statusLine": {
    "type": "command",
    "command": "python3 ~/.claude/pyccsl.py"
  }
}
```

---

## Usage Examples

### Theme Selection

```bash
# Nord theme
python3 pyccsl.py --theme nord

# Dracula theme
python3 pyccsl.py --theme dracula

# No colors
python3 pyccsl.py --theme none
```

### Field Selection

```bash
# Minimal: model and cost only
python3 pyccsl.py model,cost

# Performance metrics
python3 pyccsl.py badge,model,perf-all-metrics,cost

# Token details
python3 pyccsl.py model,input,output,context
```

### Separator Styles

```bash
# Powerline arrows (requires Powerline fonts)
python3 pyccsl.py --style powerline

# Arrow separators
python3 pyccsl.py --style arrows

# Dot separators
python3 pyccsl.py --style dots
```

---

## Configuration Examples

<details>
<summary><b>Performance Monitoring</b></summary>

```json
{
  "statusLine": {
    "type": "command",
    "command": "python3 ~/.claude/pyccsl.py badge,model,perf-all-metrics,cost --theme nord"
  }
}
```

Displays all performance metrics for session analysis and cache optimization.
</details>

<details>
<summary><b>Cost Tracking</b></summary>

```json
{
  "statusLine": {
    "type": "command",
    "command": "python3 ~/.claude/pyccsl.py model,input,output,cost --numbers full"
  }
}
```

Shows detailed token counts and costs with full number formatting.
</details>

<details>
<summary><b>Git Integration</b></summary>

```json
{
  "statusLine": {
    "type": "command",
    "command": "python3 ~/.claude/pyccsl.py folder,git,model,cost --style powerline"
  }
}
```

Includes git branch and status with powerline separators.
</details>

<details>
<summary><b>Minimal Display</b></summary>

```json
{
  "statusLine": {
    "type": "command",
    "command": "python3 ~/.claude/pyccsl.py model,cost --theme minimal --no-emoji"
  }
}
```

Shows only model and cost without colors or emoji.
</details>

---

## Field Reference

All fields display in canonical order regardless of specification:

| Field | Display | Description |
|-------|---------|-------------|
| `badge` | `●○○○` | Performance indicator (4 levels) |
| `folder` | `my-project` | Current directory name |
| `git` | `main ●` | Branch and modification status |
| `model` | `Opus` | Claude model name |
| `perf-cache-rate` | `⚡85%` | Cache hit percentage |
| `perf-response-time` | `⏱1.5s` | Average response time |
| `perf-session-time` | `🕐45m` | Session duration |
| `perf-token-rate` | `⚙94 t/s` | Token generation speed |
| `perf-message-count` | `💬12` | Number of messages |
| `perf-all-metrics` | All above | Combined metrics display |
| `input` | `↑ (53,54.8K,251K)` | Input tokens (base, cache_write, cache_read) |
| `output` | `↓ 2.6K` | Output token count |
| `context` | `⧉ 57.5K` | Total context size |
| `cost` | `48¢` or `$1.25` | Session cost |

---

## Configuration Options

### Command-Line Options

| Option | Values | Description |
|--------|--------|-------------|
| `--theme` | `default`, `solarized`, `nord`, `dracula`, `gruvbox`, `tokyo`, `catppuccin`, `minimal`, `none` | Color theme |
| `--numbers` | `compact`, `full`, `raw` | Number formatting |
| `--style` | `simple`, `powerline`, `arrows`, `pipes`, `dots` | Separator style |
| `--no-emoji` | - | Disable all emoji |
| `--perf-cache` | `GREEN,YELLOW,ORANGE` | Cache thresholds (%) |
| `--perf-response` | `GREEN,YELLOW,ORANGE` | Response thresholds (seconds) |

### Environment Variables

Set persistent defaults without command-line arguments:

```bash
export PYCCSL_THEME="nord"
export PYCCSL_NUMBERS="full"
export PYCCSL_STYLE="powerline"
export PYCCSL_NO_EMOJI="true"
export PYCCSL_FIELDS="badge,model,cost"
export PYCCSL_PERF_CACHE="70,50,30"
export PYCCSL_PERF_RESPONSE="2,4,6"
```

---

## Technical Details

### Architecture

- Single file implementation (~1000 lines)
- No external dependencies - uses only Python standard library
- Embedded Anthropic pricing data
- Handles missing transcript files and non-git directories gracefully

### Data Flow

1. Reads JSON from stdin (Claude Code hook)
2. Parses transcript file for metrics (if available)
3. Extracts git repository information
4. Calculates performance metrics and costs
5. Formats and outputs customized status line

### Performance Metrics

Performance badge calculation:
- Cache Hit Rate = `cache_read_tokens / total_input_tokens`
- Response Time = Average time between user message and assistant response

Thresholds configurable via `--perf-cache` and `--perf-response` options.

### Cost Calculation

Uses embedded Anthropic pricing data:

```
Cost = (input_tokens × input_rate + 
        cache_creation × cache_write_5m_rate + 
        cache_read × cache_read_rate + 
        output_tokens × output_rate) / 1,000,000
```

All cache writes assumed to use 5-minute TTL (Claude Code default).

### Exit Codes

- `0` - Success
- `1` - Invalid arguments
- `2` - Invalid JSON input
- `3` - Transcript file error
- `4` - Calculation error

---

## Development

### Project Structure

```
pyccsl/
├── pyccsl.py             # Main script (single file)
├── pyccsl.md             # User documentation
├── CLAUDE.md             # Development guidelines
├── README.md             # This file
├── screenshots.md        # Screenshot checklist
├── schema.json           # Transcript schema
├── test_transcript.jsonl # Test data
├── images/               # Screenshots
└── .sbsi/                # Development buildprints
    ├── P1-core-foundation.md
    ├── P2-transcript-analysis.md
    ├── P3-display-fields.md
    └── P4-styling-polish.md
```

### Development Methodology

The project uses RPIV (Research, Plan, Implement, Verify) methodology with SBSI (Step-By-Step Implementation) buildprints. Each development phase is documented in `.sbsi/` with verifiable tasks and developer signoff requirements.

### Testing

```bash
# Create test input
echo '{"model":{"id":"claude-3-5-sonnet-20241022","display_name":"Sonnet 3.5"},"transcript_path":"test_transcript.jsonl"}' > test_input.json

# Test various configurations
cat test_input.json | python3 pyccsl.py
cat test_input.json | python3 pyccsl.py --theme nord --style powerline
cat test_input.json | python3 pyccsl.py badge,model,perf-all-metrics,cost
```

### Contributing

Guidelines for contributions:
1. Maintain single-file architecture
2. No external dependencies
3. Follow existing code style
4. Update relevant SBSI documents
5. Test with various Claude Code transcripts

---

## License

MIT License - See [LICENSE](LICENSE) file for details

---

## Acknowledgments

- Developed for [Claude Code](https://claude.ai/code) by Anthropic
- Pricing data from [Anthropic's documentation](https://docs.anthropic.com/en/docs/about-claude/pricing)
- Color themes inspired by popular terminal themes

---

## Version History

- **v0.4.17** - Complete emoji handling with --no-emoji flag
- **v0.4.16** - Powerline separators and complete theming
- **v0.3.0** - Full display fields implementation
- **v0.2.x** - Transcript analysis and cost calculations
- **v0.1.0** - Initial core foundation

---

## Links

- [Claude Code Documentation](https://docs.anthropic.com/en/docs/claude-code)
- [Issue Tracker](https://github.com/wolfdenpublishing/pyccsl/issues)
- [Releases](https://github.com/wolfdenpublishing/pyccsl/releases)

---

<div align="center">

**pyccsl** - *pronounced "pixel"*

Python Claude Code Status Line

</div>