from fastapi import APIRouter
from backend.services.storage import db
from backend.schemas.responses import ApiResponse
from backend.schemas.settings import UserSettings

router = APIRouter(prefix="/settings", tags=["settings"])

@router.get("", response_model=ApiResponse[UserSettings])
def get_user_settings():
    """
    Retrieves stored workspace user configurations.
    """
    settings_dict = db.get_settings()
    return ApiResponse(
        success=True,
        message="Settings retrieved successfully",
        data=settings_dict
    )

@router.post("", response_model=ApiResponse[UserSettings])
def update_user_settings(settings: UserSettings):
    """
    Updates stored workspace user configurations.
    """
    updated_dict = db.update_settings(settings.model_dump())
    return ApiResponse(
        success=True,
        message="Settings saved successfully",
        data=updated_dict
    )
