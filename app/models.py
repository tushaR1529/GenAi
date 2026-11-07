# app/models.py
from dataclasses import dataclass
from typing import Optional


@dataclass
class Record:
    id: int
    scheme_name: str
    who_is_eligible: str
    income_limit: Optional[str]
    loan_limit: Optional[str]
    benefit: str
    source_url: str
    category: Optional[str] = "scheme_rule"
