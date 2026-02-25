"""Custom exceptions for grawl."""


class GrawlError(Exception):
    """Base exception for all grawl errors."""

    pass


class InvalidURLError(GrawlError):
    """Raised when an invalid URL is provided."""

    def __init__(self, url: str, reason: str = "Invalid URL format"):
        self.url = url
        self.reason = reason
        super().__init__(f"{reason}: {url}")


class CrawlError(GrawlError):
    """Raised when a crawl operation fails."""

    def __init__(self, url: str, cause: Exception | None = None):
        self.url = url
        self.cause = cause
        message = f"Failed to crawl {url}"
        if cause:
            message += f": {cause}"
        super().__init__(message)
