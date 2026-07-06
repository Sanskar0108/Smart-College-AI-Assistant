import os
import re
import datetime
import random
import urllib.request
import json
from typing import List, Dict, Optional, Tuple, Any
from backend.services.retrieval import retriever
from backend.services.storage import db

class BaseAIService:
    """
    Abstract Base Class defining the AI Capabilities contract.
    """
    def generate_chat_answer(self, doc_name: str, doc_chunks: List[Dict[str, Any]], question: str) -> Dict[str, Any]:
        raise NotImplementedError()

    def generate_flashcards(self, doc_name: str, doc_chunks: List[Dict[str, Any]], count: int) -> List[Dict[str, Any]]:
        raise NotImplementedError()

    def generate_quiz(self, doc_name: str, doc_chunks: List[Dict[str, Any]], count: int) -> List[Dict[str, Any]]:
        raise NotImplementedError()


class LocalHeuristicAIService(BaseAIService):
    """
    Offline local NLP service that leverages TF-IDF chunk retrieval to
    construct strictly grounded answers, flashcards, and quizzes.
    """
    
    def classify_intent(self, question: str) -> str:
        q_low = re.sub(r'[^\w\s]', '', question.lower()).strip()
        words = set(q_low.split())
        
        # 1. Summary intent
        summary_keywords = {"summary", "summarize", "outline"}
        if len(words & summary_keywords) > 0:
            return "summary"
            
        # 2. Overview/Document description intent
        overview_keywords = {"about", "overview", "explain the document", "what is this document", "what is this pdf", "main topic"}
        if len(words & overview_keywords) > 0 or "what is this" in q_low or "what is it about" in q_low:
            return "overview"
            
        # 3. Flashcards request intent (inside chat)
        flashcard_keywords = {"flashcard", "flashcards", "study card", "study cards"}
        if len(words & flashcard_keywords) > 0:
            return "flashcards"
            
        # 4. Quiz request intent (inside chat)
        quiz_keywords = {"quiz", "practice quiz", "mcq", "mcqs", "question paper"}
        if len(words & quiz_keywords) > 0:
            return "quiz"
            
        # 5. Default is concept question
        return "concept"

    def post_process_cleanup(self, text: str) -> str:
        # Remove repeated opening phrases
        text = re.sub(r'^(?:Based on your notes in [^:]+:\s*|According to the notes,\s*|As stated on page \d+ of the notes:\s*)', '', text, flags=re.IGNORECASE)
        # Remove generic filler
        text = re.sub(r'In these notes, you will learn about the foundational concepts of [^.]+\.', '', text, flags=re.IGNORECASE)
        text = re.sub(r'You can ask specific doubt questions to dive deeper into any of these concepts\.', '', text, flags=re.IGNORECASE)
        
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Trim to clean sentence boundary if too long (max 500 chars)
        if len(text) > 500:
            sentences = re.split(r'(?<=[.!?])\s+', text)
            trimmed = ""
            for s in sentences:
                if len(trimmed) + len(s) + 1 <= 500:
                    trimmed += s + " "
                else:
                    break
            text = trimmed.strip()
            
        return text

    def generate_chat_answer(self, doc_name: str, doc_chunks: List[Dict[str, Any]], question: str) -> Dict[str, Any]:
        now = datetime.datetime.now()
        time_str = now.strftime("%I:%M %p")

        if not doc_chunks:
            return {
                "sender": "assistant",
                "text": "I could not find a confident answer in the uploaded notes (document is empty).",
                "time": time_str,
                "citation": None,
                "source_excerpt": None,
                "source_page": None
            }

        intent = self.classify_intent(question)

        # 1. Flashcards intent
        if intent == "flashcards":
            return {
                "sender": "assistant",
                "text": 'You can generate and study flashcards for this document using the dedicated "Flashcards" tab in the left sidebar.',
                "time": time_str,
                "citation": None,
                "source_excerpt": None,
                "source_page": None
            }

        # 2. Quiz intent
        if intent == "quiz":
            return {
                "sender": "assistant",
                "text": 'You can generate and take interactive practice quizzes for this document using the dedicated "Practice Quiz" tab in the left sidebar.',
                "time": time_str,
                "citation": None,
                "source_excerpt": None,
                "source_page": None
            }

        # 3. Summary intent
        if intent == "summary":
            bullets = []
            seen = set()
            for chunk in doc_chunks:
                lines = [l.strip() for l in chunk["chunk_text"].split("\n") if l.strip()]
                for line in lines:
                    if line.startswith("#"):
                        topic = line.replace("#", "").strip()
                        topic_clean = re.sub(r'[^\w\s]', '', topic).lower()
                        if topic_clean not in seen and len(topic) > 3:
                            seen.add(topic_clean)
                            sentences = [s.strip() for s in re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s|\n+', chunk["chunk_text"]) if len(s.strip()) > 10 and not s.startswith("#")]
                            desc = sentences[0] if sentences else "Key topic covered in the material."
                            if not desc.endswith((".", "!", "?")):
                                desc += "."
                            bullets.append(f"- **{topic}**: {desc}")
                            break
            
            bullets = bullets[:4]
            if bullets:
                summary_text = f"Structured summary of **{doc_name}**:\n" + "\n".join(bullets)
            else:
                sentences = [s.strip() for s in re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s|\n+', doc_chunks[0]["chunk_text"]) if len(s.strip()) > 10]
                intro_sentences = [s for s in sentences if not s.startswith("#")][:3]
                intro = " ".join(intro_sentences)
                if not intro.endswith((".", "!", "?")):
                    intro += "."
                summary_text = f"Structured summary of **{doc_name}**:\n- {intro}"

            return {
                "sender": "assistant",
                "text": summary_text,
                "time": time_str,
                "citation": f"Summary ({doc_name})",
                "source_excerpt": doc_chunks[0]["chunk_text"][:300],
                "source_page": doc_chunks[0]["page_number"]
            }

        # 4. Overview intent
        if intent == "overview":
            full_text = "\n".join([chunk["chunk_text"] for chunk in doc_chunks])
            lines = [l.strip() for l in full_text.split("\n") if l.strip()]
            title = doc_name
            if lines:
                title = re.sub(r'^#+\s*', '', lines[0]).strip()
                if len(title) > 60:
                    title = title[:57] + "..."
            
            overview_text = f"This document, **{doc_name}**, covers the topic of **{title}**. It outlines the core principles and concepts discussed in these study notes."
            return {
                "sender": "assistant",
                "text": overview_text,
                "time": time_str,
                "citation": f"Overview ({doc_name})",
                "source_excerpt": doc_chunks[0]["chunk_text"][:300],
                "source_page": doc_chunks[0]["page_number"]
            }

        # 5. Concept question intent (fallback default)
        scored = retriever.retrieve_relevant_chunks(doc_chunks, question, top_k=3)
        valid_matches = [item for item in scored if item[1] > 0.0]

        if not valid_matches:
            return {
                "sender": "assistant",
                "text": "I could not find a confident answer in the uploaded notes.",
                "time": time_str,
                "citation": None,
                "source_excerpt": None,
                "source_page": None
            }

        top_chunk, top_score = valid_matches[0]
        top_text = top_chunk["chunk_text"]
        top_page = top_chunk["page_number"]

        sentences = [s.strip() for s in re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s|\n+', top_text) if len(s.strip()) > 10]
        
        query_words = [w.lower() for w in re.sub(r'[^\w\s]', '', question).split() if len(w) > 2 and w.lower() not in retriever.STOP_WORDS]
        
        matching_sentences = []
        for s in sentences:
            if s.startswith("#") or (s.isupper() and len(s) < 30):
                continue
            s_low = s.lower()
            matches = sum(1 for w in query_words if w in s_low)
            if matches > 0:
                matching_sentences.append(s)

        if matching_sentences:
            response_text = " ".join(matching_sentences[:3])
        else:
            non_heading_sents = [s for s in sentences if not s.startswith("#") and not (s.isupper() and len(s) < 30)]
            response_text = " ".join(non_heading_sents[:2]) if non_heading_sents else top_text[:250]

        response_text = self.post_process_cleanup(response_text)
        citation = f"Page {top_page} ({doc_name})"

        return {
            "sender": "assistant",
            "text": response_text,
            "time": time_str,
            "citation": citation,
            "source_excerpt": top_text,
            "source_page": top_page
        }

    def generate_flashcards(self, doc_name: str, doc_chunks: List[Dict[str, Any]], count: int) -> List[Dict[str, Any]]:
        flashcards = []
        patterns = [
            r'\*\*(.*?)\*\*:\s*(.*?)(?=\.|\n|$)',
            r'([a-zA-Z\s]{3,20})\s+is\s+defined\s+as\s+(.*?)(?=\.|\n|$)',
            r'([a-zA-Z\s]{3,20})\s+refers\s+to\s+(.*?)(?=\.|\n|$)',
            r'([a-zA-Z\s]{3,20})\s+is\s+a\s+(.*?)(?=\.|\n|$)'
        ]

        found_pairs = []
        for chunk in doc_chunks:
            chunk_text = chunk["chunk_text"]
            page = chunk["page_number"]
            for pattern in patterns:
                matches = re.findall(pattern, chunk_text, re.IGNORECASE)
                for match in matches:
                    term, definition = match[0].strip(), match[1].strip()
                    if len(term) > 30 or len(definition) < 10 or term.lower() in retriever.STOP_WORDS:
                        continue
                    found_pairs.append((term, definition, page))

        unique_pairs = []
        seen = set()
        for term, definition, page in found_pairs:
            t_low = term.lower()
            if t_low not in seen:
                seen.add(t_low)
                unique_pairs.append((term, definition, page))

        for idx, (term, definition, page) in enumerate(unique_pairs[:count]):
            definition_cap = definition[0].upper() + definition[1:] if definition else ""
            flashcards.append({
                "id": f"fc-chunked-{idx+1}",
                "question": f"What is the definition of '{term}' according to page {page}?",
                "answer": f"{definition_cap}.",
                "source_reference": f"Page {page} ({doc_name})"
            })

        if len(flashcards) < count:
            if not doc_chunks:
                raise ValueError("Cannot generate flashcards from empty study material.")
            for idx in range(len(flashcards), count):
                chunk = doc_chunks[idx % len(doc_chunks)]
                sentences = [s.strip() for s in re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', chunk["chunk_text"]) if s.strip()]
                sent_idx = idx % len(sentences) if sentences else 0
                sent = sentences[sent_idx] if sentences else "Refer to the main overview sections of the notes."
                
                flashcards.append({
                    "id": f"fc-chunked-{idx+1}",
                    "question": f"Explain the context of this key statement from page {chunk['page_number']}: '{sent[:60]}...'",
                    "answer": f"Details: '{chunk['chunk_text'][:160]}...'",
                    "source_reference": f"Page {chunk['page_number']} ({doc_name})"
                })

        return flashcards[:count]

    def generate_quiz(self, doc_name: str, doc_chunks: List[Dict[str, Any]], count: int) -> List[Dict[str, Any]]:
        quiz = []
        nouns_pool = []
        for chunk in doc_chunks:
            candidates = re.findall(r'\b[A-Z][a-zA-Z]{3,}\b', chunk["chunk_text"])
            nouns_pool.extend(candidates)
        nouns_pool = list(set(nouns_pool))
        
        if len(nouns_pool) < 10:
            nouns_pool.extend(["Process", "Thread", "Memory", "Paging", "Scheduling", "Virtual Memory", "CPU", "Kernel", "Stack"])

        valid_sentences = []
        for chunk in doc_chunks:
            sentences = [s.strip() for s in re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', chunk["chunk_text"]) if len(s.strip()) > 35]
            for sent in sentences:
                found_nouns = [n for n in nouns_pool if n in sent and not sent.startswith(n)]
                if found_nouns:
                    valid_sentences.append((sent, found_nouns[0], chunk["page_number"]))

        unique_sents = []
        seen = set()
        for sent, noun, page in valid_sentences:
            if sent not in seen:
                seen.add(sent)
                unique_sents.append((sent, noun, page))

        for idx, (sent, correct_noun, page) in enumerate(unique_sents[:count]):
            blank_sentence = sent.replace(correct_noun, "__________")
            distractors = [n for n in nouns_pool if n != correct_noun]
            random.shuffle(distractors)
            selected_distractors = list(set(distractors[:5]))[:3]
            
            options = [correct_noun] + selected_distractors
            random.shuffle(options)
            correct_idx = options.index(correct_noun)

            quiz.append({
                "id": f"q-chunked-{idx+1}",
                "question": f"(Page {page}) Fill in the blank: {blank_sentence}",
                "options": options,
                "correctIndex": correct_idx,
                "explanation": f"The correct answer is '{correct_noun}'. As stated on page {page} of the notes: '{sent}'",
                "source_reference": f"Page {page} ({doc_name})"
            })

        if len(quiz) < count:
            if not doc_chunks:
                raise ValueError("Cannot generate practice quiz from empty study material.")
            for idx in range(len(quiz), count):
                chunk = doc_chunks[idx % len(doc_chunks)]
                sentences = [s.strip() for s in re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', chunk["chunk_text"]) if len(s.strip()) > 20]
                sent_idx = idx % len(sentences) if sentences else 0
                sent = sentences[sent_idx] if sentences else "Review notes topic."
                
                # Mask a word from the sentence
                words = [w for w in re.sub(r'[^\w\s]', '', sent).split() if len(w) > 4 and w.lower() not in retriever.STOP_WORDS]
                correct_word = words[0] if words else "Focus"
                blank_sentence = sent.replace(correct_word, "__________")
                
                distractors = ["Structure", "Process", "Analysis", "Concept", "Synthesis", "Method"]
                distractors = [d for d in distractors if d.lower() != correct_word.lower()][:3]
                
                options = [correct_word] + distractors
                random.shuffle(options)
                correct_idx = options.index(correct_word)
                
                quiz.append({
                    "id": f"q-chunked-{idx+1}",
                    "question": f"(Page {chunk['page_number']}) Fill in the blank: {blank_sentence}",
                    "options": options,
                    "correctIndex": correct_idx,
                    "explanation": f"The correct answer is '{correct_word}'. From page {chunk['page_number']}: '{sent}'",
                    "source_reference": f"Page {chunk['page_number']} ({doc_name})"
                })

        return quiz[:count]


class DualModeAIService(BaseAIService):
    """
    AI Service Manager that handles switching between Gemini, Groq, and the local fallback.
    """
    def __init__(self):
        self.local_service = LocalHeuristicAIService()

    def _get_chat_meta(self, doc_chunks: List[Dict[str, Any]], question: str, doc_name: str) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
        scored = retriever.retrieve_relevant_chunks(doc_chunks, question, top_k=1)
        valid_matches = [item for item in scored if item[1] > 0.0]
        if valid_matches:
            top_chunk = valid_matches[0][0]
            return f"Page {top_chunk['page_number']} ({doc_name})", top_chunk
        return None, None

    def _call_gemini(self, doc_chunks: List[Dict[str, Any]], question: str, api_key: str) -> str:
        intent = self.local_service.classify_intent(question)
        context_text = "\n\n".join([f"Page {c['page_number']}: {c['chunk_text']}" for c in doc_chunks[:3]])

        if intent == "summary":
            prompt = (
                f"You are a structured study assistant. Create a structured summary of the document based only on this context:\n{context_text}\n\n"
                f"Strict Rules:\n1. Output exactly 3 to 4 bullet points.\n2. Each bullet point must summarize a key section or concept of the document.\n3. Do not include any intro, outro, tips, or conversational filler."
            )
        elif intent == "overview":
            prompt = (
                f"You are a concise study assistant. Summarize what this document is about based only on this context:\n{context_text}\n\n"
                f"Strict Rules:\n1. Your response must be exactly 1 to 2 sentences.\n2. Summarize only what the document is about.\n3. Do not include any greeting, introduction, or filler phrases."
            )
        elif intent == "flashcards":
            return 'You can generate and study flashcards for this document using the dedicated "Flashcards" tab in the left sidebar.'
        elif intent == "quiz":
            return 'You can generate and take interactive practice quizzes for this document using the dedicated "Practice Quiz" tab in the left sidebar.'
        else:
            prompt = (
                f"You are a strict, concise study assistant. Answer the question based only on this context:\n{context_text}\n\n"
                f"Question: {question}\n\n"
                f"Strict Rules:\n1. Answer the question directly in the very first sentence.\n2. Include at most one supporting sentence if necessary.\n3. Do not include any filler, greeting, or meta-commentary.\n4. If the context does not contain the answer, say exactly: 'I could not find a confident answer in the uploaded notes.'"
            )

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.1}
        }
        
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            return res_data["candidates"][0]["content"]["parts"][0]["text"].strip()

    def _call_groq(self, doc_chunks: List[Dict[str, Any]], question: str, api_key: str) -> str:
        intent = self.local_service.classify_intent(question)
        context_text = "\n\n".join([f"Page {c['page_number']}: {c['chunk_text']}" for c in doc_chunks[:3]])

        if intent == "summary":
            prompt = (
                f"You are a structured study assistant. Create a structured summary of the document based only on this context:\n{context_text}\n\n"
                f"Strict Rules:\n1. Output exactly 3 to 4 bullet points.\n2. Each bullet point must summarize a key section or concept of the document.\n3. Do not include any intro, outro, tips, or conversational filler."
            )
        elif intent == "overview":
            prompt = (
                f"You are a concise study assistant. Summarize what this document is about based only on this context:\n{context_text}\n\n"
                f"Strict Rules:\n1. Your response must be exactly 1 to 2 sentences.\n2. Summarize only what the document is about.\n3. Do not include any greeting, introduction, or filler phrases."
            )
        elif intent == "flashcards":
            return 'You can generate and study flashcards for this document using the dedicated "Flashcards" tab in the left sidebar.'
        elif intent == "quiz":
            return 'You can generate and take interactive practice quizzes for this document using the dedicated "Practice Quiz" tab in the left sidebar.'
        else:
            prompt = (
                f"You are a strict, concise study assistant. Answer the question based only on this context:\n{context_text}\n\n"
                f"Question: {question}\n\n"
                f"Strict Rules:\n1. Answer the question directly in the very first sentence.\n2. Include at most one supporting sentence if necessary.\n3. Do not include any filler, greeting, or meta-commentary.\n4. If the context does not contain the answer, say exactly: 'I could not find a confident answer in the uploaded notes.'"
            )

        url = "https://api.groq.com/openai/v1/chat/completions"
        payload = {
            "model": "llama3-8b-8192",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1
        }
        
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            },
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            return res_data["choices"][0]["message"]["content"].strip()

    def generate_chat_answer(self, doc_name: str, doc_chunks: List[Dict[str, Any]], question: str) -> Dict[str, Any]:
        settings = db.get_settings()
        active_model = settings.get("model", "local")
        
        now = datetime.datetime.now()
        time_str = now.strftime("%I:%M %p")

        if active_model == "local" or active_model == "local-heuristic":
            return self.local_service.generate_chat_answer(doc_name, doc_chunks, question)

        gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        groq_key = os.getenv("GROQ_API_KEY")

        if active_model == "gemini":
            if not gemini_key:
                res = self.local_service.generate_chat_answer(doc_name, doc_chunks, question)
                res["text"] = f"[Local Fallback - GEMINI_API_KEY missing] {res['text']}"
                return res
            try:
                text = self._call_gemini(doc_chunks, question, gemini_key)
                citation, top_chunk = self._get_chat_meta(doc_chunks, question, doc_name)
                return {
                    "sender": "assistant",
                    "text": text,
                    "time": time_str,
                    "citation": citation,
                    "source_excerpt": top_chunk["chunk_text"] if top_chunk else None,
                    "source_page": top_chunk["page_number"] if top_chunk else None
                }
            except Exception as e:
                res = self.local_service.generate_chat_answer(doc_name, doc_chunks, question)
                res["text"] = f"[Local Fallback - Gemini failed: {str(e)[:80]}] {res['text']}"
                return res

        elif active_model == "groq":
            if not groq_key:
                res = self.local_service.generate_chat_answer(doc_name, doc_chunks, question)
                res["text"] = f"[Local Fallback - GROQ_API_KEY missing] {res['text']}"
                return res
            try:
                text = self._call_groq(doc_chunks, question, groq_key)
                citation, top_chunk = self._get_chat_meta(doc_chunks, question, doc_name)
                return {
                    "sender": "assistant",
                    "text": text,
                    "time": time_str,
                    "citation": citation,
                    "source_excerpt": top_chunk["chunk_text"] if top_chunk else None,
                    "source_page": top_chunk["page_number"] if top_chunk else None
                }
            except Exception as e:
                res = self.local_service.generate_chat_answer(doc_name, doc_chunks, question)
                res["text"] = f"[Local Fallback - Groq failed: {str(e)[:80]}] {res['text']}"
                return res

        return self.local_service.generate_chat_answer(doc_name, doc_chunks, question)

    def generate_flashcards(self, doc_name: str, doc_chunks: List[Dict[str, Any]], count: int) -> List[Dict[str, Any]]:
        return self.local_service.generate_flashcards(doc_name, doc_chunks, count)

    def generate_quiz(self, doc_name: str, doc_chunks: List[Dict[str, Any]], count: int) -> List[Dict[str, Any]]:
        return self.local_service.generate_quiz(doc_name, doc_chunks, count)

# Global AI Service instance
ai_service = DualModeAIService()
