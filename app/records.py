# app/records.py
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from data.sample_records import SAMPLE_RECORDS

RECORDS_FILE = Path("data/records.json")


def load_records() -> List[Dict[str, Any]]:
    """Load all records from data/records.json if available, else fallback to SAMPLE_RECORDS."""
    if RECORDS_FILE.exists():
        try:
            data = json.loads(RECORDS_FILE.read_text(encoding="utf-8"))
            if isinstance(data, list) and len(data) > 0:
                return data
        except Exception:
            pass
    return SAMPLE_RECORDS.copy()


def search(keyword: str) -> List[Dict[str, Any]]:
    """Search records using a keyword."""
    records = load_records()
    keyword = keyword.strip().lower()
    if not keyword:
        return []

    results = []
    for record in records:
        record_text = " ".join(str(value) for value in record.values()).lower()
        if keyword in record_text:
            results.append(record)

    return results


def count_by(field: str) -> Dict[str, int]:
    """Count records according to a selected field."""
    records = load_records()
    counts: Dict[str, int] = {}
    for record in records:
        category = record.get(field, "Unknown")
        counts[category] = counts.get(category, 0) + 1
    return counts


def get_by_id(record_id: int) -> Optional[Dict[str, Any]]:
    """Find a record using its unique ID."""
    records = load_records()
    for record in records:
        if record.get("id") == record_id:
            return record
    return None
