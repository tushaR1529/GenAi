# app/fetch.py
from pathlib import Path
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

RAW_DIR = Path("data/raw")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/pdf,application/xhtml+xml,*/*",
    "Accept-Language": "en-US,en;q=0.9",
}

# filename -> list of working government URLs to try in order
SOURCES = {
    "pm_vidyalaxmi_guidelines.pdf": [
        "https://static.pib.gov.in/WriteReadData/specificdocs/documents/2026/jul/doc2026729936401.pdf",
        "https://pmvidyalaxmi.co.in/img/UserManual-Student.pdf",
    ],
    "pm_vidyalaxmi_faq.html": [
        "https://pmvidyalaxmi.co.in/PublicFaq.aspx",
    ],
    "csis_guidelines.pdf": [
        "https://www.canarabank.bank.in/documents/d/guest/csis-guideline-01-04-2022",
        "https://www.education.gov.in/sites/upload_files/mhrd/files/upload_document/CSIS%20-%20NewGuidelines.pdf",
    ],
}


def download(url: str) -> bytes:
    """Download content from a URL with timeout and SSL verification fallback."""
    for verify in (True, False):
        try:
            response = requests.get(url, timeout=30, headers=HEADERS, verify=verify)
            response.raise_for_status()
            content = response.content
            # Ensure valid non-empty response
            if len(content) > 500:
                return content
        except requests.exceptions.SSLError:
            continue
        except requests.exceptions.RequestException:
            continue
    raise requests.exceptions.RequestException(f"Failed to download {url}")


def fetch_all() -> None:
    """Fetch all official government documents and store in data/raw."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Fetching official documents into {RAW_DIR}...")
    for filename, urls in SOURCES.items():
        saved = False
        target_path = RAW_DIR / filename
        for url in urls:
            try:
                print(f"Downloading {filename} from {url}...")
                content = download(url)
                target_path.write_bytes(content)
                print(f"  -> Saved {filename} ({len(content)} bytes)")
                saved = True
                break
            except Exception as e:
                print(f"  -> Failed {url}: {e}")
        if not saved:
            print(f"WARNING: Could not fetch {filename}. Check source URLs.")


if __name__ == "__main__":
    fetch_all()
