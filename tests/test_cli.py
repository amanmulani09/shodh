"""Tests for the CLI module."""

import os
import tempfile

import pytest
import responses
from click.testing import CliRunner

from grawl.cli import main


@pytest.fixture
def runner():
    """Create a CLI test runner."""
    return CliRunner()


class TestCLI:
    """Tests for the CLI."""

    def test_help_option(self, runner):
        """--help shows usage information."""
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "Scan a website for broken (404) links" in result.output

    def test_version_option(self, runner):
        """--version shows version."""
        result = runner.invoke(main, ["--version"])
        assert result.exit_code == 0
        assert "version" in result.output.lower()

    @responses.activate
    def test_basic_scan(self, runner):
        """Basic scan works with URL argument."""
        responses.add(
            responses.GET,
            "https://example.com",
            body="<html></html>",
            status=200,
            content_type="text/html",
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, "report.csv")
            result = runner.invoke(main, ["https://example.com", "-o", output_file, "-q"])

            assert result.exit_code == 0
            assert os.path.exists(output_file)

    @responses.activate
    def test_quiet_mode(self, runner):
        """Quiet mode suppresses banner output."""
        responses.add(
            responses.GET,
            "https://example.com",
            body="<html></html>",
            status=200,
            content_type="text/html",
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, "report.csv")
            result = runner.invoke(main, ["https://example.com", "-o", output_file, "-q"])

            assert "GRAWL" not in result.output
            assert "Total Pages Scanned" in result.output

    @responses.activate
    def test_detects_broken_links(self, runner):
        """CLI reports broken links found."""
        responses.add(
            responses.GET,
            "https://example.com",
            body="Not Found",
            status=404,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, "report.csv")
            result = runner.invoke(main, ["https://example.com", "-o", output_file, "-q"])

            assert result.exit_code == 0
            assert "Total 404 Found: 1" in result.output

    def test_invalid_url_error(self, runner):
        """Invalid URL shows error message."""
        result = runner.invoke(main, ["not-a-valid-url://test"])
        assert result.exit_code == 1
        assert "Error" in result.output

    @responses.activate
    def test_custom_timeout(self, runner):
        """Custom timeout is accepted."""
        responses.add(
            responses.GET,
            "https://example.com",
            body="<html></html>",
            status=200,
            content_type="text/html",
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, "report.csv")
            result = runner.invoke(
                main,
                ["https://example.com", "-o", output_file, "-q", "--timeout", "10"],
            )

            assert result.exit_code == 0

    @responses.activate
    def test_csv_output_contains_broken_links(self, runner):
        """CSV output contains broken links."""
        responses.add(
            responses.GET,
            "https://example.com",
            body='<html><a href="/broken">link</a></html>',
            status=200,
            content_type="text/html",
        )
        responses.add(
            responses.GET,
            "https://example.com/broken",
            body="Not Found",
            status=404,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, "report.csv")
            result = runner.invoke(main, ["https://example.com", "-o", output_file, "-q"])

            assert result.exit_code == 0

            with open(output_file) as f:
                content = f.read()
                assert "Broken URL" in content
                assert "https://example.com/broken" in content
