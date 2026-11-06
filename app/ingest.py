# app/ingest.py
import json
import re
from dataclasses import asdict
from pathlib import Path

from bs4 import BeautifulSoup
from pypdf import PdfReader

from app.models import Record

RAW_DIR = Path("data/raw")
OUT_FILE = Path("data/records.json")

SOURCES = {
    "pm_vidyalaxmi_guidelines.pdf": ("PM-Vidyalaxmi", "https://www.education.gov.in/sites/upload_files/mhrd/files/document-reports/PM_Vidyalaxmi_Scheme_Guidelines.pdf"),
    "csis_guidelines.pdf": ("PM-USP CSIS", "https://www.education.gov.in/sites/upload_files/mhrd/files/upload_document/CSIS%20-%20NewGuidelines.pdf"),
    "pm_vidyalaxmi_faq.html": ("PM-Vidyalaxmi FAQ", "https://pmvidyalaxmi.co.in/PublicFaq.aspx"),
}

KEYWORDS = ("loan", "interest", "subvention", "guarantee", "moratorium", "income", "collateral")


def clean(text):
    return re.sub(r"\s+", " ", text).strip()


def find_amount(text, pattern):
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(0) if match else None


def paragraphs_from_pdf(path):
    for page in PdfReader(path).pages:
        text = page.extract_text() or ""
        for block in re.split(r"\n\s*\n|\n(?=\d+\.\s)", text):
            yield clean(block)


def paragraphs_from_html(path):
    soup = BeautifulSoup(path.read_text(errors="ignore"), "html.parser")
    for tag in soup(["script", "style"]):
        tag.decompose()
    for block in soup.get_text("\n").split("\n"):
        yield clean(block)


def main():
    records = []
    skipped = 0
    for filename, (scheme, url) in SOURCES.items():
        path = RAW_DIR / filename
        if not path.exists():
            print("Missing file:", filename)
            continue
        paras = paragraphs_from_pdf(path) if filename.endswith(".pdf") else paragraphs_from_html(path)
        for para in paras:
            try:
                if len(para) < 60 or not any(k in para.lower() for k in KEYWORDS):
                    continue
                records.append(Record(
                    id=len(records) + 1,
                    scheme_name=scheme,
                    who_is_eligible="",
                    income_limit=find_amount(para, r"(Rs\.?|₹)\s?[\d.,]+\s?lakh(?=[^.]*income)|income[^.]{0,40}(Rs\.?|₹)\s?[\d.,]+\s?lakh"),
                    loan_limit=find_amount(para, r"(Rs\.?|₹)\s?[\d.,]+\s?lakh"),
                    benefit=para[:600],
                    source_url=url,
                ))
            except Exception as e:
                skipped += 1
                print("Bad row skipped:", e)
    OUT_FILE.write_text(json.dumps([asdict(r) for r in records], indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Saved {len(records)} records, skipped {skipped}")


if __name__ == "__main__":
    main()