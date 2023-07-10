#!/usr/bin/env python3

import argparse
import sys
from http import HTTPStatus

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

DEFAULT_TIMEOUT = 15


def main(args):
    if not args.urls:
        return

    error_count = 0

    def print_error(url, message):
        nonlocal error_count

        if message.type != "error":
            return

        error_count += 1
        print(f"URL: {url} - ERROR: {message}", file=sys.stderr)

    def handle_exception(exc):
        nonlocal error_count

        error_count += 1
        print(f"URL: {url} = EXCEPTION: {exc}", file=sys.stderr)

    with sync_playwright() as p:
        browser = getattr(p, args.browser).launch(headless=not args.headed)

        for url in args.urls:
            context = browser.new_context(
                accept_downloads=False, service_workers="block"
            )
            context.set_default_navigation_timeout(args.timeout * 1_000)

            page = context.new_page()
            page.on("console", lambda msg: print_error(url=url, message=msg))
            # Log all uncaught errors to the terminal
            page.on("pageerror", handle_exception)

            response = None
            try:
                response = page.goto(url, wait_until=args.wait_until)
            except PlaywrightTimeoutError:
                error_count += 1
                print(f"Page: {url} timed out", file=sys.stderr)
                continue

            if response.status != HTTPStatus.OK:
                error_count += 1
                print(
                    f"GET {url} returned status code: {response.status}",
                    file=sys.stderr,
                )
                continue

            context.close()

        browser.close()

    return error_count


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-u",
        "--urls",
        nargs="+",
        default=[],
        help="list of URLs to hit (must be used at least once)",
    )
    parser.add_argument(
        "-b",
        "--browser",
        choices=[
            "chromium",
            "chrome",
            "chrome-beta",
            "msedge",
            "msedge-beta",
            "msedge-dev",
            "firefox",
            "webkit",
        ],
        default="firefox",
        help="web browser to use",
    )
    parser.add_argument(
        "-H",
        "--headed",
        help="run in `headed` mode (a.k.a not headless)",
        default=False,
        action="store_true",
    )
    parser.add_argument(
        "-t",
        "--timeout",
        help=f"how long to wait for (defaults to {DEFAULT_TIMEOUT}s)",
        type=float,
        default=DEFAULT_TIMEOUT,
    )
    parser.add_argument(
        "-w",
        "--wait-until",
        choices=["domcontentloaded", "load", "commit"],
        help="how long to wait for (defaults to 30s)",
        default="load",
    )
    args = parser.parse_args()

    if (error_count := main(args)) > 0:
        sys.exit(1)
