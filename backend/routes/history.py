from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from utils.database import get_db, ChatHistory, FileUpload, Reminder, ActionLog
from utils.formatter import format_datetime
from typing import Dict, List, Any
from datetime import datetime, timedelta
from typing import Optional

router = APIRouter(prefix="/history", tags=["history"])

@router.get("/")
async def get_full_history(
    session_id: Optional[str] = Query(None, description="Filter by session ID"),
    limit: int = Query(50, description="Maximum number of entries to return"),
    db: Session = Depends(get_db)
):
    """Get chat history"""
    
    try:
        # Get chat history directly from database
        query = db.query(ChatHistory)
        if session_id:
            query = query.filter(ChatHistory.session_id == session_id)
        
        messages = query.order_by(ChatHistory.timestamp.desc()).limit(limit).all()
        
        return {
            "session_id": session_id,
            "total_messages": len(messages),
            "messages": [
                {
                    "id": msg.id,
                    "session_id": msg.session_id,
                    "type": msg.message_type,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat(),
                    "metadata": msg.metadata
                }
                for msg in reversed(messages)  # Chronological order
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching history: {str(e)}")

@router.get("/activity")
async def get_activity_history(
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get comprehensive activity history including chats and file uploads"""
    
    try:
        # Get recent chat history
        recent_chats = db.query(ChatHistory).order_by(
            ChatHistory.timestamp.desc()
        ).limit(limit // 2).all()
        
        # Get recent file uploads
        recent_uploads = db.query(FileUpload).order_by(
            FileUpload.uploaded_at.desc()
        ).limit(limit // 3).all()
        
        # Get recent reminders
        recent_reminders = db.query(Reminder).order_by(
            Reminder.created_at.desc()
        ).limit(limit // 3).all()
        
        # Count totals
        total_chats = db.query(ChatHistory).count()
        total_uploads = db.query(FileUpload).count()
        total_reminders = db.query(Reminder).count()
        
        print(f"📊 Activity summary: {total_chats} chats, {total_uploads} uploads, {total_reminders} reminders")
        
        # Format chat history
        chat_activity = []
        for chat in recent_chats:
            chat_activity.append({
                "id": chat.id,
                "session_id": chat.session_id,
                "type": "chat",
                "content": chat.content[:100] + "..." if len(chat.content) > 100 else chat.content,
                "message_type": chat.message_type,
                "timestamp": format_datetime(chat.timestamp),
                "metadata": chat.metadata if chat.metadata else {}
            })
        
        # Format upload history
        upload_activity = []
        for upload in recent_uploads:
            upload_activity.append({
                "id": upload.id,
                "filename": upload.filename,
                "type": "upload",
                "file_type": upload.file_type,
                "file_size": upload.file_size,
                "intent": upload.intent,
                "processed": upload.processed,
                "uploaded_at": format_datetime(upload.uploaded_at),
                "result": upload.result if upload.result else {}
            })
        
        # Format reminder history
        reminder_activity = []
        for reminder in recent_reminders:
            reminder_activity.append({
                "id": reminder.id,
                "title": reminder.title,
                "description": reminder.description,
                "type": "reminder",
                "date": reminder.date,
                "time": reminder.time,
                "priority": reminder.priority,
                "category": reminder.category,
                "completed": reminder.completed,
                "created_at": format_datetime(reminder.created_at)
            })
        
        # Get last activity timestamp
        last_activity = None
        if recent_chats or recent_uploads or recent_reminders:
            timestamps = []
            if recent_chats:
                timestamps.append(recent_chats[0].timestamp)
            if recent_uploads:
                timestamps.append(recent_uploads[0].uploaded_at)
            if recent_reminders:
                timestamps.append(recent_reminders[0].created_at)
            last_activity = format_datetime(max(timestamps))
        
        return {
            "summary": {
                "total_chats": total_chats,
                "total_uploads": total_uploads,
                "total_reminders": total_reminders,
                "total_activity": total_chats + total_uploads + total_reminders
            },
            "recent_chats": chat_activity,
            "recent_uploads": upload_activity,
            "recent_reminders": reminder_activity,
            "last_activity": last_activity,
            "timestamp": format_datetime(datetime.now())
        }
        
    except Exception as e:
        print(f"❌ Error getting activity history: {e}")
        # Return empty history if database error
        return {
            "summary": {
                "total_chats": 0,
                "total_uploads": 0,
                "total_reminders": 0,
                "total_activity": 0
            },
            "recent_chats": [],
            "recent_uploads": [],
            "recent_reminders": [],
            "last_activity": None,
            "timestamp": format_datetime(datetime.now()),
            "error": "Database not available - showing empty history"
        }

@router.get("/chats/{session_id}")
async def get_chat_history(
    session_id: str,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get chat history for a specific session"""
    
    try:
        chats = db.query(ChatHistory).filter(
            ChatHistory.session_id == session_id
        ).order_by(ChatHistory.timestamp.desc()).limit(limit).all()
        
        print(f"💬 Retrieved {len(chats)} messages for session {session_id}")
        
        return {
            "session_id": session_id,
            "message_count": len(chats),
            "messages": [
                {
                    "id": chat.id,
                    "content": chat.content,
                    "message_type": chat.message_type,
                    "timestamp": format_datetime(chat.timestamp),
                    "metadata": chat.metadata if chat.metadata else {}
                }
                for chat in reversed(chats)  # Reverse to get chronological order
            ]
        }
        
    except Exception as e:
        print(f"❌ Error getting chat history: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving chat history: {str(e)}"
        )

@router.delete("/clear/{session_id}")
async def clear_session_history(
    session_id: str,
    db: Session = Depends(get_db)
):
    """Clear chat history for a specific session"""
    
    try:
        deleted_count = db.query(ChatHistory).filter(
            ChatHistory.session_id == session_id
        ).delete()
        
        db.commit()
        
        print(f"🗑️ Cleared {deleted_count} messages from session {session_id}")
        
        return {
            "status": "success",
            "message": f"Cleared {deleted_count} messages from session {session_id}",
            "session_id": session_id,
            "deleted_count": deleted_count
        }
        
    except Exception as e:
        print(f"❌ Error clearing session history: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error clearing session history: {str(e)}"
        )

@router.get("/actions")
async def get_action_logs(
    action_type: Optional[str] = Query(None, description="Filter by action type"),
    limit: int = Query(100, description="Maximum number of entries to return"),
    db: Session = Depends(get_db)
):
    """Get action logs"""
    
    try:
        # Return mock action logs since ActionLog table might not exist
        return {
            "action_type_filter": action_type,
            "total_actions": 0,
            "actions": [],
            "note": "Action logging not fully implemented yet"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching action logs: {str(e)}")

@router.get("/files")
async def get_file_history(
    limit: int = Query(50, description="Maximum number of files to return"),
    db: Session = Depends(get_db)
):
    """Get file upload history"""
    
    try:
        # Get file history directly from database
        files = db.query(FileUpload).order_by(FileUpload.uploaded_at.desc()).limit(limit).all()
        
        return {
            "total_files": len(files),
            "files": [
                {
                    "id": file.id,
                    "filename": file.filename,
                    "file_type": file.file_type,
                    "file_size": file.file_size,
                    "intent": file.intent,
                    "processed": file.processed,
                    "uploaded_at": file.uploaded_at.isoformat(),
                    "result": file.result
                }
                for file in files
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching file history: {str(e)}")

@router.get("/search")
async def search_history(
    q: str = Query(..., description="Search query"),
    search_type: str = Query("all", description="Type of content to search: all, chat, actions, files"),
    limit: int = Query(50, description="Maximum number of results per type"),
    db: Session = Depends(get_db)
):
    """Search through history"""
    
    try:
        results = {}
        
        if search_type in ["all", "chat"]:
            # Search chat history
            chat_results = db.query(ChatHistory).filter(
                ChatHistory.content.contains(q)
            ).limit(limit).all()
            
            results["chat"] = [
                {
                    "id": chat.id,
                    "session_id": chat.session_id,
                    "content": chat.content,
                    "timestamp": chat.timestamp.isoformat(),
                    "type": "chat"
                }
                for chat in chat_results
            ]
        
        if search_type in ["all", "files"]:
            # Search file uploads
            file_results = db.query(FileUpload).filter(
                FileUpload.filename.contains(q)
            ).limit(limit).all()
            
            results["files"] = [
                {
                    "id": file.id,
                    "filename": file.filename,
                    "file_type": file.file_type,
                    "uploaded_at": file.uploaded_at.isoformat(),
                    "type": "file"
                }
                for file in file_results
            ]
        
        return {
            "query": q,
            "search_type": search_type,
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching history: {str(e)}")

@router.delete("/cleanup")
async def cleanup_old_history(
    days_to_keep: int = Query(30, description="Number of days of history to keep"),
    user_id: Optional[str] = Query(None, description="Specific user ID to clean up"),
    db: Session = Depends(get_db)
):
    """Clean up old history entries"""
    
    try:
        # Calculate cutoff date
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        # Delete old chat history
        chat_deleted = db.query(ChatHistory).filter(
            ChatHistory.timestamp < cutoff_date
        ).delete()
        
        # Delete old file uploads
        files_deleted = db.query(FileUpload).filter(
            FileUpload.uploaded_at < cutoff_date
        ).delete()
        
        db.commit()
        
        return {
            "message": "History cleanup completed",
            "days_kept": days_to_keep,
            "cleanup_results": {
                "chat_messages_deleted": chat_deleted,
                "files_deleted": files_deleted,
                "total_deleted": chat_deleted + files_deleted
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during cleanup: {str(e)}")

@router.get("/recent-context/{session_id}")
async def get_recent_context(
    session_id: str,
    messages_count: int = Query(10, description="Number of recent messages to include"),
    db: Session = Depends(get_db)
):
    """Get recent chat context for a session"""
    
    try:
        # Get recent messages for context
        recent_messages = db.query(ChatHistory).filter(
            ChatHistory.session_id == session_id
        ).order_by(ChatHistory.timestamp.desc()).limit(messages_count).all()
        
        context = " ".join([
            msg.content for msg in reversed(recent_messages)
        ])
        
        return {
            "session_id": session_id,
            "messages_included": len(recent_messages),
            "context": context
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching context: {str(e)}")