# app/smart_search.py
from typing import Any, Dict, List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.records import load_records


def record_text(record: Dict[str, Any]) -> str:
    """Combine key record fields into a single search text string."""
    fields = ("scheme_name", "who_is_eligible", "income_limit", "loan_limit", "benefit")
    return " ".join(str(record.get(f, "")) for f in fields if record.get(f) is not None)


class SmartSearch:
    def __init__(self):
        self.records = load_records()
        self.vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        corpus = [record_text(r) for r in self.records]
        if corpus and any(t.strip() for t in corpus):
            self.matrix = self.vectorizer.fit_transform(corpus)
        else:
            self.matrix = None

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Rank records with TF-IDF vectorizer and cosine similarity."""
        query = query.strip()
        if not query or self.matrix is None or len(self.records) == 0:
            return []

        scores = cosine_similarity(self.vectorizer.transform([query]), self.matrix)[0]
        ranked = sorted(zip(scores, self.records), key=lambda x: x[0], reverse=True)
        return [
            {**record, "score": round(float(score), 4)}
            for score, record in ranked[:top_k]
            if score > 0
        ]
