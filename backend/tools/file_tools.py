#!/usr/bin/env python3
"""
LangChain Tools for File and Text Processing
"""

from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Optional, Type, List
from datetime import datetime
from sqlalchemy.orm import Session
import re

# Import database utilities
try:
    from utils.database import get_db, FileUpload
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False
    print("⚠️ Database utilities not available for file tools")


class SummaryInput(BaseModel):
    """Input schema for text summarization"""
    text: str = Field(..., description="Text content to summarize")
    max_length: int = Field(default=200, description="Maximum summary length in words")
    focus: str = Field(default="general", description="Focus area: general, key_dates, action_items, contacts")


class SummarizeFileTool(BaseTool):
    """Tool for summarizing text content"""
    name: str = "summarize_file"
    description: str = """Summarize long text content into a shorter, concise summary. 
    Use this when user wants to summarize, condense, or get a brief overview of text.
    Examples: 'summarize this document', 'give me a summary of...', 'condense this text'"""
    args_schema: Type[BaseModel] = SummaryInput
    
    def _run(self, text: str, max_length: int = 200, focus: str = "general") -> str:
        """Execute the text summarization function"""
        try:
            words = text.split()
            
            if len(words) <= max_length:
                return f"✅ Text is already concise ({len(words)} words):\n{text}"
            
            # Different summarization strategies based on focus
            if focus == "key_dates":
                summary = self._extract_dates_summary(text)
            elif focus == "action_items":
                summary = self._extract_action_items(text)
            elif focus == "contacts":
                summary = self._extract_contacts_summary(text)
            else:
                summary = self._general_summary(text, max_length)
            
            return f"✅ Summary ({focus}):\n{summary}"
        except Exception as e:
            return f"❌ Failed to summarize text: {str(e)}"
    
    def _general_summary(self, text: str, max_length: int) -> str:
        """Create a general summary of the text"""
        sentences = text.split('.')
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) <= 3:
            return text[:max_length * 6] + "..." if len(text) > max_length * 6 else text
        
        # Take first sentence, middle sentence, and last sentence
        summary_parts = []
        if sentences:
            summary_parts.append(sentences[0])
        if len(sentences) > 2:
            summary_parts.append(sentences[len(sentences) // 2])
        if len(sentences) > 1:
            summary_parts.append(sentences[-1])
        
        summary = '. '.join(summary_parts) + '.'
        
        # Truncate if still too long
        if len(summary.split()) > max_length:
            summary = ' '.join(summary.split()[:max_length]) + "..."
        
        return summary
    
    def _extract_dates_summary(self, text: str) -> str:
        """Extract and summarize date-related information"""
        date_patterns = [
            r'\d{1,2}/\d{1,2}/\d{4}',  # MM/DD/YYYY
            r'\d{4}-\d{2}-\d{2}',      # YYYY-MM-DD
            r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}',
            r'\b(due|deadline|expires?|appointment|meeting|scheduled)\b.*?\d'
        ]
        
        date_info = []
        for pattern in date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            date_info.extend(matches)
        
        if date_info:
            return f"Key dates found: {', '.join(date_info[:5])}"
        else:
            return "No specific dates found in the text."
    
    def _extract_action_items(self, text: str) -> str:
        """Extract action items and tasks"""
        action_patterns = [
            r'(need to|must|should|required to|have to)\s+([^.]+)',
            r'(action|task|todo|reminder):\s*([^.]+)',
            r'(complete|finish|submit|deliver|send)\s+([^.]+)'
        ]
        
        actions = []
        for pattern in action_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                actions.append(match[1] if isinstance(match, tuple) else match)
        
        if actions:
            return f"Action items: {'. '.join(actions[:3])}"
        else:
            return "No clear action items found."
    
    def _extract_contacts_summary(self, text: str) -> str:
        """Extract and summarize contact information"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        
        emails = re.findall(email_pattern, text)
        phones = re.findall(phone_pattern, text)
        
        contacts = []
        if emails:
            contacts.append(f"{len(emails)} email(s)")
        if phones:
            contacts.append(f"{len(phones)} phone number(s)")
        
        if contacts:
            return f"Contact information found: {', '.join(contacts)}"
        else:
            return "No contact information found."

    async def _arun(self, text: str, max_length: int = 200, focus: str = "general") -> str:
        """Async version of the tool"""
        return self._run(text, max_length, focus)


class FileAnalysisInput(BaseModel):
    """Input schema for file analysis"""
    content: str = Field(..., description="File content to analyze")
    filename: str = Field(..., description="Name of the file")
    file_type: str = Field(default="text", description="Type of file (text, pdf, doc, etc.)")


class AnalyzeFileTool(BaseTool):
    """Tool for analyzing file content"""
    name: str = "analyze_file"
    description: str = """Analyze file content and extract insights, patterns, and key information. 
    Use this when user wants to analyze, examine, or get insights from a file.
    Examples: 'analyze this file', 'what's in this document?', 'examine the content'"""
    args_schema: Type[BaseModel] = FileAnalysisInput
    
    def _run(self, content: str, filename: str, file_type: str = "text") -> str:
        """Execute the file analysis function"""
        try:
            analysis = {
                "filename": filename,
                "file_type": file_type,
                "word_count": len(content.split()),
                "char_count": len(content),
                "line_count": len(content.split('\n')),
                "analysis_date": datetime.now().isoformat()
            }
            
            # Extract key metrics
            emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', content)
            phones = re.findall(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', content)
            dates = re.findall(r'\d{1,2}/\d{1,2}/\d{4}|\d{4}-\d{2}-\d{2}', content)
            
            # Common keywords analysis
            keywords = ["deadline", "due", "appointment", "meeting", "task", "reminder", "urgent", "important"]
            found_keywords = [kw for kw in keywords if kw.lower() in content.lower()]
            
            result = f"📄 File Analysis: {filename}\n"
            result += f"📊 Stats: {analysis['word_count']} words, {analysis['line_count']} lines\n"
            
            if emails:
                result += f"📧 Emails found: {len(emails)}\n"
            if phones:
                result += f"📞 Phone numbers: {len(phones)}\n"
            if dates:
                result += f"📅 Dates found: {len(dates)}\n"
            if found_keywords:
                result += f"🔍 Keywords: {', '.join(found_keywords)}\n"
            
            # Content preview
            preview = content[:200] + "..." if len(content) > 200 else content
            result += f"📝 Preview: {preview}"
            
            return result
        except Exception as e:
            return f"❌ Failed to analyze file: {str(e)}"

    async def _arun(self, content: str, filename: str, file_type: str = "text") -> str:
        """Async version of the tool"""
        return self._run(content, filename, file_type)


class RetrieveFileInput(BaseModel):
    """Input schema for retrieving uploaded files"""
    filename: Optional[str] = Field(None, description="Name of the uploaded file to retrieve")
    file_id: Optional[int] = Field(None, description="ID of the uploaded file to retrieve")
    recent_count: int = Field(default=5, description="Number of recent files to list if no specific file requested")


class RetrieveUploadedFileTool(BaseTool):
    """Tool for retrieving uploaded file content from database"""
    name: str = "retrieve_uploaded_file"
    description: str = """Retrieve content from previously uploaded files stored in the database.
    Use this when user asks about files they've uploaded before, wants to summarize uploaded files,
    or references files without uploading new ones. Can retrieve by filename or list recent uploads.
    Examples: 'summarize the file I uploaded', 'what was in that document?', 'show me my uploaded files'"""
    args_schema: Type[BaseModel] = RetrieveFileInput
    db_session: Optional[Session] = None
    
    def __init__(self, db_session: Session = None):
        super().__init__()
        self.db_session = db_session
    
    def _run(self, filename: Optional[str] = None, file_id: Optional[int] = None, recent_count: int = 5) -> str:
        """Execute the file retrieval function"""
        if not DATABASE_AVAILABLE:
            return "❌ Database not available. Cannot retrieve uploaded files."
        
        try:
            # Get database session
            if self.db_session:
                db = self.db_session
                should_close = False
            else:
                db = next(get_db())
                should_close = True
            
            try:
                # If specific file requested by ID
                if file_id:
                    file_record = db.query(FileUpload).filter(FileUpload.id == file_id).first()
                    if file_record and file_record.content:
                        return f"📄 File: {file_record.filename}\n📊 Type: {file_record.file_type}\n📝 Content:\n{file_record.content}"
                    elif file_record:
                        return f"❌ File '{file_record.filename}' found but no content stored."
                    else:
                        return f"❌ No file found with ID {file_id}."
                
                # If specific file requested by filename
                elif filename:
                    file_record = db.query(FileUpload).filter(FileUpload.filename.ilike(f"%{filename}%")).first()
                    if file_record and file_record.content:
                        return f"📄 File: {file_record.filename}\n📊 Type: {file_record.file_type}\n📝 Content:\n{file_record.content}"
                    elif file_record:
                        return f"❌ File '{file_record.filename}' found but no content stored."
                    else:
                        return f"❌ No file found matching '{filename}'. Try listing recent files first."
                
                # List recent files if no specific file requested
                else:
                    recent_files = db.query(FileUpload).order_by(FileUpload.uploaded_at.desc()).limit(recent_count).all()
                    
                    if not recent_files:
                        return "📁 No files have been uploaded yet. Please upload a file first."
                    
                    file_list = []
                    for i, file_record in enumerate(recent_files, 1):
                        status = "✅ Content available" if file_record.content else "❌ No content"
                        file_list.append(f"{i}. {file_record.filename} (ID: {file_record.id}) - {file_record.file_type} - {status}")
                    
                    return f"📁 Recent uploaded files:\n" + "\n".join(file_list) + "\n\nTo retrieve a specific file, use the filename or ID."
            
            finally:
                if should_close:
                    db.close()
        
        except Exception as e:
            return f"❌ Error retrieving file: {str(e)}"
    
    async def _arun(self, filename: Optional[str] = None, file_id: Optional[int] = None, recent_count: int = 5) -> str:
        """Async version of the tool"""
        return self._run(filename, file_id, recent_count)