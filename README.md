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
- **RESTful FastAPI Service:** Endpoints for health checks, record retrieval, TF-IDF smart search, and logging user queries (`app/main.py`).
- **Exploratory Data Analysis:** Fast pandas-based dataset profiling computing distribution across schemes, categories, and income limits (`analysis/explore.py`).
- **Interactive CLI & Exploration:** Command-line interface for searching and inspecting scheme records (`app/cli.py`).

---

## Technologies

- **Backend & API:** Python 3.11+, FastAPI, Uvicorn, Pydantic
- **Data & Text Processing:** Pandas, Scikit-learn (TF-IDF), PyPDF, BeautifulSoup4, Requests
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
│   ├── main.py                # FastAPI REST service (/health, /records, /search, /questions)
│   ├── models.py              # Record dataclass definition
│   ├── records.py             # Data loading, search, and lookup functions
│   └── smart_search.py        # TF-IDF vectorizer + Cosine similarity search engine
├── data/
│   ├── raw/                   # Downloaded government guidelines and FAQs
│   │   ├── csis_guidelines.pdf
│   │   ├── pm_vidyalaxmi_faq.html
│   │   └── pm_vidyalaxmi_guidelines.pdf
│   ├── questions.json         # User questions submitted via POST /questions
│   ├── records.json           # Ingested scheme records (59+ structured entries)
│   └── sample_records.py      # Baseline seed records
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

### 2. Fetch Government Documents (Day 3)
Downloads official PM-Vidyalaxmi guidelines, PM-USP CSIS guidelines, and portal FAQs with timeouts and SSL handling:
```bash
python -m app.fetch
```

### 3. Ingest Documents into Structured Records (Day 3)
Extracts and normalizes scheme records into `data/records.json`:
```bash
python -m app.ingest
```

### 4. Run Exploratory Analysis (Day 4)
Prints 3 key dataset facts using Pandas:
```bash
python analysis/explore.py
```

### 5. Launch FastAPI Service (Day 4)
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
  curl -X POST http://127.0.0.1:8000/questions -H "Content-Type: application/json" -d "{\"question\": \"What is the moratorium period for PM-Vidyalaxmi?\"}"
  ```

### 6. Interactive Command-Line Tool
```bash
python -m app.cli
```

---

## Developer

**Tushar Sachin Vargude** | PRN: 2124UDSM2015 | Roll No.: 15
Sanjivani University | Domain: Artificial Intelligence and Data Science  
