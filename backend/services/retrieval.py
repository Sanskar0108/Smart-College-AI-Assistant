import re
import math
from typing import List, Dict, Any, Tuple

class LocalTfidfRetriever:
    """
    Lightweight, zero-dependency TF-IDF retrieval engine to rank document chunks by query relevance.
    """
    STOP_WORDS = {
        "the", "is", "at", "which", "on", "and", "a", "an", "of", "to", "in", 
        "for", "with", "that", "this", "these", "those", "it", "its", "they",
        "them", "their", "are", "was", "were", "be", "been", "being", "have",
        "has", "had", "do", "does", "did", "but", "by", "or", "as", "from",
        "how", "what", "why", "where", "who", "when", "can", "should", "explain"
    }

    def _tokenize_clean(self, text: str) -> List[str]:
        """
        Cleans punctuation and returns lowercase word tokens, filtering out stop-words.
        """
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        return [w for w in words if w not in self.STOP_WORDS]

    def retrieve_relevant_chunks(
        self, chunks: List[Dict[str, Any]], query: str, top_k: int = 3
    ) -> List[Tuple[Dict[str, Any], float]]:
        """
        Calculates TF-IDF relevance scores for each chunk against the query.
        Returns: List of tuples containing (chunk_dict, score) sorted descending.
        """
        query_tokens = self._tokenize_clean(query)
        if not query_tokens:
            # Fallback if query contains only stop words
            query_tokens = query.lower().split()

        total_chunks = len(chunks)
        if total_chunks == 0:
            return []

        # 1. Calculate Document Frequency (DF) for query terms
        df = {}
        for token in query_tokens:
            count = 0
            for chunk in chunks:
                text = chunk.get("chunk_text", "").lower()
                if token in text:
                    count += 1
            df[token] = count

        # 2. Score each chunk
        scored_chunks = []
        for chunk in chunks:
            chunk_text = chunk.get("chunk_text", "")
            chunk_tokens = self._tokenize_clean(chunk_text)
            
            if not chunk_tokens:
                continue

            score = 0.0
            total_terms = len(chunk_tokens)

            for token in query_tokens:
                # Term Frequency (TF)
                tf_count = chunk_tokens.count(token)
                tf = tf_count / total_terms

                # Inverse Document Frequency (IDF)
                # We use standard smoothed logarithmic IDF
                doc_freq = df.get(token, 0)
                idf = math.log(1.0 + (total_chunks / (1.0 + doc_freq)))

                # Accumulate TF-IDF term score
                score += tf * idf

            scored_chunks.append((chunk, score))

        # 3. Sort by relevance score descending
        scored_chunks.sort(key=lambda x: x[1], reverse=True)

        return scored_chunks[:top_k]

# Global retriever instance
retriever = LocalTfidfRetriever()
