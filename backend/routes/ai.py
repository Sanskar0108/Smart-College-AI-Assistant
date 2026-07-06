from fastapi import APIRouter, HTTPException, status
from backend.services.storage import db
from backend.services.ai import ai_service
from backend.schemas.responses import ApiResponse
from backend.schemas.ai import ChatRequest, ChatResponse, FlashcardRequest, FlashcardItem, QuizRequest, QuizQuestionItem
from typing import List

router = APIRouter(prefix="/ai", tags=["ai"])

def get_verified_document_text(document_id: str) -> dict:
    """
    Helper to fetch the document from DB and verify it is parsed and not empty.
    """
    doc = db.get_document(document_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID '{document_id}' was not found."
        )
    
    if doc.get("parse_status") == "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document text extraction is currently pending. Please try again shortly."
        )
        
    if doc.get("parse_status") == "failed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Document parsing previously failed. Error: {doc.get('parse_error')}"
        )

    # Fetch the raw text contents
    full_doc = db.get_document(document_id) # get_document returns metadata only without full text
    
    # We must fetch the actual full record with extracted_text from DB
    with db.lock:
        state = db._load_state_unlocked()
        for d in state.get("documents", []):
            if d["id"] == document_id:
                return d
                
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Internal index retrieval error."
    )

@router.post("/chat", response_model=ApiResponse[ChatResponse])
def chat_with_notes(req: ChatRequest):
    """
    Grounded question-answering matching doubts with document paragraphs.
    """
    print(f"[DEBUG] POST /api/ai/chat - document_id: {req.document_id}, query: {req.message}")
    doc_record = get_verified_document_text(req.document_id)
    chunks = doc_record.get("chunks", [])
    
    # Generate doubt resolution response from TF-IDF retrieved chunks
    reply = ai_service.generate_chat_answer(doc_record["name"], chunks, req.message)
    
    return ApiResponse(
        success=True,
        message="Doubt resolved against notes context",
        data=reply
    )

@router.post("/flashcards", response_model=ApiResponse[List[FlashcardItem]])
def generate_flashcards(req: FlashcardRequest):
    """
    Generates Q&A study cards from the active notes text.
    """
    print(f"[DEBUG] POST /api/ai/flashcards - document_id: {req.document_id}, count: {req.count}")
    doc_record = get_verified_document_text(req.document_id)
    chunks = doc_record.get("chunks", [])
    
    # Generate deck list from chunks
    cards = ai_service.generate_flashcards(doc_record["name"], chunks, req.count)
    
    return ApiResponse(
        success=True,
        message="Flashcards compiled successfully",
        data=cards
    )

@router.post("/quiz", response_model=ApiResponse[List[QuizQuestionItem]])
def generate_quiz(req: QuizRequest):
    """
    Generates fill-in-the-blank MCQ quizzes with distractor terms from the notes.
    """
    print(f"[DEBUG] POST /api/ai/quiz - document_id: {req.document_id}, count: {req.count}")
    doc_record = get_verified_document_text(req.document_id)
    chunks = doc_record.get("chunks", [])
    
    # Generate quiz list from chunks
    quiz = ai_service.generate_quiz(doc_record["name"], chunks, req.count)
    
    return ApiResponse(
        success=True,
        message="MCQ assessment generated successfully",
        data=quiz
    )
