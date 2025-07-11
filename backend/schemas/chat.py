from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class ReminderCreate(BaseModel):
    title: str
    description: Optional[str] = ""
    date: str  # YYYY-MM-DD
    time: Optional[str] = "09:00"  # HH:MM
    priority: Optional[str] = "medium"
    category: Optional[str] = "general"

    class Config:
        extra = "allow"

class ReminderResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    date: str
    time: Optional[str] = None
    priority: Optional[str] = None
    category: Optional[str] = None
    completed: bool = False
    created_at: datetime

    class Config:
        from_attributes = True
        extra = "allow"

class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = "default"
    context: Optional[str] = ""

    class Config:
        extra = "allow"

# Missing schema: ChatRequest
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default"
    context: Optional[str] = ""
    model: Optional[str] = None
    messages: Optional[List[Dict[str, Any]]] = None
    file_data: Optional[Dict[str, Any]] = None

    class Config:
        extra = "allow"

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

# Missing schema: MultimodalChatResponse
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

# New OpenRouter Orchestrator Response Schemas
class OrchestratorResponse(BaseModel):
    """Main response format for the OpenRouter orchestrator"""
    model: Optional[str] = None  # e.g., "google/gemini-2.5-flash"
    plugin: Optional[str] = None  # e.g., "file-parser", "gemini-multimodal" or null
    input_type: Optional[str] = None  # e.g., "text", "file", "image_url"
    response: str  # The actual AI response text
    success: bool = True
    message_type: Optional[str] = None  # "text" or "file"
    timestamp: Optional[str] = None
    error: Optional[str] = None

    class Config:
        extra = "allow"

class OrchestratorFileResponse(OrchestratorResponse):
    """Extended response format for file processing with additional metadata"""
    processed_files: Optional[List[Dict[str, Any]]] = []
    embedding_chunks: Optional[List[Dict[str, Any]]] = []

    class Config:
        extra = "allow"

class ChatWithFilesRequest(BaseModel):
    """Request schema for chat endpoint that can handle both text and files"""
    message: str
    session_id: Optional[str] = "default"
    context: Optional[str] = ""
    model: Optional[str] = None
    files: Optional[List[Dict[str, Any]]] = None

    class Config:
        extra = "allow"

class FileUploadRequest(BaseModel):
    intent: Optional[str] = None
    custom_command: Optional[str] = None

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

class ConfirmationRequest(BaseModel):
    decision: str  # "yes" or "no"
    file_id: Optional[int] = None
    session_id: Optional[str] = "default"
    action_data: Optional[Dict[str, Any]] = None

    class Config:
        extra = "allow"

class ConfirmationResponse(BaseModel):
    status: str
    message: str
    results: Optional[Dict[str, Any]] = None

    class Config:
        extra = "allow"

class HistoryResponse(BaseModel):
    id: int
    session_id: str
    message_type: str
    content: str
    metadata: Optional[Dict[str, Any]] = None
    timestamp: datetime

    class Config:
        from_attributes = True
        extra = "allow"

class RemindersGrouped(BaseModel):
    date: str
    reminders: List[ReminderResponse]

    class Config:
        extra = "allow"

# Enhanced embedding chunk schema for RAG
class EmbeddingChunk(BaseModel):
    """Schema for storing embedding-ready text chunks"""
    content: str
    source: str  # filename or source identifier
    chunk_index: int
    created_at: str
    metadata: Dict[str, Any]

    class Config:
        extra = "allow"

class ProcessMessageRequest(BaseModel):
    """Request schema for the main process_message endpoint"""
    message: str
    session_id: Optional[str] = "default"
    model: Optional[str] = None
    messages: Optional[List[Dict[str, Any]]] = None
    file_data: Optional[Dict[str, Any]] = None

    class Config:
        extra = "allow"

class ProcessMessageResponse(BaseModel):
    """Response schema for the main process_message endpoint"""
    model: Optional[str] = None
    plugin: Optional[str] = None
    input_type: Optional[str] = None  # Added for multi-modal support
    response: str
    success: bool = True
    message_type: Optional[str] = None
    timestamp: Optional[str] = None
    processed_files: Optional[List[Dict[str, Any]]] = []
    embedding_chunks: Optional[List[EmbeddingChunk]] = []
    session_id: str
    error: Optional[str] = None

    class Config:
        extra = "allow"

# Legacy schemas for backward compatibility
class MultiModalResponse(BaseModel):
    """Response format for multi-modal Gemini requests"""
    model: Optional[str] = None  # "google/gemini-2.5-flash"
    input_type: Optional[str] = None  # "text", "file", "image_url"
    response: str  # The AI response
    success: bool = True
    error: Optional[str] = None

    class Config:
        extra = "allow"

# Debug schema for payload testing
class DebugChatRequest(BaseModel):
    """Debug schema that accepts any fields for testing"""
    message: Optional[str] = None
    session_id: Optional[str] = None
    context: Optional[str] = None
    model: Optional[str] = None
    messages: Optional[List[Dict[str, Any]]] = None
    file_data: Optional[Dict[str, Any]] = None
    files: Optional[List[Dict[str, Any]]] = None

    class Config:
        extra = "allow" 