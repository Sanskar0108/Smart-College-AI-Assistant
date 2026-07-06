from pydantic import BaseModel
from typing import List, Optional

class ChatRequest(BaseModel):
    """
    Payload for asking a doubt from active document context.
    """
    document_id: str
    message: str

class ChatResponse(BaseModel):
    """
    Grounded AI response details, including support references.
    """
    sender: str = "assistant"
    text: str
    time: str
    citation: Optional[str] = None
    source_excerpt: Optional[str] = None
    source_page: Optional[int] = None

class FlashcardRequest(BaseModel):
    """
    Payload to trigger custom flashcards.
    """
    document_id: str
    count: Optional[int] = 5

class FlashcardItem(BaseModel):
    """
    Individual front-and-back revision card.
    """
    id: str
    question: str
    answer: str
    source_reference: Optional[str] = None

class QuizRequest(BaseModel):
    """
    Payload to trigger custom quizzes.
    """
    document_id: str
    count: Optional[int] = 5

class QuizQuestionItem(BaseModel):
    """
    Individual multiple-choice question item.
    """
    id: str
    question: str
    options: List[str]
    correctIndex: int
    explanation: str
    source_reference: Optional[str] = None
