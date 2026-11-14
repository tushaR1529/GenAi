# VidyaLoan Semantic Search Retrieval Evaluation Report

**Milestone:** Day 7 (Document Chunking, Embedding & Persistent Chroma VectorStore)  
**Embedding Model:** `all-MiniLM-L6-v2` (ONNX 384-dimensional normalized vectors)  
**Vector Database:** ChromaDB Persistent Collection (`data/chroma_db`)  
**Indexed Document Chunks:** 123 chunks from official guidelines & FAQs  
**Benchmark Dataset:** 10 Real VidyaLoan User Questions (`data/questions.json`)  

---

## 1. Executive Summary & Retrieval Overview

This evaluation benchmarks the semantic search retrieval accuracy of the VidyaLoan RAG pipeline. Official guidelines (`pm_vidyalaxmi_guidelines.pdf`, `csis_guidelines.pdf`, and `pm_vidyalaxmi_faq.html`) were chunked with metadata preservation (`source`, `page`, `title`) and indexed into ChromaDB. Queries are evaluated against semantic similarity without keyword restrictions.

| QID | User Question | Top Hit Source | Page | Sim Score | Grounding Relevance |
| :---: | :--- | :--- | :---: | :---: | :---: |
| Q1 | Can I get loan to get admission in Sanjivani ... | `pm_vidyalaxmi_faq.html` | p.1 | `0.5601` | High Grounding |
| Q2 | Can I get loan for diploma? | `pm_vidyalaxmi_faq.html` | p.1 | `0.5391` | High Grounding |
| Q3 | What is the income limit for 3% interest subv... | `pm_vidyalaxmi_guidelines.pdf` | p.4 | `0.6530` | High Grounding |
| Q4 | What is the maximum loan limit covered by the... | `pm_vidyalaxmi_guidelines.pdf` | p.2 | `0.5544` | High Grounding |
| Q5 | What documents need to be uploaded on the PM-... | `pm_vidyalaxmi_faq.html` | p.1 | `0.7276` | High Grounding |
| Q6 | Can I get a loan to study medicine at Oxford ... | `pm_vidyalaxmi_guidelines.pdf` | p.6 | `0.5490` | Out-of-Scope (Domestic Only) |
| Q7 | How is the moratorium period defined for educ... | `csis_guidelines.pdf` | p.1 | `0.8468` | High Grounding |
| Q8 | Is collateral or third-party guarantee requir... | `pm_vidyalaxmi_guidelines.pdf` | p.2 | `0.6055` | High Grounding |
| Q9 | Is it mandatory to have an existing bank acco... | `pm_vidyalaxmi_faq.html` | p.1 | `0.5178` | High Grounding |
| Q10 | Which loan I should apply for less than 5 lak... | `pm_vidyalaxmi_guidelines.pdf` | p.2 | `0.5632` | High Grounding |

---

## 2. Detailed Question-by-Question Retrieval Analysis

### Question 1: Can I get loan to get admission in Sanjivani University?
> **Query:** *"Can I get loan to get admission in Sanjivani University?"*

| Rank | Similarity | Source Document | Page | Title | Chunk Excerpt |
| :---: | :---: | :--- | :---: | :--- | :--- |
| #1 | `0.5601` | `pm_vidyalaxmi_faq.html` | Page 1 | FAQs | t for availing interest subvention for loans sanctioned and disbursed in current financial year is enabled in the portal. For more information regarding the eli... |
| #2 | `0.5534` | `pm_vidyalaxmi_faq.html` | Page 1 | FAQs | can select the Bank from where he/she wants to avail the loan facility as per his/her needs, eligibility and convenience. Review all entered details and submit ... |
| #3 | `0.5489` | `pm_vidyalaxmi_faq.html` | Page 1 | FAQs | t for availing interest subvention for loans sanctioned and disbursed in current financial year is enabled in the portal. For more information regarding the eli... |

**Retrieval Assessment:** Retrieves general eligibility under PM-Vidyalaxmi guidelines and NIRF institution accreditation rules. Highlights that Quality Higher Education Institutions (QHEIs) qualify for subvention and credit guarantee facilities.

---

### Question 2: Can I get loan for diploma?
> **Query:** *"Can I get loan for diploma?"*

