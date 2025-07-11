from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class ChatResponse(BaseModel):
    response: str
    session_id: str
    suggestions: Optional[List[str]] = []
    needs_confirmation: bool = False
    confirmation_data: Optional[Dict[str, Any]] = None
    tools_used: Optional[List[str]] = []
    tool_count: int = 0

    class Config:
        extra = "allow"

class MultimodalChatResponse(BaseModel):
    """Response schema for multimodal chat endpoint"""
    response: str
    model: Optional[str] = None
    plugin: Optional[str] = None
    input_type: Optional[str] = "text"
    processed_files: Optional[int] = 0
    file_previews: Optional[List[str]] = []
    session_id: Optional[str] = None
    success: bool = True
    error: Optional[str] = None

    class Config:
        extra = "allow"

class FileUploadResponse(BaseModel):
    filename: str
    file_type: str
    suggested_intent: str
    summary: str
    confirmation_prompt: str
    extracted_data: Optional[Dict[str, Any]] = None
    needs_confirmation: bool = True

    class Config:
        extra = "allow"

class ConfirmationResponse(BaseModel):
    status: str
    message: str
    results: Optional[Dict[str, Any]] = None

    class Config:
        extra = "allow"

class ReminderResponse(BaseModel):
    """Response schema for reminder objects"""
    id: int
    title: str
    description: str
    date: str
    time: str
    priority: str
    category: str
    completed: bool
    created_at: datetime

    @classmethod
    def from_orm(cls, reminder):
        """Create from ORM object"""
        return cls(
            id=reminder.id,
            title=reminder.title,
            description=reminder.description or "",
            date=reminder.date,
            time=reminder.time or "09:00",
            priority=reminder.priority or "medium",
            category=reminder.category or "general",
            completed=reminder.completed,
            created_at=reminder.created_at
        )

    class Config:
        extra = "allow"

class RemindersGrouped(BaseModel):
    """Response schema for grouped reminders"""
    date: str
    reminders: List[ReminderResponse]

    class Config:
        extra = "allow" 