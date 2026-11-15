# VidyaLoan: AI-Powered Education Loan Assistance System

**Product:** VidyaLoan is an AI assistant that explains Indian government education loan schemes (PM-Vidyalaxmi, PM-USP CSIS, and CGFSEL) in simple, accessible language.

**Target User:** Students and parents, especially from families with an annual income under Rs. 8 lakh, who need guidance understanding which education loan scheme applies to them.

**Problem:** Multiple overlapping schemes have different income limits, subsidies, and guarantee rules. Families often struggle to identify what they qualify for, how much the government will cover, and what the loan will actually cost over time.

**Data Sources:**
- **PM-Vidyalaxmi Scheme Guidelines:** Press Information Bureau / Ministry of Education ([PIB Guidelines PDF](https://static.pib.gov.in/WriteReadData/specificdocs/documents/2026/jul/doc2026729936401.pdf))
- **PM-Vidyalaxmi Official Portal FAQs:** [pmvidyalaxmi.co.in FAQs](https://pmvidyalaxmi.co.in/PublicFaq.aspx)
- **Central Sector Interest Subsidy (PM-USP CSIS) Guidelines:** Canara Bank / Ministry of Education ([CSIS Guidelines PDF](https://www.canarabank.bank.in/documents/d/guest/csis-guideline-01-04-2022))

---

## Features

- **Document Fetching & Ingestion Pipeline:** Automated downloader (`app/fetch.py`) and PDF/HTML parser (`app/ingest.py`) extracting structured scheme rules into `data/records.json`.
- **Smart Search (TF-IDF + Cosine Similarity):** Relevance-ranked keyword and semantic similarity search across loan criteria, benefits, and scheme rules (`app/smart_search.py`).
- **RESTful FastAPI Service:** Endpoints for health checks, record retrieval, TF-IDF smart search, semantic vector search, user questions, and AI chat (`app/main.py`).
- **Document Chunking & Embeddings (Day 7):** Boundary-aware chunking preserving source, page, and title metadata (`app/chunking.py`) with ONNX-accelerated MiniLM embedding wrapper (`app/embed.py`).
- **Persistent Chroma Vectorstore (Day 7):** Persistent Chroma collection indexing document chunks with metadata filtering and similarity search (`app/vectorstore.py`).
- **Semantic Search Endpoint (`GET /search/semantic`):** High-speed semantic search retrieving grounded context with similarity scores (`app/main.py`).
- **RAG Answering with Citations (Day 8):** RAG answering pipeline (`app/rag.py` & `POST /ask`) answering questions strictly from retrieved chunks with structured source citations (`source`, `page`, `title`).
- **Out-of-Scope Guardrails (Day 8):** Enforced guardrails that refuse unsupported queries (such as foreign studies at Oxford University in Q6) with `"I don't know"`.
- **RAG Configuration Benchmark (Day 8):** 15-question evaluation suite (`eval/eval_set.json` & `eval/run_eval.py`) benchmarking chunk size and top-k retrieval configurations.
- **LLM Provider Wrapper (Groq / Gemini):** Universal LLM client with system prompt grounding, JSON output parsing, and resilient fallback (`app/llm.py`).
- **Prompt Engineering & Systematic Evaluation:** Dual prompt versions (Direct Factual vs Comprehensive Advisory) evaluated across 10 real user questions (`eval/prompt_compare.md`).
- **Exploratory Data Analysis:** Fast pandas-based dataset profiling computing distribution across schemes, categories, and income limits (`analysis/explore.py`).
- **Interactive CLI & Exploration:** Command-line interface for searching and inspecting scheme records (`app/cli.py`).

---

## Technologies

- **Backend & API:** Python 3.11+, FastAPI, Uvicorn, Pydantic, Python-dotenv
- **LLMs & Prompt Engineering:** Groq (Llama-3.3-70B), Google Gemini (Gemini 1.5 Flash), Requests
- **Data & Text Processing:** Pandas, Scikit-learn (TF-IDF), PyPDF, BeautifulSoup4
- **Data Models:** Python dataclasses (`app/models.py`)

---

## Project Structure

```text
├── analysis/
│   └── explore.py             # Prints 3 key facts about records using Pandas
├── app/
│   ├── chunking.py            # Day 7: Document chunker preserving source, page, title
│   ├── cli.py                 # Command-line interface for browsing records
│   ├── embed.py               # Day 7: Embedding wrapper using all-MiniLM-L6-v2 ONNX
│   ├── explore.py             # Mirror for exploratory analysis
│   ├── fetch.py               # Fetches official government PDFs & HTML FAQs
│   ├── ingest.py              # Parses raw documents into structured Record dataclasses
│   ├── llm.py                 # Day 6: Groq/Gemini provider wrapper + JSON parser
│   ├── main.py                # FastAPI REST service (/health, /records, /search, /chat, /ask)
│   ├── models.py              # Record dataclass definition
│   ├── rag.py                 # Day 8: RAG pipeline with citations & out-of-scope refusal
│   ├── records.py             # Data loading, search, and lookup functions
│   ├── smart_search.py        # TF-IDF vectorizer + Cosine similarity search engine
│   └── vectorstore.py         # Day 7: Persistent Chroma collection indexer & searcher
├── data/
│   ├── chroma_db/             # Day 7: Persistent Chroma database
│   ├── raw/                   # Downloaded government guidelines and FAQs
│   │   ├── csis_guidelines.pdf
│   │   ├── pm_vidyalaxmi_faq.html
│   │   └── pm_vidyalaxmi_guidelines.pdf
│   ├── questions.json         # 10 real VidyaLoan user questions
│   ├── records.json           # Ingested scheme records (59 structured entries)
│   └── sample_records.py      # Baseline seed records
├── docs/
│   └── how_llms_work.md       # Day 5: How LLMs work, diagram, 10 user questions, Checkpoint 1
├── eval/
│   ├── eval_set.json          # Day 8: 15-question benchmark evaluation dataset
│   ├── generate_search_eval.py# Day 7: Semantic search evaluation script
│   ├── prompt_compare.md      # Day 6: Comparison of Prompt v1 vs Prompt v2 across 10 questions
│   ├── rag_eval_report.md     # Day 8: Detailed RAG evaluation report and winner analysis
│   ├── rag_eval_results.json  # Day 8: Quantitative metrics for tested RAG configs
│   ├── results.json           # Day 6: Benchmark evaluation outputs
│   ├── run_eval.py            # Day 8: RAG configuration benchmark execution harness
│   └── search_results.md      # Day 7: Semantic search hits report across 10 benchmark questions
├── prompts/
│   ├── system_prompt.txt      # Core VidyaLoan system prompt & constraints
│   ├── task_prompt_v1.txt     # Task prompt version 1: Direct & rule-centric
│   └── task_prompt_v2.txt     # Task prompt version 2: Comprehensive student advisory
├── .env.example               # Template for LLM API keys (.env is not committed)
├── day01_intro.py             # Day 1 project card demonstration
├── requirements.txt           # Project dependencies
└── README.md                  # Project documentation & instructions
```

---

## How to Run

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment (Optional for Live LLMs)
Copy `.env.example` to `.env` and insert your Gemini or Groq API key:
```bash
cp .env.example .env
```
*(If no API key is provided, `app/llm.py` automatically uses its deterministic grounded fallback engine for offline testing and evaluation).*

### 3. Fetch Government Documents (Day 3)
Downloads official PM-Vidyalaxmi guidelines, PM-USP CSIS guidelines, and portal FAQs with timeouts and SSL handling:
```bash
python -m app.fetch
```

### 4. Ingest Documents into Structured Records (Day 3)
Extracts and normalizes scheme records into `data/records.json`:
```bash
python -m app.ingest
```

### 5. Run Exploratory Analysis (Day 4)
Prints 3 key dataset facts using Pandas:
```bash
python analysis/explore.py
```

### 6. Launch FastAPI Service (Day 4, 5 & 6)
Start the REST API server:
```bash
uvicorn app.main:app --reload --port 8000
```
Open interactive Swagger documentation in your browser at:
**[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**

#### Available API Endpoints:
- `GET /health`: Returns service status and total ingested record count.
  ```bash
  curl http://127.0.0.1:8000/health
  ```
- `GET /records?limit=10`: Returns a list of scheme records up to the specified limit.
  ```bash
  curl http://127.0.0.1:8000/records?limit=5
  ```
- `GET /records/{id}`: Returns a single record by ID (or 404 if missing).
  ```bash
  curl http://127.0.0.1:8000/records/1
  ```
- `GET /search?q={query}`: Searches records using TF-IDF and Cosine similarity.
  ```bash
  curl "http://127.0.0.1:8000/search?q=interest+subvention"
  ```
- `GET /search/semantic?q={query}&limit=5` (Day 7): High-speed semantic search over indexed document chunks using persistent Chroma vectorstore.
  ```bash
  curl "http://127.0.0.1:8000/search/semantic?q=credit+guarantee+limit&limit=3"
  ```
- `POST /questions`: Saves a user question into `data/questions.json`.
  ```bash
  curl -X POST http://127.0.0.1:8000/questions -H "Content-Type: application/json" -d "{\"question\": \"Can I get loan for diploma?\"}"
  ```
- `POST /chat` (Day 6): AI loan consultation returning structured JSON with answer, confidence, and follow-up.
  ```bash
  curl -X POST http://127.0.0.1:8000/chat -H "Content-Type: application/json" -d "{\"message\": \"Which loan I should apply for less than 5 lakh income?\", \"prompt_version\": \"v2\"}"
  ```
- `POST /ask` (Day 8): RAG endpoint answering questions strictly using retrieved document chunks with source citations and out-of-scope refusal.
  ```bash
  curl -X POST http://127.0.0.1:8000/ask -H "Content-Type: application/json" -d "{\"question\": \"What is the maximum loan limit covered by the 75% credit guarantee?\", \"top_k\": 3}"
  ```
  *Refusal Example (Q6 foreign study query):*
  ```bash
  curl -X POST http://127.0.0.1:8000/ask -H "Content-Type: application/json" -d "{\"question\": \"Can I get a loan to study medicine at Oxford University in the UK under PM-Vidyalaxmi?\"}"
  # Output: {"question": "...", "answer": "I don't know. The PM-Vidyalaxmi scheme and PM-USP CSIS only cover domestic higher education...", "citations": []}
  ```

---

## Day 8: RAG Configuration Benchmark & Winner Table

To optimize retrieval fidelity and prevent hallucinations, two distinct RAG configurations were evaluated across **15 realistic VidyaLoan queries** ([`eval/eval_set.json`](file:///c:/Users/TusharV/Desktop/vidyaloan/GenAi/eval/eval_set.json)):
- **Config A (Macro Chunking):** Chunk size = 700 chars, Overlap = 120 chars, Top-k = 3
- **Config B (Micro Chunking):** Chunk size = 350 chars, Overlap = 60 chars, Top-k = 5

### How to Run the Evaluation Harness
```bash
python eval/run_eval.py
```

### Benchmark Results & Winner Table

| Evaluation Metric | Config A (chunk=700, k=3) | Config B (chunk=350, k=5) | Winner |
| :--- | :---: | :---: | :---: |
| **Chunk Size / Overlap** | 700 / 120 chars | 350 / 60 chars | - |
| **Top-K Retrieved Chunks** | 3 | 5 | - |
| **Indexed Chunks Count** | 123 chunks | 254 chunks | - |
| **Context Hit Rate (Recall)** | 80.0% | **93.33%** | **Config B** |
| **Avg Context Relevance (Similarity)** | **0.6087** | 0.5905 | Config A |
| **Answer Correctness** | 81.11% | 81.11% | Tie |
| **Faithfulness / Grounding** | **100.0%** | **100.0%** | **Tie (100%)** |
| **Citation Precision** | **100.0%** | **100.0%** | **Tie (100%)** |
| **Q6 Refusal ("I don't know")** | **PASS** | **PASS** | **Tie (100% Pass)** |
| **Average Query Latency** | 582.37 ms | **542.05 ms** | **Config B** |
| **Composite Score** | 88.33% | **92.33%** | **Config B 🏆** |

> **🏆 Winner Decision:** **Config B** won the benchmark with a composite score of **92.33%**, driven by a **+13.33% higher context hit rate (93.33% vs 80.0%)** and lower query latency. Both configurations demonstrated 100% citation precision and strictly refused Question 6 with *"I don't know"*.

---

## Developer

**Tushar Sachin Vargude** | PRN: 2124UDSM2015 | Roll No.: 15  
Sanjivani University | Domain: Artificial Intelligence and Data Science  
