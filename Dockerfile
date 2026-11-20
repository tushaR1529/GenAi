# VidyaLoan Multi-Service Dockerfile (Python 3.11)
FROM python:3.11-slim

# Prevent Python from writing .pyc files and buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Python dependencies first for caching
COPY requirements.txt /app/
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy application source code and data assets
COPY app/ /app/app/
COPY data/ /app/data/
COPY prompts/ /app/prompts/
COPY ui/ /app/ui/
COPY tests/ /app/tests/
COPY pyproject.toml /app/
COPY run_app.py /app/
COPY README.md /app/

# Expose FastAPI backend (8000) and Streamlit frontend (8501)
EXPOSE 8000 8501

ENV PORT=8000

# Default command starts the unified server running Streamlit UI at / with FastAPI /health
CMD ["sh", "-c", "python run_app.py"]
