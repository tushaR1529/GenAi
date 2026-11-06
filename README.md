# VidyaLoan: AI-Powered Education Loan Assistance System

**Product:** VidyaLoan is an AI assistant that explains Indian government education loan schemes (PM-Vidyalaxmi, CSIS and CGFSEL) in simple language.

**User:** Students and parents, especially from families with income under Rs. 8 lakh, who need help understanding which education loan scheme applies to them.

**Problem:** Several overlapping schemes have different income limits, subsidies and guarantees. Families find it hard to know what they are eligible for, what the government will pay, and what the loan will really cost them.

**Data source:** PM-Vidyalaxmi Scheme Guidelines (education.gov.in) and the PM-Vidyalaxmi portal FAQ (pmvidyalaxmi.co.in).

## About

VidyaLoan helps Indian students understand government education loan schemes, eligibility criteria, interest subsidies and repayment options. It uses official government guidelines and FAQs as its data sources.

Planned features:
- A chatbot that gives context-aware answers using Large Language Models (LLMs), Retrieval-Augmented Generation (RAG), semantic search and Agentic AI
- An education loan eligibility checker
- A loan cost calculator with EMI estimation
- Government subsidy analysis
- An interactive loan cost breakdown chart

## Technologies

Python, FastAPI, Streamlit, Pandas, Sentence Transformers, ChromaDB, Groq/Gemini, LangGraph, Pytest and Docker.

## Project Structure

- day01_intro.py: prints the project card and asks for the user's name and question
- day01_menu.py: menu-driven program with a rule check
- data/sample_records.py: 20 hand-collected scheme records
- app/records.py: load, search, count and get-by-id functions
- app/cli.py: command-line menu for the records

## How to Run

python day01_intro.py
python day01_menu.py
python -m app.cli

## Developer

Tushar Sachin Vargude | PRN: 2124UDSM2015 | Roll No.: 38
Sanjivani University | Domain: Artificial Intelligence and Data Science

Project Status: Under Development
