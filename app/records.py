
# app/records.py

from data.sample_records import SAMPLE_RECORDS


def load_records():
    """Load all records from the dataset."""

    return SAMPLE_RECORDS.copy()


def search(keyword):
    """Search records using a keyword."""

    records = load_records()

    keyword = keyword.strip().lower()

    if not keyword:
        return []

    results = []

    for record in records:

        record_text = " ".join(
            str(value) for value in record.values()
        ).lower()

        if keyword in record_text:
            results.append(record)

    return results


def count_by(field):
    """Count records according to a selected field."""

    records = load_records()

    counts = {}

    for record in records:

        category = record.get(field, "Unknown")

        counts[category] = counts.get(category, 0) + 1

    return counts


def get_by_id(record_id):
    """Find a record using its unique ID."""

    records = load_records()

    for record in records:

        if record["id"] == record_id:
            return record

    return None
