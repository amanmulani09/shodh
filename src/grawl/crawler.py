"""Core crawling logic for grawl."""

import csv
import itertools
import sys
import threading
import time
from collections.abc import Callable
from urllib.parse import urljoin, urlparse

import requests
from colorama import Fore, Style, init
from selectolax.parser import HTMLParser

from .exceptions import InvalidURLError
from .types import CrawlResult, ScanReport

init(autoreset=True)


def _validate_url(url: str) -> str:
    """Validate and normalize a URL."""
    parsed = urlparse(url)
    if not parsed.scheme:
        url = f"https://{url}"
        parsed = urlparse(url)
    if not parsed.netloc:
        raise InvalidURLError(url, "Missing domain")
    if parsed.scheme not in ("http", "https"):
        raise InvalidURLError(url, "URL must use http or https")
    return url


class Crawler:
    """Website crawler for detecting broken links."""

    def __init__(
        self,
        base_url: str,
        timeout: int = 5,
        quiet: bool = False,
        on_result: Callable[[CrawlResult], None] | None = None,
    ):
        """
        Initialize the crawler.

        Args:
            base_url: The starting URL to crawl.
            timeout: Request timeout in seconds.
            quiet: Suppress output if True.
            on_result: Optional callback for each crawl result.
        """
        self.base_url = _validate_url(base_url)
        self.timeout = timeout
        self.quiet = quiet
        self.on_result = on_result

        self._visited: set[str] = set()
        self._to_visit: set[str] = set()
        self._results: list[CrawlResult] = []
        self._stop_spinner = False
        self._spinner_thread: threading.Thread | None = None

    def _print(self, message: str) -> None:
        """Print a message if not in quiet mode."""
        if not self.quiet:
            print(message)

    def _start_spinner(self) -> None:
        """Start the spinner animation."""
        if self.quiet:
            return

        def spinner() -> None:
            for c in itertools.cycle(["|", "/", "-", "\\"]):
                if self._stop_spinner:
                    break
                sys.stdout.write(Fore.CYAN + f"\rScanning... {c} ")
                sys.stdout.flush()
                time.sleep(0.1)
            sys.stdout.write("\rScan complete!      \n")

        self._spinner_thread = threading.Thread(target=spinner)
        self._spinner_thread.start()

    def _stop_spinner_thread(self) -> None:
        """Stop the spinner animation."""
        self._stop_spinner = True
        if self._spinner_thread:
            self._spinner_thread.join()

    def _extract_links(self, html: str, current_url: str) -> set[str]:
        """Extract all same-domain links from HTML content."""
        links: set[str] = set()
        tree = HTMLParser(html)
        base_netloc = urlparse(self.base_url).netloc

        for node in tree.css("a"):
            href = node.attributes.get("href")
            if not href:
                continue

            full_url = urljoin(current_url, href).split("#")[0]
            parsed = urlparse(full_url)

            if parsed.netloc == base_netloc:
                links.add(full_url)

        return links

    def _crawl_url(self, url: str) -> CrawlResult:
        """Crawl a single URL and return the result."""
        try:
            response = requests.get(url, timeout=self.timeout)
            result = CrawlResult(url=url, status_code=response.status_code)

            if response.status_code == 404:
                self._print(Fore.RED + f"\n[404 DETECTED] {url}")
            else:
                self._print(Fore.GREEN + f"\n[OK {response.status_code}] {url}")

                if "text/html" in response.headers.get("Content-Type", ""):
                    new_links = self._extract_links(response.text, url)
                    self._to_visit.update(new_links - self._visited)

            return result

        except Exception as e:
            self._print(Fore.YELLOW + f"\n[ERROR] {url} -> {e}")
            return CrawlResult(url=url, status_code=0, error=str(e))

    def scan(self) -> ScanReport:
        """
        Perform the full site scan.

        Returns:
            ScanReport containing all crawl results.
        """
        self._visited.clear()
        self._to_visit = {self.base_url}
        self._results.clear()
        self._stop_spinner = False

        self._print(
            Fore.GREEN
            + """
==========================================
      GRAWL - Broken Link Scanner
      selectolax Engine Activated...
==========================================
"""
            + Style.RESET_ALL
        )

        self._start_spinner()

        try:
            while self._to_visit:
                url = self._to_visit.pop()

                if url in self._visited:
                    continue

                self._visited.add(url)
                result = self._crawl_url(url)
                self._results.append(result)

                if self.on_result:
                    self.on_result(result)

        finally:
            self._stop_spinner_thread()

        return ScanReport(base_url=self.base_url, results=self._results)


def scan(
    url: str,
    timeout: int = 5,
    quiet: bool = False,
    on_result: Callable[[CrawlResult], None] | None = None,
) -> ScanReport:
    """
    Scan a website for broken links.

    This is the main public API for programmatic use.

    Args:
        url: The URL to scan.
        timeout: Request timeout in seconds.
        quiet: Suppress output if True.
        on_result: Optional callback for each crawl result.

    Returns:
        ScanReport containing all crawl results.

    Example:
        >>> report = grawl.scan("https://example.com")
        >>> print(f"Found {len(report.broken_links)} broken links")
    """
    crawler = Crawler(url, timeout=timeout, quiet=quiet, on_result=on_result)
    return crawler.scan()


def export_csv(report: ScanReport, filename: str) -> None:
    """
    Export broken links to a CSV file.

    Args:
        report: The scan report to export.
        filename: Output filename.
    """
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Broken URL"])

        for result in report.broken_links:
            writer.writerow([result.url])
