"""Data types for shodh scan results."""

from dataclasses import dataclass, field


@dataclass
class CrawlResult:
    """Result of crawling a single URL."""

    url: str
    status_code: int
    error: str | None = None

    @property
    def is_broken(self) -> bool:
        """Check if this URL returned a 404 status."""
        return self.status_code == 404

    @property
    def is_error(self) -> bool:
        """Check if this URL resulted in an error."""
        return self.error is not None


@dataclass
class ScanReport:
    """Complete report from a site scan."""

    base_url: str
    results: list[CrawlResult] = field(default_factory=list)

    @property
    def total_scanned(self) -> int:
        """Total number of URLs scanned."""
        return len(self.results)

    @property
    def broken_links(self) -> list[CrawlResult]:
        """List of URLs that returned 404."""
        return [r for r in self.results if r.is_broken]

    @property
    def errors(self) -> list[CrawlResult]:
        """List of URLs that resulted in errors."""
        return [r for r in self.results if r.is_error]

    @property
    def successful(self) -> list[CrawlResult]:
        """List of successfully crawled URLs."""
        return [r for r in self.results if not r.is_broken and not r.is_error]
