# Shodh

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
pip install shodh
```

## CLI Usage

```bash
# Basic scan
shodh https://example.com

# Custom output file
shodh https://example.com -o report.csv

# Custom timeout (seconds)
shodh https://example.com --timeout 10

# Quiet mode (minimal output)
shodh https://example.com -q

# Show help
shodh --help
```

## Programmatic API

```python
import shodh

# Basic scan
report = shodh.scan("https://example.com")

print(f"Scanned {report.total_scanned} pages")
print(f"Found {len(report.broken_links)} broken links")

# Access results
for result in report.broken_links:
    print(f"404: {result.url}")

# With options
report = shodh.scan(
    "https://example.com",
    timeout=10,
    quiet=True,
)

# Export to CSV
shodh.export_csv(report, "broken_links.csv")

# Callback for real-time results
def on_result(result):
    if result.is_broken:
        print(f"Found broken link: {result.url}")

report = shodh.scan("https://example.com", on_result=on_result)
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
