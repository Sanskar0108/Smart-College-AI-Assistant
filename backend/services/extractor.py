import os
import traceback
from typing import Tuple

# Try importing multiple PDF extraction engines for maximum quality
PYMUPDF_AVAILABLE = False
try:
    import fitz # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    pass

PDFPLUMBER_AVAILABLE = False
try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    pass

PYPDF_AVAILABLE = False
try:
    import pypdf
    PYPDF_AVAILABLE = True
except ImportError:
    pass

import re

class DocumentExtractor:
    """
    Parses plain text (.txt) and PDF (.pdf) study materials.
    """
    @staticmethod
    def extract_text(file_path: str, file_extension: str) -> Tuple[str, int, str]:
        """
        Extracts raw text content, counts pages, and generates a preview snippet.
        Returns: Tuple[extracted_text, page_count, preview_snippet]
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found at: {file_path}")

        file_extension = file_extension.lower().strip('.')
        extracted_text = ""
        page_count = 1

        if file_extension == "txt":
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    extracted_text = f.read()
                
                # Compute virtual page count to match chunker boundaries
                if "\n\n--- PAGE_BREAK ---\n\n" in extracted_text:
                    page_count = len(extracted_text.split("\n\n--- PAGE_BREAK ---\n\n"))
                else:
                    divider_pattern = r'\n(?:---|===|___|Page \d+|\[Page \d+\])\n'
                    raw_splits = re.split(divider_pattern, extracted_text)
                    if len(raw_splits) > 1:
                        page_count = len([p.strip() for p in raw_splits if p.strip()])
                    else:
                        paragraphs = extracted_text.split("\n\n")
                        current_len = 0
                        pages_list = []
                        current_page = []
                        for para in paragraphs:
                            para_strip = para.strip()
                            if not para_strip:
                                continue
                            current_page.append(para_strip)
                            current_len += len(para_strip)
                            if current_len >= 1500:
                                pages_list.append(current_page)
                                current_page = []
                                current_len = 0
                        if current_page:
                            pages_list.append(current_page)
                        page_count = max(1, len(pages_list))
            except Exception as e:
                print(f"[ERROR] Failed to read TXT: {e}")
                raise ValueError(f"Failed to read text file: {str(e)}")

        elif file_extension == "pdf":
            # Engine 1: PyMuPDF (fitz) - Best quality
            if PYMUPDF_AVAILABLE:
                try:
                    print("[DEBUG] Attempting PDF text extraction using PyMuPDF (fitz)...")
                    doc = fitz.open(file_path)
                    page_count = len(doc)
                    text_pages = []
                    for page in doc:
                        # Extract blocks: (x0, y0, x1, y1, "text", block_no, block_type)
                        blocks = page.get_text("blocks")
                        # Filter to only keep text blocks
                        text_blocks = [b for b in blocks if b[6] == 0]
                        
                        width = page.rect.width
                        # Helper to classify columns and sort
                        def get_block_sort_key(b):
                            x0, y0, x1, y1, text, b_no, b_type = b
                            # Spans across middle (wider than 60% of page)
                            if x0 < width * 0.45 and x1 > width * 0.55:
                                col = 0
                            elif x1 <= width * 0.55:
                                col = 1
                            else:
                                col = 2
                            # Round y0 coordinate to group lines vertically within minor alignments
                            return (col, round(y0 / 3) * 3, x0)
                        
                        text_blocks.sort(key=get_block_sort_key)
                        page_text = "\n".join([b[4] for b in text_blocks])
                        if page_text:
                            text_pages.append(page_text)
                    extracted_text = "\n\n--- PAGE_BREAK ---\n\n".join(text_pages)
                except Exception as e:
                    print(f"[WARNING] PyMuPDF extraction failed: {e}")
                    traceback.print_exc()
            
            # Engine 2: pdfplumber - Structured fallback
            if not extracted_text.strip() and PDFPLUMBER_AVAILABLE:
                try:
                    print("[DEBUG] Attempting PDF text extraction using pdfplumber...")
                    with pdfplumber.open(file_path) as pdf:
                        page_count = len(pdf.pages)
                        text_pages = []
                        for page in pdf.pages:
                            page_text = page.extract_text()
                            if page_text:
                                text_pages.append(page_text)
                        extracted_text = "\n\n--- PAGE_BREAK ---\n\n".join(text_pages)
                except Exception as e:
                    print(f"[WARNING] pdfplumber extraction failed: {e}")
                    traceback.print_exc()

            # Engine 3: pypdf - Baseline fallback
            if not extracted_text.strip() and PYPDF_AVAILABLE:
                try:
                    print("[DEBUG] Attempting PDF text extraction using pypdf...")
                    reader = pypdf.PdfReader(file_path)
                    page_count = len(reader.pages)
                    text_pages = []
                    for page in reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text_pages.append(page_text)
                    extracted_text = "\n\n--- PAGE_BREAK ---\n\n".join(text_pages)
                except Exception as e:
                    print(f"[ERROR] pypdf extraction failed: {e}")
                    traceback.print_exc()
                    raise ValueError(f"Failed to parse PDF document structure: {str(e)}")

            if not extracted_text.strip():
                if not (PYMUPDF_AVAILABLE or PDFPLUMBER_AVAILABLE or PYPDF_AVAILABLE):
                    raise ImportError("No PDF extraction libraries (PyMuPDF, pdfplumber, pypdf) are installed on the system.")
                raise ValueError("PDF document extraction returned no text. It might be scanned/image-only or password protected.")
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")

        # Post-extraction validation
        cleaned_text = extracted_text.strip()
        if not cleaned_text:
            raise ValueError(
                "Document text extraction returned no content. "
                "The file may be empty or contain only scanned images/handwritten notes without OCR text."
            )

        # Generate preview snippet
        preview_snippet = cleaned_text[:200]
        if len(cleaned_text) > 200:
            preview_snippet += "..."

        return cleaned_text, page_count, preview_snippet
