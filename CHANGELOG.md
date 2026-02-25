# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-02-25

### Added

- Initial release
- CLI with `grawl <url>` command
- Parameterized URL scanning (no more hardcoded URLs)
- Custom output file with `-o` / `--output`
- Configurable timeout with `-t` / `--timeout`
- Quiet mode with `-q` / `--quiet`
- Programmatic API: `grawl.scan(url)` for library usage
- Type hints throughout
- Unit tests with mocked HTTP
- CI/CD with GitHub Actions
