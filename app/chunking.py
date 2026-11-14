# app/chunking.py
"""
Document chunking module for VidyaLoan documents.
Chunks PDF and HTML documents while preserving source, page, and title metadata.
"""
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from bs4 import BeautifulSoup
from pypdf import PdfReader


@dataclass
class DocumentChunk:
    id: str
    text: str
    source: str
    page: int
    title: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def split_text_into_chunks(
    text: str,
    chunk_size: int = 700,
    overlap: int = 120,
) -> List[str]:
    """Split text into overlapping windows respecting paragraph and sentence boundaries."""
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    if len(text) <= chunk_size:
        return [text]

    chunks: List[str] = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        if end >= len(text):
            chunk = text[start:].strip()
            if chunk:
                chunks.append(chunk)
            break

        # Look for sentence boundary near end
        split_pos = text.rfind(". ", start + chunk_size // 2, end)
        if split_pos == -1:
            split_pos = text.rfind(" ", start + chunk_size // 2, end)
        if split_pos == -1 or split_pos <= start:
            split_pos = end

        chunk = text[start:split_pos].strip()
        if chunk:
            chunks.append(chunk)
        start = max(start + 1, split_pos - overlap)

    return chunks


def extract_chunks_from_pdf(
    pdf_path: Path,
    title: Optional[str] = None,
    chunk_size: int = 700,
    overlap: int = 120,
) -> List[DocumentChunk]:
    """Extract page-by-page text from a PDF file and chunk it preserving page metadata."""
    if not pdf_path.exists():
        return []

    doc_title = title or pdf_path.stem.replace("_", " ").title()
    chunks: List[DocumentChunk] = []
    reader = PdfReader(str(pdf_path))

    for page_idx, page in enumerate(reader.pages):
        page_num = page_idx + 1
        raw_text = page.extract_text() or ""
        clean_page_text = re.sub(r"\s+", " ", raw_text).strip()
        if not clean_page_text:
            continue

        text_chunks = split_text_into_chunks(clean_page_text, chunk_size=chunk_size, overlap=overlap)
        for chunk_idx, chunk_text in enumerate(text_chunks):
            chunk_id = f"{pdf_path.stem}_p{page_num}_c{chunk_idx+1}"
            chunks.append(
                DocumentChunk(
                    id=chunk_id,
                    text=chunk_text,
                    source=pdf_path.name,
                    page=page_num,
                    title=doc_title,
                )
            )

    return chunks


def extract_chunks_from_html(
    html_path: Path,
    title: Optional[str] = None,
    chunk_size: int = 700,
    overlap: int = 120,
) -> List[DocumentChunk]:
    """Extract text from an HTML document (e.g. FAQ) and chunk preserving metadata."""
    if not html_path.exists():
        return []

    doc_title = title or html_path.stem.replace("_", " ").title()
    soup = BeautifulSoup(html_path.read_text(encoding="utf-8", errors="ignore"), "html.parser")

    # If title tag is present, use it
    if soup.title and soup.title.string:
        doc_title = soup.title.string.strip()

    # Find question/answer pairs or headings
    qa_blocks = soup.find_all(["div", "section", "p", "li", "h2", "h3"])
    extracted_texts: List[str] = []
    for el in qa_blocks:
        t = el.get_text(separator=" ", strip=True)
        if len(t) > 30 and t not in extracted_texts:
            extracted_texts.append(t)

    combined_text = "\n\n".join(extracted_texts)
    if not combined_text:
        combined_text = soup.get_text(separator=" ", strip=True)

    text_chunks = split_text_into_chunks(combined_text, chunk_size=chunk_size, overlap=overlap)
    chunks: List[DocumentChunk] = []
    for chunk_idx, chunk_text in enumerate(text_chunks):
        chunk_id = f"{html_path.stem}_p1_c{chunk_idx+1}"
        chunks.append(
            DocumentChunk(
                id=chunk_id,
                text=chunk_text,
                source=html_path.name,
                page=1,
                title=doc_title,
            )
        )

    return chunks


def chunk_all_documents(
    raw_dir: Optional[Path] = None,
    chunk_size: int = 700,
    overlap: int = 120,
) -> List[DocumentChunk]:
    """Chunk all VidyaLoan documents in data/raw."""
    base_dir = raw_dir or Path(__file__).resolve().parent.parent / "data" / "raw"
    all_chunks: List[DocumentChunk] = []

    # Map of known files to friendly titles
    title_map = {
        "pm_vidyalaxmi_guidelines.pdf": "PM-Vidyalaxmi Scheme Guidelines",
        "csis_guidelines.pdf": "PM-USP CSIS Scheme Guidelines",
        "pm_vidyalaxmi_faq.html": "PM-Vidyalaxmi Portal Official FAQs",
    }

    if not base_dir.exists():
        return all_chunks

    for file_path in sorted(base_dir.iterdir()):
        title = title_map.get(file_path.name, file_path.stem.replace("_", " ").title())
        if file_path.suffix.lower() == ".pdf":
            pdf_chunks = extract_chunks_from_pdf(
                file_path, title=title, chunk_size=chunk_size, overlap=overlap
            )
            all_chunks.extend(pdf_chunks)
        elif file_path.suffix.lower() in [".html", ".htm"]:
            html_chunks = extract_chunks_from_html(
                file_path, title=title, chunk_size=chunk_size, overlap=overlap
            )
            all_chunks.extend(html_chunks)

    return all_chunks


if __name__ == "__main__":
    chunks = chunk_all_documents()
    print(f"Total chunks generated: {len(chunks)}")
    for i in range(min(3, len(chunks))):
        c = chunks[i]
        print(f"\n--- Chunk {c.id} (Source: {c.source}, Page: {c.page}, Title: {c.title}) ---")
        print(c.text[:200] + "...")

