# app/models.py
from dataclasses import dataclass


@dataclass
class Record:
    id: int
    scheme_name: str
    who_is_eligible: str
    income_limit: str | None
    loan_limit: str | None
    benefit: str
    source_url: str
    category: str | None = "scheme_rule"
