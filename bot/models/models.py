from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class User(BaseModel):
    user_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    current_room_code: Optional[str] = None
    role: str = "user"  # "user" or "admin"


class Room(BaseModel):
    code: str
    name: str
    description: Optional[str] = None
    owner_id: int
    members: List[int] = []
    linked_chat_id: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True


class File(BaseModel):
    file_id: str
    file_type: str  # document, photo, text, voice, etc.
    file_name: Optional[str] = None
    caption: Optional[str] = None
    uploader_id: int
    room_code: str
    tags: List[str] = []
    ai_tags: List[str] = []  # AI-suggested tags
    created_at: datetime = Field(default_factory=datetime.utcnow)
    message_id: Optional[int] = None  # For reference


class AIUsage(BaseModel):
    user_id: int
    command: str  # summarise, explain, quiz
    date: str  # YYYY-MM-DD format for daily tracking
    count: int = 1
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Settings(BaseModel):
    key: str
    value: str
    description: Optional[str] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)