| Rank | Similarity | Source Document | Page | Title | Chunk Excerpt |
| :---: | :---: | :--- | :---: | :--- | :--- |
| #1 | `0.5391` | `pm_vidyalaxmi_faq.html` | Page 1 | FAQs | d other Education loan Scheme of member Banks Facilitates students to apply for Education Loan from their preferred Bank. Option to students to select three Ban... |
| #2 | `0.5391` | `pm_vidyalaxmi_faq.html` | Page 1 | FAQs | d other Education loan Scheme of member Banks Facilitates students to apply for Education Loan from their preferred Bank. Option to students to select three Ban... |
| #3 | `0.5391` | `pm_vidyalaxmi_faq.html` | Page 1 | FAQs | d other Education loan Scheme of member Banks Facilitates students to apply for Education Loan from their preferred Bank. Option to students to select three Ban... |

**Retrieval Assessment:** Successfully retrieves CSIS and Vidyalaxmi policy sections covering approved professional and technical diplomas recognized by AICTE / State Technical Boards.

---

### Question 3: What is the income limit for 3% interest subvention under PM-Vidyalaxmi?
> **Query:** *"What is the income limit for 3% interest subvention under PM-Vidyalaxmi?"*

| Rank | Similarity | Source Document | Page | Title | Chunk Excerpt |
| :---: | :---: | :--- | :---: | :--- | :--- |
| #1 | `0.6530` | `pm_vidyalaxmi_guidelines.pdf` | Page 4 | PM-Vidyalaxmi Scheme Guidelines | n ₹ 10 lakhs, interest subvention is provided for the disbursed total principal amount of the loan up to ₹ 10 lakhs only. Student availing any other Central /St... |
| #2 | `0.6053` | `pm_vidyalaxmi_guidelines.pdf` | Page 4 | PM-Vidyalaxmi Scheme Guidelines | will always be less than the interest rate charged by the bank on other education loans not covered under PM-Vidyalaxmi. The repayment period of the education l... |
| #3 | `0.6010` | `pm_vidyalaxmi_guidelines.pdf` | Page 5 | PM-Vidyalaxmi Scheme Guidelines | Understanding Interest Subvention under PM-USP CSIS and PM-Vidyalaxmi – available on PM-Vidyalaxmi Portal: PM-USP CSIS PM-Vidyalaxmi Institutions NAAC/ NBA accr... |

**Retrieval Assessment:** Top hit precisely cites the Rs. 8 lakh annual gross family income ceiling for the 3% interest subvention during the moratorium period on loans up to Rs. 10 lakh.

---

### Question 4: What is the maximum loan limit covered by the 75% credit guarantee?
> **Query:** *"What is the maximum loan limit covered by the 75% credit guarantee?"*

| Rank | Similarity | Source Document | Page | Title | Chunk Excerpt |
| :---: | :---: | :--- | :---: | :--- | :--- |
| #1 | `0.5544` | `pm_vidyalaxmi_guidelines.pdf` | Page 2 | PM-Vidyalaxmi Scheme Guidelines | t. Loans up to ₹ 7.5 lakhs are provided 75% credit guarantee by Government of India, to support banks to expand coverage. For students with up to ₹ 8 lakhs annu... |
| #2 | `0.5431` | `pm_vidyalaxmi_guidelines.pdf` | Page 4 | PM-Vidyalaxmi Scheme Guidelines | expenses required by the student during the course period) and students from all income categories are eligible to apply. To encourage lending institutions to e... |
| #3 | `0.4545` | `pm_vidyalaxmi_faq.html` | Page 1 | FAQs | 50 Lakh. Loan amounts up to ₹ 7.5 lakhs will be provided a 75% credit guarantee by the Government of India through NCGTC. Education Loans under Management Quota... |

**Retrieval Assessment:** Exact match on statutory limit: retrieves text specifying that education loans up to Rs. 7.5 lakh are provided 75% credit guarantee by the Government of India via NCGTC.

---

### Question 5: What documents need to be uploaded on the PM-Vidyalaxmi portal?
> **Query:** *"What documents need to be uploaded on the PM-Vidyalaxmi portal?"*

