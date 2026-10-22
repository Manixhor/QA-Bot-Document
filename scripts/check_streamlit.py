"""Wake the public demo, then verify the real UI without uploading or calling AI."""
from pathlib import Path
from playwright.sync_api import sync_playwright

URL = "https://app-bot-document-f4vzh3ghty7n23j6gmzbse.streamlit.app/"


def main():
    output = Path("artifacts")
    output.mkdir(exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 1000})
        page.set_default_timeout(15_000)
        try:
            page.goto(URL, wait_until="domcontentloaded", timeout=90_000)
            # Streamlit Community Cloud may wrap the application in an iframe.
            for _ in range(60):
                for frame in page.frames:
                    wake = frame.get_by_role("button", name="Yes, get this app back up!", exact=True)
                    if wake.count() and wake.first.is_visible():
                        wake.first.click()
                    ready = frame.get_by_role("button", name="Process documents", exact=True)
                    if ready.count() and ready.first.is_visible():
                        print("QA Bot interface loaded successfully.")
                        return
                page.wait_for_timeout(5_000)
            raise RuntimeError("QA Bot did not display its document-processing interface within five minutes.")
        finally:
            page.screenshot(path=str(output / "qa-bot-status.png"), full_page=True)
            browser.close()


if __name__ == "__main__":
    main()
