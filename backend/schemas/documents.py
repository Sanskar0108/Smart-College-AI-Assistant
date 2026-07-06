from pydantic import BaseModel
from typing import Optional

class DocumentMetadata(BaseModel):
    """
    Pydantic schema representing the full metadata state of a study document.
    """
    id: str
    name: str
    type: str
    size_bytes: int
    upload_timestamp: str
    parse_status: str  # pending, completed, failed
    parse_error: Optional[str] = None
    active: bool
    preview_snippet: str
    page_count: int

class DocumentDetail(DocumentMetadata):
    """
    Detailed document view including full text extraction.
    """
    extracted_text: str

class SetActiveDocRequest(BaseModel):
    """
    Payload required to switch active workspace focus.
    """
    id: str

class ActiveDocResponse(BaseModel):
    """
    Response schema returning current active file UUID.
    """
    active_document_id: Optional[str] = None

class DeleteDocResponse(BaseModel):
    """
    Response schema returning deleted status details.
    """
    id: str
    deleted: bool
