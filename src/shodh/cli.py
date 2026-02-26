"""Command-line interface for shodh."""

import sys

import click
from colorama import Fore

from .crawler import Crawler, export_csv
from .exceptions import ShodhError


@click.command()
@click.argument("url")
@click.option(
    "-o",
    "--output",
    default="404_report.csv",
    help="Output CSV filename.",
    show_default=True,
)
@click.option(
    "-t",
    "--timeout",
    default=5,
    type=int,
    help="Request timeout in seconds.",
    show_default=True,
)
@click.option(
    "-q",
    "--quiet",
    is_flag=True,
    help="Suppress output except errors and summary.",
)
@click.version_option(package_name="shodh")
def main(url: str, output: str, timeout: int, quiet: bool) -> None:
    """Scan a website for broken (404) links.

    URL is the starting page to crawl, e.g., https://example.com
    """
    try:
        crawler = Crawler(url, timeout=timeout, quiet=quiet)
        report = crawler.scan()

        # Print summary
        if not quiet:
            print(Fore.MAGENTA + "\n========= SCAN SUMMARY =========")
        print(Fore.CYAN + f"Total Pages Scanned: {report.total_scanned}")
        print(Fore.RED + f"Total 404 Found: {len(report.broken_links)}")

        # Export CSV
        export_csv(report, output)
        print(Fore.GREEN + f"\nReport exported: {output}")

    except ShodhError as e:
        click.echo(Fore.RED + f"Error: {e}", err=True)
        sys.exit(1)
    except KeyboardInterrupt:
        click.echo("\nScan cancelled.", err=True)
        sys.exit(130)


if __name__ == "__main__":
    main()
