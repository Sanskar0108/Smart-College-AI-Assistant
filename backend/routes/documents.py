import os
import uuid
import datetime
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from backend.core.config import UPLOAD_DIR, ALLOWED_EXTENSIONS, MAX_FILE_SIZE_BYTES
from backend.services.storage import db
from backend.services.extractor import DocumentExtractor
from backend.services.chunker import DocumentChunker
from backend.schemas.responses import ApiResponse
from backend.schemas.documents import DocumentMetadata, SetActiveDocRequest, ActiveDocResponse, DeleteDocResponse, DocumentDetail
from typing import List

router = APIRouter(prefix="/documents", tags=["documents"])

def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@router.post("/upload", response_model=ApiResponse[DocumentMetadata])
async def upload_document(file: UploadFile = File(...)):
    """
    Uploads a document (PDF or TXT), extracts page details/text context,
    and returns document metadata.
    """
    print(f"[DEBUG] POST /api/documents/upload - Received file: {file.filename}")
    # 1. Validation Checks
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No filename provided in upload payload."
        )
    
    if not allowed_file(file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type. Allowed formats: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # 2. Setup ID and Timestamps
    doc_id = f"doc-{uuid.uuid4().hex[:8]}"
    upload_timestamp = datetime.datetime.now().isoformat()
    file_ext = file.filename.rsplit('.', 1)[1].lower()
    
    saved_filename = f"{doc_id}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, saved_filename)
    
    # 3. Read and Save File locally
    try:
        content = await file.read()
        file_size = len(content)
        
        if file_size > MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File exceeds maximum size limits of {MAX_FILE_SIZE_BYTES // (1024 * 1024)}MB."
            )
            
        with open(file_path, "wb") as f:
            f.write(content)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file physically: {str(e)}"
        )

    # 4. Initialize Database Record in "pending" status
    meta = {
        "id": doc_id,
        "name": file.filename,
        "type": file_ext,
        "size_bytes": file_size,
        "upload_timestamp": upload_timestamp,
        "parse_status": "pending",
        "parse_error": None,
        "active": False,
        "preview_snippet": "",
        "page_count": 0
    }
    
    # Register pending state
    db.add_document(meta, "")

    # 5. Extract Text & Parse Pages
    try:
        extracted_text, page_count, preview_snippet = DocumentExtractor.extract_text(file_path, file_ext)
        
        # Generate study context chunks
        chunks = DocumentChunker.chunk_document(doc_id, file.filename, extracted_text)
        
        # Update record to completed with chunks
        db.update_document_status(
            doc_id=doc_id,
            status="completed",
            error=None,
            text=extracted_text,
            pages=page_count,
            preview=preview_snippet,
            chunks=chunks
        )
        
        # Fetch updated record
        updated_doc = db.get_document(doc_id)
        # Omit extracted text for response schema match
        if updated_doc and "extracted_text" in updated_doc:
            del updated_doc["extracted_text"]
            
        return ApiResponse(
            success=True,
            message="Document uploaded and processed successfully",
            data=updated_doc
        )
        
    except Exception as e:
        # Update record to failed state
        error_msg = str(e)
        db.update_document_status(
            doc_id=doc_id,
            status="failed",
            error=error_msg,
            text="",
            pages=0,
            preview=""
        )
        
        # Remove physical file if extraction failed to preserve clean directory
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except OSError:
                pass
                
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Text extraction failed: {error_msg}"
        )

@router.get("", response_model=ApiResponse[List[DocumentMetadata]])
def list_documents():
    """
    Lists all indexed document metadata states.
    """
    print("[DEBUG] GET /api/documents - listing all documents")
    docs = db.list_documents()
    return ApiResponse(
        success=True,
        message="Document list retrieved successfully",
        data=docs
    )

@router.delete("/{id}", response_model=ApiResponse[DeleteDocResponse])
def delete_document(id: str):
    """
    Deletes the document matching path ID from database and filesystem.
    """
    print(f"[DEBUG] DELETE /api/documents/{id}")
    deleted_filename = db.delete_document(id)
    if not deleted_filename:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID '{id}' was not found in storage."
        )
    return ApiResponse(
        success=True,
        message=f"Document '{deleted_filename}' removed successfully",
        data={"id": id, "deleted": True}
    )

@router.get("/active", response_model=ApiResponse[ActiveDocResponse])
def get_active_document():
    """
    Retrieves the currently selected workspace document context.
    """
    print("[DEBUG] GET /api/documents/active")
    active_id = db.get_active_document_id()
    return ApiResponse(
        success=True,
        message="Active document ID retrieved successfully",
        data={"active_document_id": active_id}
    )

@router.post("/active", response_model=ApiResponse[ActiveDocResponse])
def set_active_document(req: SetActiveDocRequest):
    """
    Updates the workspace active document scope focus.
    """
    print(f"[DEBUG] POST /api/documents/active - id: {req.id}")
    success = db.set_active_document_id(req.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID '{req.id}' not found in database."
        )
    return ApiResponse(
        success=True,
        message="Active document updated successfully",
        data={"active_document_id": req.id}
    )

@router.get("/{id}", response_model=ApiResponse[DocumentDetail])
def get_document(id: str):
    """
    Retrieves a single document's full details (including extracted_text).
    """
    print(f"[DEBUG] GET /api/documents/{id}")
    doc = db.get_document(id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID '{id}' was not found in storage."
        )
    return ApiResponse(
        success=True,
        message="Document details retrieved successfully",
        data=doc
    )
