"""Pytest fixtures for grawl tests."""

import pytest
import responses


@pytest.fixture
def mock_responses():
    """Activate responses mock for HTTP requests."""
    with responses.RequestsMock() as rsps:
        yield rsps


@pytest.fixture
def simple_html_page():
    """Simple HTML page with links."""
    return """
    <!DOCTYPE html>
    <html>
    <head><title>Test Page</title></head>
    <body>
        <a href="/page1">Page 1</a>
        <a href="/page2">Page 2</a>
        <a href="https://external.com">External</a>
    </body>
    </html>
    """


@pytest.fixture
def html_with_fragment():
    """HTML page with fragment links."""
    return """
    <!DOCTYPE html>
    <html>
    <body>
        <a href="/page#section1">Section 1</a>
        <a href="#section2">Section 2</a>
    </body>
    </html>
    """
