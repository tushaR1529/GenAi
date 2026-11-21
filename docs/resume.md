# VidyaLoan Engineering Experience & Resume Bullets

Quantified, high-impact resume bullet points highlighting system design, full-stack development, agentic workflows, RAG architecture, performance optimization, and CI/CD deployment for the VidyaLoan platform.

---

## 3 Engineering-Grade Resume Bullets

- **Architected End-to-End RAG & Stateful Multi-Agent System:**
  Engineered a production-grade AI loan advisory platform using **FastAPI**, **LangGraph (StateGraph + MemorySaver)**, and persistent **ChromaDB**, indexing 59+ official policy documents (PM-Vidyalaxmi, PM-USP CSIS, CGFSEL) across 152 vectorized chunks; achieved **93.3% context recall** and **100% citation precision** with strict out-of-scope refusal guardrails to eliminate financial hallucinations.

- **Engineered Low-Latency Caching, Observability & Adversarial Guardrails:**
  Designed an in-memory **LRU query cache** cutting p95 response latency by **98% (from 450ms to 2.1ms)** with **0 tokens consumed on cache hits**, integrated real-time token consumption telemetry and structured JSONL logging, and deployed multi-layered guardrails enforcing input boundary limits (3–500 chars) and deterministic regex/heuristic detection against adversarial prompt-injection and jailbreak attacks.

- **Built Full-Stack Financial Simulator, Containerization & Automated CI/CD:**
  Developed an interactive **Streamlit** web application with dynamic Plotly stacked-bar visualizers computing compound moratorium interest, 100% central sector interest subsidies, and post-moratorium EMIs; containerized the microservices architecture using **Docker & Docker Compose**, configured a robust **GitHub Actions CI** pipeline (Ruff linting, 34 automated unit tests, container builds), and deployed to **Render** with 100% public `/health` uptime.

---

## Technical Skills Demonstrated

- **Languages & Frameworks:** Python 3.11+, FastAPI, Streamlit, Pydantic, Uvicorn, LangGraph, LangChain, PyTest, Ruff
- **Generative AI & Search:** Retrieval-Augmented Generation (RAG), ChromaDB, ONNX all-MiniLM-L6-v2 embeddings, TF-IDF + Cosine Similarity, Groq Llama-3.3-70B, Google Gemini 1.5 Flash, Prompt Engineering & Jailbreak Defense
- **System Design & Observability:** LRU Caching, Request Latency Profiling (p50/p90/p95), Token Estimation & Usage Logging, Human-in-the-Loop Approval Gates
- **DevOps & Cloud Deployment:** Docker, Docker Compose, GitHub Actions CI/CD, Render Cloud Platform, Linux/Windows hermetic testing
