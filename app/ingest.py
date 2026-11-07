# app/ingest.py
import json
import re
import sys
from dataclasses import asdict
from pathlib import Path

# Ensure root directory is on sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from bs4 import BeautifulSoup
from pypdf import PdfReader

from app.models import Record

RAW_DIR = Path("data/raw")
OUT_FILE = Path("data/records.json")

SOURCES = {
    "pm_vidyalaxmi_guidelines.pdf": (
        "PM-Vidyalaxmi",
        "https://static.pib.gov.in/WriteReadData/specificdocs/documents/2026/jul/doc2026729936401.pdf",
        "scheme_feature",
    ),
    "csis_guidelines.pdf": (
        "PM-USP CSIS",
        "https://www.canarabank.bank.in/documents/d/guest/csis-guideline-01-04-2022",
        "cgfsel_csis_rule",
    ),
    "pm_vidyalaxmi_faq.html": (
        "PM-Vidyalaxmi FAQ",
        "https://pmvidyalaxmi.co.in/PublicFaq.aspx",
        "portal_faq",
    ),
}

KEYWORDS = (
    "loan", "interest", "subvention", "guarantee", "moratorium",
    "income", "collateral", "qhei", "eligib", "csis", "vidyalaxmi", "portal"
)


def clean(text: str) -> str:
    """Normalize whitespace and strip text."""
    return re.sub(r"\s+", " ", text).strip()


def find_income_limit(text: str):
    """Extract income limit mentioned in text if any."""
    m = re.search(
        r"(?:annual\s+)?(?:family\s+)?income\s*(?:up\s+to|ceiling\s+of|limit\s+of|of|not\s+exceeding)?\s*(?:Rs\.?|₹)?\s*[\d.,]+\s*lakh",
        text,
        re.IGNORECASE,
    )
    if m:
        return clean(m.group(0))
    m = re.search(r"(?:Rs\.?|₹)\s*[\d.,]+\s*lakh(?=[^.]*income)", text, re.IGNORECASE)
    if m:
        return clean(m.group(0))
    return None


def find_loan_limit(text: str):
    """Extract loan amount limit mentioned in text if any."""
    m = re.search(
        r"loan[s]?\s*(?:up\s+to|amount\s+of|of|limit\s+of)?\s*(?:Rs\.?|₹)?\s*[\d.,]+\s*lakh",
        text,
        re.IGNORECASE,
    )
    if m:
        return clean(m.group(0))
    m = re.search(
        r"(?:Rs\.?|₹)\s*[\d.,]+\s*lakh(?=[^.]*(?:loan|credit\s+guarantee|facility))",
        text,
        re.IGNORECASE,
    )
    if m:
        return clean(m.group(0))
    return None


def find_who_is_eligible(text: str, default_scheme: str) -> str:
    """Extract eligible target group from text or apply standard scheme criteria."""
    m = re.search(
        r"(?:eligib(?:le|ility)|admitted\s+to|open\s+to|applicable\s+(?:to|for))\s*[:\-]?\s*([^.;]{10,120})",
        text,
        re.IGNORECASE,
    )
    if m:
        return clean(m.group(1))
    if default_scheme == "PM-Vidyalaxmi":
        return "Students admitted on merit to eligible Quality Higher Education Institutions (QHEIs) in India"
    elif default_scheme == "PM-USP CSIS":
        return "Students from Economically Weaker Sections with annual gross parental income up to Rs. 4.5 lakh"
    elif default_scheme == "PM-Vidyalaxmi FAQ":
        return "Students applying for education loans / interest subvention on the PM-Vidyalaxmi portal"
    return "Eligible students meeting scheme criteria"


def paragraphs_from_pdf(path: Path):
    """Extract text paragraphs from PDF file."""
    reader = PdfReader(path)
    for page in reader.pages:
        text = page.extract_text() or ""
        blocks = re.split(r"\n\s*\n|\n(?=\d+\.\s)", text)
        for block in blocks:
            c = clean(block)
            if len(c) >= 60 and any(k in c.lower() for k in KEYWORDS):
                yield c


def paragraphs_from_html(path: Path):
    """Extract FAQ items or text paragraphs from HTML file."""
    soup = BeautifulSoup(path.read_text(encoding="utf-8", errors="ignore"), "html.parser")
    # First priority: check for structured <details> FAQs
    details_list = soup.find_all("details")
    if details_list:
        for d in details_list:
            summary = d.find("summary")
            q = clean(summary.get_text()) if summary else ""
            if summary:
                summary.decompose()
            a = clean(d.get_text())
            if q and a:
                yield f"Q: {q} A: {a}"
    else:
        for tag in soup(["script", "style"]):
            tag.decompose()
        for block in soup.get_text("\n").split("\n"):
            c = clean(block)
            if len(c) >= 60 and any(k in c.lower() for k in KEYWORDS):
                yield c


def main():
    records = []
    skipped = 0

    for filename, (scheme, url, category) in SOURCES.items():
        path = RAW_DIR / filename
        if not path.exists():
            print(f"Missing file: {filename}")
            continue

        paras = paragraphs_from_pdf(path) if filename.endswith(".pdf") else paragraphs_from_html(path)
        for para in paras:
            try:
                rec_id = len(records) + 1
                income = find_income_limit(para)
                loan = find_loan_limit(para)
                eligible = find_who_is_eligible(para, scheme)

                records.append(
                    Record(
                        id=rec_id,
                        scheme_name=scheme,
                        who_is_eligible=eligible,
                        income_limit=income,
                        loan_limit=loan,
                        benefit=para[:600],
                        source_url=url,
                        category=category,
                    )
                )
            except Exception as e:
                skipped += 1
                print("Bad row skipped:", e)

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUT_FILE.write_text(
        json.dumps([asdict(r) for r in records], indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"Saved {len(records)} records, skipped {skipped}")


if __name__ == "__main__":
    main()
