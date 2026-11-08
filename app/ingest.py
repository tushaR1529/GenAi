# app/ingest.py
import json
import re
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Optional

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


def find_income_limit(text: str, scheme: str = "") -> Optional[str]:
    """Extract or determine the applicable family income limit."""
    t = text.lower()

    # Direct explicit text pattern matches
    m = re.search(
        r"(?:annual\s+)?(?:family\s+|parental\s+)?income\s*(?:is|upto|up\s+to|less\s+than|ceiling\s+of|limit\s+of|of|not\s+exceeding)?\s*(?:Rs\.?|₹)?\s*([\d.,]+)\s*(?:lakh|crore)?",
        text,
        re.IGNORECASE,
    )
    if m:
        val = m.group(1).strip()
        return f"Rs. {val} lakh per annum"

    if re.search(r"(?:Rs\.?|₹)?\s*8,00,000", text) or re.search(r"8\s*lakh", text, re.IGNORECASE):
        if "income" in t or "subvention" in t:
            return "Rs. 8 lakh per annum"

    if re.search(r"(?:Rs\.?|₹)?\s*4,50,000", text) or re.search(r"4\.5\s*lakh", text, re.IGNORECASE):
        if "income" in t or "csis" in t or "parental" in t:
            return "Rs. 4.5 lakh per annum"

    if "all income categories" in t or "all income groups" in t or "all family income groups" in t:
        return "All family income groups"

    if "economically weaker" in t or "ews" in t:
        return "Rs. 4.5 lakh per annum (EWS)"

    # Scheme-specific contextual inferencing
    if "3% interest subvention" in t or "3 % interest subvention" in t or "3% subvention" in t:
        return "Rs. 8 lakh per annum"

    if "csis" in t or scheme == "PM-USP CSIS":
        return "Rs. 4.5 lakh per annum"

    if "75% credit guarantee" in t or "credit guarantee" in t or "collateral-free" in t or "collateral free" in t:
        return "All family income groups"

    if "moratorium" in t:
        if "csis" in t:
            return "Rs. 4.5 lakh per annum"
        if "vidyalaxmi" in t or "3%" in t:
            return "Rs. 8 lakh per annum"
        return "Rs. 4.5 lakh to Rs. 8 lakh per annum"

    return None


def find_loan_limit(text: str, scheme: str = "") -> Optional[str]:
    """Extract or determine the applicable loan ceiling / coverage limit."""
    t = text.lower()

    # Direct explicit text pattern matches
    if re.search(r"7\.5\s*lakh", text, re.IGNORECASE):
        return "Up to Rs. 7.5 lakh"

    if re.search(r"10(?:\.0)?\s*lakh", text, re.IGNORECASE):
        return "Up to Rs. 10 lakh"

    m = re.search(
        r"loan[s]?\s*(?:up\s+to|amount\s+of|of|limit\s+of|ceiling\s+of)?\s*(?:Rs\.?|₹)?\s*([\d.,]+)\s*lakh",
        text,
        re.IGNORECASE,
    )
    if m:
        val = m.group(1).strip()
        return f"Up to Rs. {val} lakh"

    # Scheme-specific contextual inferencing
    if "75% credit guarantee" in t or "credit guarantee" in t:
        return "Up to Rs. 7.5 lakh"

    if "3% interest subvention" in t or "3 % interest subvention" in t or "3% subvention" in t:
        return "Up to Rs. 10 lakh"

    if "csis" in t or scheme == "PM-USP CSIS":
        return "Up to Rs. 10 lakh"

    if "collateral-free" in t or "collateral free" in t or "guarantor-free" in t or "guarantor free" in t:
        return "Up to Rs. 7.5 lakh (guarantee) / Rs. 10 lakh (subvention)"

    if "moratorium" in t:
        return "Up to Rs. 10 lakh"

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
    """Extract text paragraphs from PDF file without splitting decimal points."""
    reader = PdfReader(path)
    for page in reader.pages:
        text = page.extract_text() or ""
        blocks = re.split(r"\n\s*\n", text)
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
                income = find_income_limit(para, scheme)
                loan = find_loan_limit(para, scheme)
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
    both = sum(1 for r in records if r.income_limit and r.loan_limit)
    print(f"Saved {len(records)} records ({both} complete with both income_limit and loan_limit), skipped {skipped}")


if __name__ == "__main__":
    main()
