"""Tests for the crawler module."""

import pytest
import responses

from grawl import Crawler, InvalidURLError, scan
from grawl.types import CrawlResult, ScanReport


class TestCrawler:
    """Tests for the Crawler class."""

    def test_validate_url_adds_https(self):
        """URL without scheme gets https added."""
        crawler = Crawler("example.com", quiet=True)
        assert crawler.base_url == "https://example.com"

    def test_validate_url_preserves_http(self):
        """HTTP URLs are preserved."""
        crawler = Crawler("http://example.com", quiet=True)
        assert crawler.base_url == "http://example.com"

    def test_validate_url_invalid_scheme(self):
        """Invalid schemes raise InvalidURLError."""
        with pytest.raises(InvalidURLError, match="http or https"):
            Crawler("ftp://example.com", quiet=True)

    def test_validate_url_missing_domain(self):
        """URLs without domain raise InvalidURLError."""
        with pytest.raises(InvalidURLError, match="Missing domain"):
            Crawler("https://", quiet=True)

    @responses.activate
    def test_scan_single_page(self, simple_html_page):
        """Scanning a single page with no links works."""
        responses.add(
            responses.GET,
            "https://example.com",
            body="<html></html>",
            status=200,
            content_type="text/html",
        )

        report = scan("https://example.com", quiet=True)

        assert report.total_scanned == 1
        assert len(report.broken_links) == 0
        assert report.results[0].status_code == 200

    @responses.activate
    def test_scan_detects_404(self):
        """404 pages are detected as broken links."""
        responses.add(
            responses.GET,
            "https://example.com",
            body="Not Found",
            status=404,
        )

        report = scan("https://example.com", quiet=True)

        assert len(report.broken_links) == 1
        assert report.broken_links[0].url == "https://example.com"
        assert report.broken_links[0].is_broken

    @responses.activate
    def test_scan_follows_internal_links(self, simple_html_page):
        """Crawler follows internal links."""
        responses.add(
            responses.GET,
            "https://example.com",
            body=simple_html_page,
            status=200,
            content_type="text/html",
        )
        responses.add(
            responses.GET,
            "https://example.com/page1",
            body="<html></html>",
            status=200,
            content_type="text/html",
        )
        responses.add(
            responses.GET,
            "https://example.com/page2",
            body="<html></html>",
            status=200,
            content_type="text/html",
        )

        report = scan("https://example.com", quiet=True)

        assert report.total_scanned == 3
        visited_urls = {r.url for r in report.results}
        assert "https://example.com" in visited_urls
        assert "https://example.com/page1" in visited_urls
        assert "https://example.com/page2" in visited_urls

    @responses.activate
    def test_scan_ignores_external_links(self, simple_html_page):
        """External links are not followed."""
        responses.add(
            responses.GET,
            "https://example.com",
            body=simple_html_page,
            status=200,
            content_type="text/html",
        )
        responses.add(
            responses.GET,
            "https://example.com/page1",
            body="<html></html>",
            status=200,
            content_type="text/html",
        )
        responses.add(
            responses.GET,
            "https://example.com/page2",
            body="<html></html>",
            status=200,
            content_type="text/html",
        )

        report = scan("https://example.com", quiet=True)

        visited_urls = {r.url for r in report.results}
        assert "https://external.com" not in visited_urls

    @responses.activate
    def test_scan_strips_fragments(self, html_with_fragment):
        """URL fragments are stripped from links."""
        responses.add(
            responses.GET,
            "https://example.com",
            body=html_with_fragment,
            status=200,
            content_type="text/html",
        )
        responses.add(
            responses.GET,
            "https://example.com/page",
            body="<html></html>",
            status=200,
            content_type="text/html",
        )

        report = scan("https://example.com", quiet=True)

        visited_urls = {r.url for r in report.results}
        # /page#section1 should become /page
        assert "https://example.com/page" in visited_urls
        assert not any("#" in url for url in visited_urls)

    @responses.activate
    def test_scan_handles_errors(self):
        """Connection errors are captured in results."""
        responses.add(
            responses.GET,
            "https://example.com",
            body=Exception("Connection failed"),
        )

        report = scan("https://example.com", quiet=True)

        assert report.total_scanned == 1
        assert report.results[0].is_error
        assert "Connection failed" in report.results[0].error

    @responses.activate
    def test_on_result_callback(self):
        """Callback is called for each result."""
        responses.add(
            responses.GET,
            "https://example.com",
            body="<html></html>",
            status=200,
            content_type="text/html",
        )

        results = []
        scan("https://example.com", quiet=True, on_result=results.append)

        assert len(results) == 1
        assert isinstance(results[0], CrawlResult)


class TestCrawlResult:
    """Tests for CrawlResult dataclass."""

    def test_is_broken_true_for_404(self):
        """is_broken is True for 404 status."""
        result = CrawlResult(url="https://example.com", status_code=404)
        assert result.is_broken

    def test_is_broken_false_for_200(self):
        """is_broken is False for 200 status."""
        result = CrawlResult(url="https://example.com", status_code=200)
        assert not result.is_broken

    def test_is_error_true_when_error_set(self):
        """is_error is True when error is set."""
        result = CrawlResult(url="https://example.com", status_code=0, error="Timeout")
        assert result.is_error

    def test_is_error_false_when_no_error(self):
        """is_error is False when error is None."""
        result = CrawlResult(url="https://example.com", status_code=200)
        assert not result.is_error


class TestScanReport:
    """Tests for ScanReport dataclass."""

    def test_broken_links_filters_404(self):
        """broken_links returns only 404 results."""
        report = ScanReport(
            base_url="https://example.com",
            results=[
                CrawlResult(url="https://example.com", status_code=200),
                CrawlResult(url="https://example.com/broken", status_code=404),
                CrawlResult(url="https://example.com/also-broken", status_code=404),
            ],
        )
        assert len(report.broken_links) == 2

    def test_errors_filters_error_results(self):
        """errors returns only results with errors."""
        report = ScanReport(
            base_url="https://example.com",
            results=[
                CrawlResult(url="https://example.com", status_code=200),
                CrawlResult(url="https://example.com/error", status_code=0, error="Timeout"),
            ],
        )
        assert len(report.errors) == 1

    def test_successful_filters_good_results(self):
        """successful returns only non-broken, non-error results."""
        report = ScanReport(
            base_url="https://example.com",
            results=[
                CrawlResult(url="https://example.com", status_code=200),
                CrawlResult(url="https://example.com/broken", status_code=404),
                CrawlResult(url="https://example.com/error", status_code=0, error="Timeout"),
            ],
        )
        assert len(report.successful) == 1
