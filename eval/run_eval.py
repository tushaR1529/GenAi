# eval/run_eval.py
"""
Script to evaluate VidyaLoan prompts (v1 vs v2) across the 10 benchmark questions
using the configured LLMClient (Gemini / Groq / Grounded Fallback) and output fresh results.json.
"""
import json
import sys
import time
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.llm import LLMClient
QUESTIONS_PATH = ROOT_DIR / "data" / "questions.json"
RESULTS_PATH = ROOT_DIR / "eval" / "results.json"


def run_evaluation():
    client = LLMClient()
    print(f"Running evaluation with LLM provider: {client.provider}")
    if client.provider == "gemini":
        print(f"Gemini Model: {client.gemini_model}")
    elif client.provider == "groq":
        print(f"Groq Model: {client.groq_model}")

    questions = json.loads(QUESTIONS_PATH.read_text(encoding="utf-8"))
    results = []

    for idx, item in enumerate(questions, 1):
        qid = item["id"]
        qtext = item["question"]
        print(f"[{idx}/{len(questions)}] Q{qid}: {qtext}")

        # Evaluate Prompt v1
        print("  Evaluating v1...")
        resp_v1 = client.chat(qtext, prompt_version="v1")
        time.sleep(3)  # Respect free tier rate limits

        # Evaluate Prompt v2
        print("  Evaluating v2...")
        resp_v2 = client.chat(qtext, prompt_version="v2")
        time.sleep(3)

        results.append({
            "id": qid,
            "question": qtext,
            "v1": resp_v1,
            "v2": resp_v2,
        })

    RESULTS_PATH.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nFresh evaluation results saved to: {RESULTS_PATH}")
    print(f"Total questions evaluated: {len(results)}")


if __name__ == "__main__":
    run_evaluation()
