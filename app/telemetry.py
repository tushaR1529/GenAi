# app/telemetry.py
"""
Observability and telemetry module for VidyaLoan:
- Request latency tracking (milliseconds)
- Token estimation (prompt, completion, total)
- Structured JSONL request logger
- Prompt injection and jailbreak detector
"""
import json
import logging
import math
import re
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger("vidyaloan.telemetry")

ROOT_DIR = Path(__file__).resolve().parent.parent
LOG_FILE = ROOT_DIR / "data" / "request_logs.jsonl"


def estimate_tokens(text: str) -> int:
    """
    Estimate token count for a text string using standard subword heuristics
    (~4 characters per token in English, with word-boundary awareness).
    """
    if not text:
        return 0
    words = len(text.split())
    chars = len(text)
    # Average between char-based and word-based estimation
    char_tokens = chars / 4.0
    word_tokens = words * 1.3
    return max(1, math.ceil((char_tokens + word_tokens) / 2.0))


def is_prompt_injection(text: str) -> bool:
    """
    Detect adversarial prompt injection, jailbreak attempts, or system prompt extraction.
    """
    if not text:
        return False

    t = text.lower()
    patterns = [
        r"ignore\s+(all\s+)?(previous|prior|above)\s+(instructions|prompts|rules|commands)",
        r"(system\s+)?override\s+(all\s+)?(instructions|rules|prompts)",
        r"(reveal|print|show|output|leak|expose)\s+(your\s+)?(system\s+prompt|instructions|api\s*key|secret)",
        r"you\s+are\s+now\s+(dan|unrestricted|jailbroken|an\s+ai\s+without\s+rules)",
        r"(bypass|disable|ignore)\s+(safety|guardrails|loan\s+restrictions)",
        r"disregard\s+(all\s+)?(rules|instructions)",
        r"act\s+as\s+(dan|an\s+unrestricted)",
        r"pretend\s+you\s+have\s+no\s+(rules|limits|guidelines)",
    ]
    return any(re.search(pat, t) for pat in patterns)


def log_request_telemetry(
    endpoint: str,
    question: str,
    latency_ms: float,
    prompt_tokens: int,
    completion_tokens: int,
    cached: bool = False,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Log request telemetry (latency, token consumption, cache status)
    to data/request_logs.jsonl and application logger.
    """
    record = {
        "timestamp": datetime.now().isoformat(),
        "endpoint": endpoint,
        "question": question[:100] + ("..." if len(question) > 100 else ""),
        "latency_ms": round(latency_ms, 2),
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": prompt_tokens + completion_tokens,
        "cached": cached,
        "metadata": metadata or {},
    }

    # Console logging
    logger.info(
        "[%s] %s | Latency: %.2fms | Tokens: %d (in: %d, out: %d) | Cached: %s",
        record["timestamp"],
        endpoint,
        record["latency_ms"],
        record["total_tokens"],
        record["prompt_tokens"],
        record["completion_tokens"],
        record["cached"],
    )

    # Append to JSONL log file
    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception as e:
        logger.warning("Could not append to telemetry log file: %s", e)

    return record


def get_telemetry_summary() -> dict[str, Any]:
    """
    Analyze data/request_logs.jsonl and return summary metrics:
    - Total queries
    - Cache hit ratio
    - p50, p95, p99 latency
    - Average tokens per query
    """
    if not LOG_FILE.exists():
        return {
            "total_requests": 0,
            "cache_hit_ratio_pct": 0.0,
            "avg_latency_ms": 0.0,
            "p50_latency_ms": 0.0,
            "p95_latency_ms": 0.0,
            "p99_latency_ms": 0.0,
            "avg_tokens": 0.0,
        }

    records: list[dict[str, Any]] = []
    try:
        with LOG_FILE.open("r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    records.append(json.loads(line))
    except Exception:
        records = []

    if not records:
        return {
            "total_requests": 0,
            "cache_hit_ratio_pct": 0.0,
            "avg_latency_ms": 0.0,
            "p50_latency_ms": 0.0,
            "p95_latency_ms": 0.0,
            "p99_latency_ms": 0.0,
            "avg_tokens": 0.0,
        }

    latencies = sorted(r.get("latency_ms", 0.0) for r in records)
    total_reqs = len(records)
    cached_count = sum(1 for r in records if r.get("cached", False))
    total_tokens = sum(r.get("total_tokens", 0) for r in records)

    def percentile(p: float) -> float:
        idx = min(int(math.ceil(p * total_reqs)) - 1, total_reqs - 1)
        return round(latencies[max(0, idx)], 2)

    return {
        "total_requests": total_reqs,
        "cache_hits": cached_count,
        "cache_hit_ratio_pct": round((cached_count / total_reqs) * 100.0, 2),
        "avg_latency_ms": round(sum(latencies) / total_reqs, 2),
        "p50_latency_ms": percentile(0.50),
        "p95_latency_ms": percentile(0.95),
        "p99_latency_ms": percentile(0.99),
        "avg_tokens": round(total_tokens / total_reqs, 1),
    }
