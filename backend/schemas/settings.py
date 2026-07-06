from pydantic import BaseModel

class UserSettings(BaseModel):
    """
    Validation schema for workspace customization settings.
    """
    user_name: str
    user_about: str
    model: str
    ollama_url: str
    system_prompt: str
