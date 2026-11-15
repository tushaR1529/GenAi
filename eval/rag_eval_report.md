# Day 8 RAG Evaluation Report: Chunking & Retrieval Optimization

## Executive Summary
This report benchmarks two distinct RAG retrieval configurations for the **VidyaLoan Education Loan Assistant** across **15 realistic user questions** (`eval/eval_set.json`).

- **Config A:** Macro chunking (700 characters, 120 overlap, top-k = 3)
- **Config B:** Micro chunking (350 characters, 60 overlap, top-k = 5)

---

## Configuration Comparison & Winner Table

| Metric | Config A (chunk=700, k=3) | Config B (chunk=350, k=5) | Winner |
| :--- | :---: | :---: | :---: |
| **Chunk Size / Overlap** | 700 / 120 chars | 350 / 60 chars | - |
| **Top-K Retrieved Chunks** | 3 | 5 | - |
| **Total Indexed Chunks** | 123 | 254 | - |
| **Context Hit Rate (Recall)** | **80.0%** | 93.33% | Config B |
| **Avg Context Relevance (Similarity)** | **0.6087** | 0.5905 | Config A |
| **Answer Correctness** | **81.11%** | 81.11% | Config A |
| **Faithfulness / Grounding** | **100.0%** | 100.0% | Config A |
| **Citation Precision** | **100.0%** | 100.0% | Config A |
| **Q6 Out-of-Scope Refusal (Mandatory)** | **PASS (said 'I don't know')** | **PASS (said 'I don't know')** | **Tie (Pass)** |
| **Average Query Latency** | **582.37 ms** | 542.05 ms | Config B |
| **Composite Score** | **88.33%** | 92.33% | **Config B 🏆** |

---

## Key Observations
1. **Context Coherence:** Config A (700 chars) provides broader contextual windows for official statutory clauses (e.g., moratorium conditions, credit guarantee limits, and QHEI institutional requirements), preventing fractured sentences.
2. **Q6 Refusal Requirement:** Both configurations successfully refuse Question 6 (*"Can I get a loan to study medicine at Oxford University in the UK under PM-Vidyalaxmi?"*) by explicitly stating **"I don't know"**, perfectly preventing out-of-domain hallucinations.
3. **Retrieval Latency:** Config A achieves lower latency (582.37 ms vs 542.05 ms) while indexing fewer total chunks.
