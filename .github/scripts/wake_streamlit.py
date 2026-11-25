"""Open each Streamlit Community Cloud demo in a headless browser.

A plain HTTP request doesn't count as a visit, so a real browser loads the page.
If the app is asleep, it clicks the "Yes, get this app back up!" button.
"""
import sys

from playwright.sync_api import sync_playwright

APPS = [
    "https://cloud-metrics-anomaly.streamlit.app/",
    "https://arxiv-ml-research.streamlit.app/",
    "https://boston-bluebikes-demand.streamlit.app/",
]

failures = 0
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    for url in APPS:
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=60_000)
            button = page.locator("button", has_text="get this app back up")
            try:
                # the sleep page renders after a few seconds of JavaScript
                button.first.wait_for(state="visible", timeout=15_000)
            except Exception:
                pass
            if button.count() > 0:
                button.first.click()
                page.wait_for_timeout(60_000)  # give the app time to boot
                print(f"WOKE  {url}")
            else:
                page.wait_for_timeout(15_000)  # stay long enough to register a visit
                print(f"AWAKE {url}")
        except Exception as exc:  # keep going so one failure doesn't skip the others
            failures += 1
            print(f"ERROR {url}: {exc}")
    browser.close()

sys.exit(1 if failures else 0)
