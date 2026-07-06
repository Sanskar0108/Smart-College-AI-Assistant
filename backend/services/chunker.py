import re
from typing import List, Dict, Any

class DocumentChunker:
    """
    Splits document text into manageable study context chunks with overlapping boundaries.
    """
    @staticmethod
    def chunk_document(doc_id: str, filename: str, full_text: str) -> List[Dict[str, Any]]:
        """
        Groups document text page-by-page and segments paragraphs/sentences into overlapping chunks.
        Target size: 500-1000 characters per chunk, with 150 characters overlap.
        """
        # Split text into pages (supports explicit markers or fallback to virtual pages)
        if "\n\n--- PAGE_BREAK ---\n\n" in full_text:
            pages = full_text.split("\n\n--- PAGE_BREAK ---\n\n")
        else:
            # Fallback: split on common page dividers or virtual pages by word count (~1500 chars)
            divider_pattern = r'\n(?:---|===|___|Page \d+|\[Page \d+\])\n'
            raw_splits = re.split(divider_pattern, full_text)
            if len(raw_splits) > 1:
                pages = [p.strip() for p in raw_splits if p.strip()]
            else:
                pages = []
                paragraphs = full_text.split("\n\n")
                current_page_paras = []
                current_len = 0
                for para in paragraphs:
                    para_strip = para.strip()
                    if not para_strip:
                        continue
                    current_page_paras.append(para_strip)
                    current_len += len(para_strip)
                    if current_len >= 1500:
                        pages.append("\n\n".join(current_page_paras))
                        current_page_paras = []
                        current_len = 0
                if current_page_paras:
                    pages.append("\n\n".join(current_page_paras))
        
        chunks = []
        chunk_idx = 1

        for page_idx, page_text in enumerate(pages):
            page_number = page_idx + 1
            text_len = len(page_text)

            # If page text is empty, skip
            if not page_text.strip():
                continue

            # If the entire page is already small, keep it as a single chunk
            if text_len <= 1000:
                chunks.append({
                    "document_id": doc_id,
                    "chunk_id": f"{doc_id}-c{chunk_idx}",
                    "chunk_text": page_text.strip(),
                    "page_number": page_number,
                    "source_filename": filename
                })
                chunk_idx += 1
                continue

            # Segment page text using a sliding window
            start = 0
            while start < text_len:
                # Target end index
                end = min(start + 800, text_len)

                # Align boundaries with sentence end marks or word breaks
                if end < text_len:
                    # Look back 200 characters for a sentence terminator (., !, ?) followed by whitespace
                    boundary_match = re.search(r'(?<=[.!?])\s', page_text[end-200:end])
                    if boundary_match:
                        # Align to end of sentence
                        end = (end - 200) + boundary_match.start() + 1
                    else:
                        # Fall back to aligning with a word space
                        space_idx = page_text.rfind(' ', end-100, end)
                        if space_idx != -1:
                            end = space_idx

                chunk_txt = page_text[start:end].strip()
                if chunk_txt:
                    chunks.append({
                        "document_id": doc_id,
                        "chunk_id": f"{doc_id}-c{chunk_idx}",
                        "chunk_text": chunk_txt,
                        "page_number": page_number,
                        "source_filename": filename
                    })
                    chunk_idx += 1

                # Slide forward. Overlap size is 150 characters
                next_start = end - 150
                if next_start <= start:
                    start = end
                else:
                    start = next_start
                # Guard against infinite loops or tiny trailing chunks
                if start >= text_len - 100:
                    break

        return chunks