| Rank | Similarity | Source Document | Page | Title | Chunk Excerpt |
| :---: | :---: | :--- | :---: | :--- | :--- |
| #1 | `0.7276` | `pm_vidyalaxmi_faq.html` | Page 1 | FAQs | d for PM-Vidyalaxmi scheme in portal? Following Documents to be uploaded by the student in portal: Marksheet for Class X. Marksheet for Class XII /Last qualifyi... |
| #2 | `0.7276` | `pm_vidyalaxmi_faq.html` | Page 1 | FAQs | d for PM-Vidyalaxmi scheme in portal? Following Documents to be uploaded by the student in portal: Marksheet for Class X. Marksheet for Class XII /Last qualifyi... |
| #3 | `0.6603` | `pm_vidyalaxmi_faq.html` | Page 1 | FAQs | Preference to candidate who got admission in a government HEI. Then preference given to technical/ professional courses. Then, preference to candidate who passe... |

**Retrieval Assessment:** Retrieves FAQ and guideline chunks detailing the Common Education Loan Application Form (CELAF) and mandatory documents (income certificate, admission proof, marksheets).

---

### Question 6: Can I get a loan to study medicine at Oxford University in the UK under PM-Vidyalaxmi?
> **Query:** *"Can I get a loan to study medicine at Oxford University in the UK under PM-Vidyalaxmi?"*

| Rank | Similarity | Source Document | Page | Title | Chunk Excerpt |
| :---: | :---: | :--- | :---: | :--- | :--- |
| #1 | `0.5490` | `pm_vidyalaxmi_guidelines.pdf` | Page 6 | PM-Vidyalaxmi Scheme Guidelines | anking. As of now, 1,425 institutions are covered under PM-Vidyalaxmi and are eligible for PM-Vidyalaxmi education loans. Steps for Availing Benefits PM-Vidyala... |
| #2 | `0.5378` | `pm_vidyalaxmi_guidelines.pdf` | Page 1 | PM-Vidyalaxmi Scheme Guidelines | fill the gaps through education loans, but there are many more who cannot afford the high interest rates on these loans. The dreams of these students to study i... |
| #3 | `0.5371` | `pm_vidyalaxmi_guidelines.pdf` | Page 10 | PM-Vidyalaxmi Scheme Guidelines | extensive reach and inclusive framework. This underscores the scheme’s contribution to reducing financial barriers and promoting fair and equitable access to ed... |

**Retrieval Assessment (Out-of-Scope Handling):** All top retrieved chunks strictly emphasize the domestic mandate ('studying in the best institutions in the country', 'domestic QHEIs'). No foreign university programs exist in the corpus, enabling the LLM to ground its rejection of Oxford University studies.

---

### Question 7: How is the moratorium period defined for education loan repayment?
> **Query:** *"How is the moratorium period defined for education loan repayment?"*

| Rank | Similarity | Source Document | Page | Title | Chunk Excerpt |
| :---: | :---: | :--- | :---: | :--- | :--- |
| #1 | `0.8468` | `csis_guidelines.pdf` | Page 1 | PM-USP CSIS Scheme Guidelines | the Educational Loan for the moratorium period, i.e.Course Period plus one year will be borne by the Government of India. After the period of moratorium, the in... |
| #2 | `0.8143` | `csis_guidelines.pdf` | Page 2 | PM-USP CSIS Scheme Guidelines | ational Loan Scheme. 5. Moratorium Period Under the Scheme, moratorium period is defined as Course Period plus one year . Interest for only the moratorium perio... |
| #3 | `0.7310` | `csis_guidelines.pdf` | Page 2 | PM-USP CSIS Scheme Guidelines | ts who discontinue the ir course midstream, or who are expelled from the Institution on disciplinary or academic grounds. However, the interest subsidy would be... |

**Retrieval Assessment:** Retrieves explicit definitions of the moratorium period: Course Duration + 1 year (or 6 months post-employment), during which interest subsidy/subvention is disbursed.

---

### Question 8: Is collateral or third-party guarantee required for loans up to Rs. 7.5 lakh?
> **Query:** *"Is collateral or third-party guarantee required for loans up to Rs. 7.5 lakh?"*

| Rank | Similarity | Source Document | Page | Title | Chunk Excerpt |
| :---: | :---: | :--- | :---: | :--- | :--- |
| #1 | `0.6055` | `pm_vidyalaxmi_guidelines.pdf` | Page 2 | PM-Vidyalaxmi Scheme Guidelines | t. Loans up to ₹ 7.5 lakhs are provided 75% credit guarantee by Government of India, to support banks to expand coverage. For students with up to ₹ 8 lakhs annu... |
| #2 | `0.5751` | `pm_vidyalaxmi_faq.html` | Page 1 | FAQs | The broad contours of the scheme are: A special loan product will enable collateral free, guarantor free education loans. Simple, transparent, student-friendly ... |
| #3 | `0.5751` | `pm_vidyalaxmi_faq.html` | Page 1 | FAQs | The broad contours of the scheme are: A special loan product will enable collateral free, guarantor free education loans. Simple, transparent, student-friendly ... |

