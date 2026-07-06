from pydantic import BaseModel
from typing import Generic, TypeVar, Optional

T = TypeVar('T')

class ApiResponse(BaseModel, Generic[T]):
    """
    Consistent envelope for all API responses.
    """
    success: bool
    message: Optional[str] = None
    data: Optional[T] = None
    error: Optional[str] = None
