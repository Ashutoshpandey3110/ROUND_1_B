"""
PDF Parser and Structural Analyzer

This module is responsible for ingesting PDF files, deconstructing them,
and analyzing their structure to identify headings and associated content.
It uses the PyMuPDF library for its high performance and detailed output.
"""

import fitz  # PyMuPDF
from pathlib import Path
from typing import List, Dict, Any, Tuple
from collections import Counter
import re

from . import config

# A simple internal data structure for holding processed section info
class DocumentSection:
    def __init__(self, title: str, start_page: int, doc_name: str):
        self.title = title
        self.start_page = start_page
        self.doc_name = doc_name
        self.content = ""

    def __repr__(self):
        return f"Section(title='{self.title}', page={self.start_page}, content_len={len(self.content)})"

def get_body_text_size(doc: fitz.Document) -> float:
    """
    Analyzes the entire document to find the most common font size,
    which is assumed to be the body text size.

    Args:
        doc (fitz.Document): The opened PyMuPDF document.

    Returns:
        float: The statistically determined size of the body text.
    """
    font_sizes = []
    for page in doc:
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        font_sizes.append(round(span["size"]))
    
    if not font_sizes:
        return 10.0 # A reasonable default

    # Use Counter to find the most frequent font size
    size_counts = Counter(font_sizes)
    return size_counts.most_common(1)[0][0]

def parse_document(doc_path: Path) -> List[DocumentSection]:
    """
    Parses a single PDF document, identifies its structure, and groups
    text content under the appropriate headings.

    Args:
        doc_path (Path): The path to the PDF file.

    Returns:
        List[DocumentSection]: A list of structured section objects.
    """
    doc = fitz.open(doc_path)
    body_size = get_body_text_size(doc)
    
    sections = []
    current_section = DocumentSection("Introduction", 1, doc_path.name)

    for page_num, page in enumerate(doc, start=1):
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if "lines" not in block or not block["lines"]:
                continue

            # Heuristic: Assume the first span's style represents the whole block
            first_span = block["lines"][0]["spans"][0]
            font_size = first_span["size"]
            is_bold = (first_span["flags"] & 16) != 0
            block_text = " ".join([line["spans"][0]["text"] for line in block["lines"]]).strip()

            if not block_text:
                continue

            # Heading classification logic
            is_h1 = font_size > body_size * config.H1_SIZE_MULTIPLIER and is_bold
            is_h2 = body_size * config.H2_SIZE_MULTIPLIER < font_size <= body_size * config.H1_SIZE_MULTIPLIER and is_bold

            if is_h1 or is_h2:
                # Save the previous section if it has content
                if current_section.content.strip():
                    sections.append(current_section)
                # Start a new section
                current_section = DocumentSection(block_text, page_num, doc_path.name)
            else:
                # Append content to the current section
                current_section.content += block_text + "\n"

    # Append the last section
    if current_section.content.strip():
        sections.append(current_section)

    return sections

def chunk_sections(sections: List[DocumentSection]) -> List[Dict[str, Any]]:
    """
    Takes structured sections and breaks their content down into smaller,
    semantically coherent chunks suitable for embedding.

    Args:
        sections (List[DocumentSection]): The list of sections from a document.

    Returns:
        List[Dict[str, Any]]: A list of chunk dictionaries, each containing
                              the text and its source metadata.
    """
    all_chunks = []
    for section in sections:
        # Simple word-based chunking
        words = section.content.split()
        for i in range(0, len(words), config.CHUNK_TARGET_WORD_COUNT):
            chunk_text = " ".join(words[i:i + config.CHUNK_TARGET_WORD_COUNT])
            if chunk_text.strip():
                all_chunks.append({
                    "text": chunk_text,
                    "doc_name": section.doc_name,
                    "page_number": section.start_page,
                    "section_title": section.title
                })
    return all_chunks
