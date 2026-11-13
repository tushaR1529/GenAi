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
- **RESTful FastAPI Service:** Endpoints for health checks, record retrieval, TF-IDF smart search, user questions, and AI chat (`app/main.py`).
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
│   ├── cli.py                 # Command-line interface for browsing records
│   ├── explore.py             # Mirror for exploratory analysis
│   ├── fetch.py               # Fetches official government PDFs & HTML FAQs
│   ├── ingest.py              # Parses raw documents into structured Record dataclasses
│   ├── llm.py                 # Day 6: Groq/Gemini provider wrapper + JSON parser
│   ├── main.py                # FastAPI REST service (/health, /records, /search, /chat, etc.)
│   ├── models.py              # Record dataclass definition
│   ├── records.py             # Data loading, search, and lookup functions
│   └── smart_search.py        # TF-IDF vectorizer + Cosine similarity search engine
├── data/
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
│   └── prompt_compare.md      # Day 6: Comparison of Prompt v1 vs Prompt v2 across 10 questions
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
- `POST /questions`: Saves a user question into `data/questions.json`.
  ```bash
  curl -X POST http://127.0.0.1:8000/questions -H "Content-Type: application/json" -d "{\"question\": \"Can I get loan for diploma?\"}"
  ```
- `POST /chat` (Day 6): AI loan consultation returning structured JSON with answer, confidence, and follow-up.
  ```bash
  curl -X POST http://127.0.0.1:8000/chat -H "Content-Type: application/json" -d "{\"message\": \"Which loan I should apply for less than 5 lakh income?\", \"prompt_version\": \"v2\"}"
  ```

---

## Developer

**Tushar Sachin Vargude** | PRN: 2124UDSM2015 | Roll No.: 15  
Sanjivani University | Domain: Artificial Intelligence and Data Science  