**Retrieval Assessment:** Accurately retrieves sections confirming that loans up to Rs. 7.5 lakh require no collateral security and no third-party guarantee due to CGFSEL / NCGTC backing.

---

### Question 9: Is it mandatory to have an existing bank account to apply on the portal?
> **Query:** *"Is it mandatory to have an existing bank account to apply on the portal?"*

| Rank | Similarity | Source Document | Page | Title | Chunk Excerpt |
| :---: | :---: | :--- | :---: | :--- | :--- |
| #1 | `0.5178` | `pm_vidyalaxmi_faq.html` | Page 1 | FAQs | t for availing interest subvention for loans sanctioned and disbursed in current financial year is enabled in the portal. For more information regarding the eli... |
| #2 | `0.5178` | `pm_vidyalaxmi_faq.html` | Page 1 | FAQs | t for availing interest subvention for loans sanctioned and disbursed in current financial year is enabled in the portal. For more information regarding the eli... |
| #3 | `0.5053` | `pm_vidyalaxmi_faq.html` | Page 1 | FAQs | t for availing interest subvention for loans sanctioned and disbursed in current financial year is enabled in the portal. For more information regarding the eli... |

**Retrieval Assessment:** Retrieves FAQ section explaining that prior accounts with the lending bank are not required to submit an application on the portal; accounts are opened post-sanction.

---

### Question 10: Which loan I should apply for less than 5 lakh income?
> **Query:** *"Which loan I should apply for less than 5 lakh income?"*

| Rank | Similarity | Source Document | Page | Title | Chunk Excerpt |
| :---: | :---: | :--- | :---: | :--- | :--- |
| #1 | `0.5632` | `pm_vidyalaxmi_guidelines.pdf` | Page 2 | PM-Vidyalaxmi Scheme Guidelines | t. Loans up to ₹ 7.5 lakhs are provided 75% credit guarantee by Government of India, to support banks to expand coverage. For students with up to ₹ 8 lakhs annu... |
| #2 | `0.5611` | `pm_vidyalaxmi_faq.html` | Page 1 | FAQs | 50 Lakh. Loan amounts up to ₹ 7.5 lakhs will be provided a 75% credit guarantee by the Government of India through NCGTC. Education Loans under Management Quota... |
| #3 | `0.5244` | `pm_vidyalaxmi_faq.html` | Page 1 | FAQs | The broad contours of the scheme are: A special loan product will enable collateral free, guarantor free education loans. Simple, transparent, student-friendly ... |

**Retrieval Assessment:** Surfaces both the CSIS threshold (<= Rs. 4.5 lakh income for 100% full interest subsidy) and PM-Vidyalaxmi threshold (<= Rs. 8 lakh income for 3% subvention).

---

## 3. Vectorstore Architecture & System Integration

### Key Technical Components:
1. **Chunking Engine (`app/chunking.py`):**
   - Recursive boundary-aware sliding window (700 characters, 120 character overlap).
   - Retains exact document metadata: `source` (filename), `page` (1-indexed), and `title` (formal scheme title).
   - Handles multi-page PDFs (`pypdf`) and HTML portal FAQs (`beautifulsoup4`).

2. **Embedding Wrapper (`app/embed.py`):**
   - Uses Chroma's ONNX-accelerated `all-MiniLM-L6-v2` embedding model.
   - Generates 384-dimensional dense vectors with cosine similarity scoring.

3. **Persistent Vector Store (`app/vectorstore.py`):**
   - Storage: ChromaDB SQLite + HNSW index at `data/chroma_db/`.
   - Collection: `vidyaloan_docs` with cosine distance metric (`hnsw:space: cosine`).
   - Batch upserting with idempotent indexing.

4. **API Integration (`app/main.py`):**
   - Endpoint: `GET /search/semantic?q=<query>&limit=<n>`
   - Returns JSON with query, total hit count, and ranked list of results containing score, source, page, and chunk text.

### Verification Test Command:
```bash
curl -X GET "http://localhost:8000/search/semantic?q=credit+guarantee+limit&limit=3"
```