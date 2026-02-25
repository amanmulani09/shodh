# Grawl

A fast, simple CLI tool and library to detect 404 pages on your website.

Built for developers who want quick broken-link checks without heavy dependencies.

## Features

- Fast crawling powered by selectolax
- Detects 404 pages and reports broken links
- Skips URL fragments (#section)
- Exports results to CSV
- Simple CLI and programmatic API
- Type hints throughout

## Installation

```bash
pip install grawl
```

## CLI Usage

```bash
# Basic scan
grawl https://example.com

# Custom output file
grawl https://example.com -o report.csv

# Custom timeout (seconds)
grawl https://example.com --timeout 10

# Quiet mode (minimal output)
grawl https://example.com -q

# Show help
grawl --help
```

## Programmatic API

```python
import grawl

# Basic scan
report = grawl.scan("https://example.com")

print(f"Scanned {report.total_scanned} pages")
print(f"Found {len(report.broken_links)} broken links")

# Access results
for result in report.broken_links:
    print(f"404: {result.url}")

# With options
report = grawl.scan(
    "https://example.com",
    timeout=10,
    quiet=True,
)

# Export to CSV
grawl.export_csv(report, "broken_links.csv")

# Callback for real-time results
def on_result(result):
    if result.is_broken:
        print(f"Found broken link: {result.url}")

report = grawl.scan("https://example.com", on_result=on_result)
```

## Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Lint
ruff check src tests

# Type check
mypy src
```

## License

MIT
