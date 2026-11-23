# VidyaLoan: 14-Day Engineering Milestone Tracker (PROGRESS.md)

[![Project Status: 100% Complete](https://img.shields.io/badge/Project_Status-100%25_Complete-brightgreen.svg)](#)
[![All Milestones Closed](https://img.shields.io/badge/Milestones-All_Closed-blue.svg)](#)
[![Tests: 34 Passing](https://img.shields.io/badge/Tests-34_Passing-brightgreen.svg)](tests/)
[![Ruff Lint: 0 Errors](https://img.shields.io/badge/Ruff_Lint-0_Errors-black.svg)](#)
[![Release Tag: final](https://img.shields.io/badge/Release_Tag-final-orange.svg)](#)

> **All open tasks and engineering milestones across the 14-day development cycle are fully implemented, thoroughly tested, verified, and closed.**

---

## 📅 Daily Milestones & Completion Status

### [x] Day 1: Project Initialization & Scope Definition
- [x] Initialized project repository with Git tracking and standard directory structure.
- [x] Created `day01_intro.py` defining the VidyaLoan project card, problem statement, and user persona.
- [x] Built interactive CLI menu in `day01_menu.py` for terminal-based navigation.
- [x] **Status:** `CLOSED` (Completed)

### [x] Day 2: Scheme Discovery & Domain Research
- [x] Researched Indian government Central Sector education loan schemes: PM-Vidyalaxmi, PM-USP CSIS, and CGFSEL.
- [x] Identified key eligibility variables: gross parental income ($\le$ ₹4.5L vs $\le$ ₹8L), moratorium period (course + 1 year), 3% subvention, and 75% credit guarantees.
- [x] Created initial seed records in `data/sample_records.py`.
- [x] **Status:** `CLOSED` (Completed)

### [x] Day 3: Automated Document Ingestion Pipeline
- [x] Built automated downloader in `app/fetch.py` fetching official PIB guidelines, Canara Bank CSIS circulars, and official FAQs.
- [x] Developed robust PDF parser (PyPDF) and HTML parser (BeautifulSoup4) in `app/ingest.py`.
- [x] Extracted and normalized 59 structured scheme records into `data/records.json`.
- [x] **Status:** `CLOSED` (Completed)

### [x] Day 4: Exploratory Data Analysis & REST API Foundation
- [x] Implemented Pandas dataset exploration script `analysis/explore.py` profiling scheme distributions, categories, and income caps.
- [x] Initialized FastAPI application in `app/main.py`.
- [x] Built core REST endpoints: `GET /health`, `GET /records`, and `GET /records/{id}`.
- [x] Added keyword search engine in `app/records.py`.
- [x] **Status:** `CLOSED` (Completed)

### [x] Day 5: LLM Foundations & Checkpoint 1 Submission
- [x] Authored technical architecture guide [`docs/how_llms_work.md`](docs/how_llms_work.md) covering tokenization, self-attention, and hallucination mechanics.
- [x] Formulated core VidyaLoan system prompt [`prompts/system_prompt.txt`](prompts/system_prompt.txt) with grounding constraints.
- [x] Curated 10 real student loan evaluation questions in [`data/questions.json`](data/questions.json).
- [x] Tagged and released `checkpoint-1`.
- [x] **Status:** `CLOSED` (Completed)

### [x] Day 6: Universal LLM Client & Prompt Engineering
- [x] Implemented universal LLM client `app/llm.py` supporting Groq (Llama-3.3-70B) and Google Gemini (Gemini 1.5 Flash).
- [x] Created resilient grounded offline fallback engine for zero-dependency local execution.
- [x] Evaluated Task Prompt v1 (Direct & Rule-centric) vs Task Prompt v2 (Comprehensive Student Advisory) across 10 benchmark queries in [`eval/prompt_compare.md`](eval/prompt_compare.md).
- [x] Exposed `POST /chat` endpoint returning structured JSON answers with confidence scores.
- [x] **Status:** `CLOSED` (Completed)

### [x] Day 7: Document Chunking, ChromaDB Vectorstore & Semantic Search
- [x] Implemented boundary-aware document chunker in `app/chunking.py` preserving source file, page number, and section titles.
- [x] Built ONNX runtime embedding wrapper in `app/embed.py` using `all-MiniLM-L6-v2`.
- [x] Created persistent vector database in `app/vectorstore.py` indexing document chunks into ChromaDB.
- [x] Exposed semantic vector search endpoint `GET /search/semantic` with similarity scoring.
- [x] Evaluated retrieval quality across 10 benchmark queries in [`eval/search_results.md`](eval/search_results.md).
- [x] **Status:** `CLOSED` (Completed)

### [x] Day 8: Citation-Backed RAG Pipeline & Configuration Benchmark
- [x] Engineered RAG pipeline in `app/rag.py` and exposed `POST /ask`.
- [x] Enforced structured citations (`source`, `page`, `title`) grounded exclusively in retrieved chunks.
- [x] Added out-of-scope refusal guardrail (Question 6: Oxford University UK query) returning *"I don't know"*.
- [x] Built automated benchmark harness `eval/run_eval.py` testing Config A (Macro: 700 chars, k=3) vs Config B (Micro: 350 chars, k=5) across 15 questions in [`eval/eval_set.json`](eval/eval_set.json).
- [x] Declared Config B winner with **93.3% context recall** and **100% citation precision** ([`eval/rag_eval_report.md`](eval/rag_eval_report.md)).
- [x] **Status:** `CLOSED` (Completed)

### [x] Day 9: Financial Calculator Tool, ReAct Loop & LangGraph Human Gate
- [x] Engineered deterministic financial modeling tool in `app/tools.py` (`education_loan_cost_calculator`):
  - Accurately models moratorium interest (course + 1 year).
  - Evaluates 100% CSIS subsidy ($\le$ ₹4.5L) vs 3% PM-Vidyalaxmi subvention ($\le$ ₹8L for QHEIs).
  - Evaluates 75% CGFSEL credit guarantee eligibility ($\le$ ₹7.5L).
  - Computes post-moratorium amortized monthly EMIs.
- [x] Built hand-written ReAct agent loop in `app/agent_loop.py`.
- [x] Built stateful multi-agent workflow with LangGraph in `app/graph.py` using `StateGraph` and `MemorySaver`.
- [x] Integrated Human-in-the-Loop approval gate pausing execution on calculations $> ₹4.0 \text{ Lakh}$.
- [x] Exposed `POST /agent` endpoint with session memory and approval resumption.
- [x] Authored comprehensive agent tests in `eval/test_agent_day9.py`.
- [x] **Status:** `CLOSED` (Completed)

### [x] Day 10: Streamlit Web UI, Visualizer & Checkpoint 2
- [x] Developed interactive Streamlit web application in `ui/app.py`.
- [x] Integrated multi-turn conversational chat with citation badges.
- [x] Created **Signature Feature**: Interactive **Loan Cost Breakdown Stacked Bar Chart** (Plotly):
  - Visualizes Principal vs Government Subsidy vs Family Moratorium Cost vs Repayment Interest.
  - Live scenario comparison: "Without Scheme" vs "With VidyaLoan Scheme".
- [x] Implemented thumbs up/down user feedback system logging to `data/feedback.json`.
- [x] Captured demo screenshot [`docs/checkpoint2_demo.png`](docs/checkpoint2_demo.png).
- [x] Tagged and released `checkpoint-2`.
- [x] **Status:** `CLOSED` (Completed)

### [x] Day 11: Hermetic Pytest Suite, Ruff Quality & Containerization
- [x] Created formal unit test suite in `tests/`:
  - `test_records.py`: Record loading, lookup, and search (7 tests).
  - `test_search.py`: TF-IDF and Chroma vector search (5 tests).
  - `test_calculator.py`: Financial calculation tool edge cases (7 tests).
  - `test_api.py`: FastAPI endpoints `/health`, `/records`, `/ask`, and `/agent` (11 tests).
- [x] Configured Ruff linter in `pyproject.toml`; achieved 0 errors across codebase.
- [x] Containerized application with `Dockerfile`, `.dockerignore`, and `docker-compose.yml`.
- [x] Tagged and released `day-11`.
- [x] **Status:** `CLOSED` (Completed)

### [x] Day 12: GitHub Actions CI/CD Pipeline & Live Render Cloud Deployment
- [x] Set up continuous integration workflow in `.github/workflows/ci.yml` (Ruff, Pytest, Docker build).
- [x] Deployed live on Render cloud platform ([https://vidyaloan-api.onrender.com](https://vidyaloan-api.onrender.com)) with `render.yaml`.
- [x] Configured public `/health` monitoring and interactive `/docs` Swagger endpoint.
- [x] Created `run_app.py` for unified single-port multi-service hosting.
- [x] Tagged and released `day-12`.
- [x] **Status:** `CLOSED` (Completed)

### [x] Day 13: Production Hardening, In-Memory Caching & Capstone Portfolio
- [x] Implemented structured latency tracking and token estimator in `app/telemetry.py`.
- [x] Built thread-safe in-memory LRU query cache in `app/cache.py` (p50 latency 1.42ms, 0 tokens on hit).
- [x] Enforced input length validation limits (3–500 chars) returning HTTP 400.
- [x] Integrated deterministic prompt-injection defense deflecting jailbreak attempts.
- [x] Added `GET /stats` telemetry endpoint.
- [x] Expanded test suite to 34 passing tests (`test_prompt_injection_defense`, `test_query_caching`, `test_input_length_limits`, `test_stats_endpoint`).
- [x] Authored 3 quantified resume bullets in [`docs/resume.md`](docs/resume.md).
- [x] Rewrote [`README.md`](README.md) to showcase problem narrative, Mermaid architecture diagram, demo video link, and production numbers.
- [x] **Status:** `CLOSED` (Completed)

### [x] Day 14: Final Capstone Delivery & Interview Preparation
- [x] Authored comprehensive technical interview guide in [`docs/interview.md`](docs/interview.md):
  - 60-second elevator pitch for VidyaLoan.
  - Core engineering interview story (hardest technical problem: reconciling overlapping schemes & strictly enforcing zero arithmetic hallucinations).
  - 10 likely technical interview questions with deep architectural answers.
- [x] Documented and rehearsed the live demo protocol twice:
  - Rehearsal 1: CSIS subsidy & RAG citations retrieval.
  - Rehearsal 2: High-value loan approval gate, injection defense & out-of-scope refusal.
- [x] Closed all open items in [`PROGRESS.md`](PROGRESS.md).
- [x] Verified zero Ruff errors and all 34 passing Pytest unit tests.
- [x] Tagged final release: `git tag final`.
- [x] Pushed all code, documentation, and tags to `origin/main`.
- [x] **Status:** `CLOSED` (Completed)

---

## 🏆 Final System Verification Summary

| Verification Category | Target Standard | Measured Result | Final Status |
| :--- | :---: | :---: | :---: |
| **Unit & Integration Tests** | $\ge 30$ tests passing | **34 / 34 tests passing** | ✅ **VERIFIED** |
| **Code Style & Linting** | Ruff 0 errors | **0 errors / 0 warnings** | ✅ **VERIFIED** |
| **RAG Context Recall** | $\ge 80.0\%$ | **93.33%** | ✅ **VERIFIED** |
| **Citation Precision** | 100.0% | **100.0%** | ✅ **VERIFIED** |
| **Arithmetic Hallucination** | 0.0% | **0.0% (Deterministic Tool)** | ✅ **VERIFIED** |
| **Cache Hit Latency** | $< 5.0\text{ ms}$ | **1.42 ms (p50) / 2.84 ms (p95)** | ✅ **VERIFIED** |
| **Input Limits Guardrail** | 3–500 chars | **Enforced (HTTP 400)** | ✅ **VERIFIED** |
| **Prompt Injection Defense** | 100% deflection | **100% deflection rate** | ✅ **VERIFIED** |
| **Containerization** | Docker Compose | **Multi-service isolated** | ✅ **VERIFIED** |
| **CI/CD Pipeline** | GitHub Actions | **Green build & test status** | ✅ **VERIFIED** |
| **Live Cloud Deployment** | Public `/health` | **Live on Render (`status: ok`)** | ✅ **VERIFIED** |
| **Release Tagging** | `final` tag | **Tagged & pushed to remote** | ✅ **VERIFIED** |
