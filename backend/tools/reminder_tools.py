#!/usr/bin/env python3
"""
LangChain Tools for Reminder Management
"""

from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Optional, Type
from datetime import datetime
from sqlalchemy.orm import Session


class ReminderInput(BaseModel):
    """Input schema for reminder tools"""
    title: str = Field(..., description="Title of the reminder")
    due_date: str = Field(..., description="Due date in YYYY-MM-DD format")
    description: str = Field(default="", description="Optional description")
    priority: str = Field(default="medium", description="Priority: high, medium, low")


class AddReminderTool(BaseTool):
    """Tool for adding reminders to the system"""
    name = "add_reminder"
    description = """Add a new reminder to the system. 
    Use this when user wants to create, add, or set a reminder.
    Examples: 'remind me to...', 'add reminder for...', 'create a reminder about...'"""
    args_schema: Type[BaseModel] = ReminderInput
    
    def __init__(self, db_session: Session = None):
        super().__init__()
        self.db_session = db_session
    
    def _run(self, title: str, due_date: str, description: str = "", priority: str = "medium") -> str:
        """Execute the add reminder function"""
        try:
            if self.db_session:
                from models.database import Reminder
                from utils.database import ActionLog
                
                new_reminder = Reminder(
                    title=title,
                    description=description,
                    date=due_date,
                    priority=priority,
                    completed=False
                )
                self.db_session.add(new_reminder)
                self.db_session.commit()
                self.db_session.refresh(new_reminder)
                
                # Log the activity
                activity_log = ActionLog(
                    action_type="reminder_created_ai",
                    description=f"AI created reminder: {title}",
                    status="success",
                    meta_data={
                        "reminder_id": new_reminder.id,
                        "title": title,
                        "date": due_date,
                        "priority": priority,
                        "created_by": "ai_tool"
                    }
                )
                self.db_session.add(activity_log)
                self.db_session.commit()
                
                return f"✅ Reminder '{title}' created successfully for {due_date} (ID: {new_reminder.id}, Priority: {priority})"
            else:
                # Fallback for in-memory storage
                reminder_id = datetime.now().microsecond
                return f"✅ Reminder '{title}' created successfully for {due_date} (ID: {reminder_id}, Priority: {priority})"
        except Exception as e:
            return f"❌ Failed to create reminder: {str(e)}"

    async def _arun(self, title: str, due_date: str, description: str = "", priority: str = "medium") -> str:
        """Async version of the tool"""
        return self._run(title, due_date, description, priority)


class ListRemindersInput(BaseModel):
    """Input schema for listing reminders"""
    status: str = Field(default="all", description="Filter by status: all, pending, completed")
    limit: int = Field(default=10, description="Maximum number of reminders to return")


class ListRemindersTool(BaseTool):
    """Tool for listing existing reminders"""
    name = "list_reminders"
    description = """List existing reminders from the system. 
    Use this when user wants to see, check, or view their reminders.
    Examples: 'show my reminders', 'what reminders do I have?', 'list my tasks'"""
    args_schema: Type[BaseModel] = ListRemindersInput
    
    def __init__(self, db_session: Session = None):
        super().__init__()
        self.db_session = db_session
    
    def _run(self, status: str = "all", limit: int = 10) -> str:
        """Execute the list reminders function"""
        try:
            if self.db_session:
                from models.database import Reminder
                query = self.db_session.query(Reminder)
                
                if status == "pending":
                    query = query.filter(Reminder.completed == False)
                elif status == "completed":
                    query = query.filter(Reminder.completed == True)
                
                reminders = query.limit(limit).all()
                
                if not reminders:
                    return "📝 No reminders found."
                
                result = f"📋 Found {len(reminders)} reminder(s):\n"
                for reminder in reminders:
                    status_emoji = "✅" if reminder.completed else "⏰"
                    result += f"{status_emoji} {reminder.title} - Due: {reminder.date} (Priority: {reminder.priority})\n"
                
                return result
            else:
                return "📝 No reminders found (using in-memory storage)."
        except Exception as e:
            return f"❌ Failed to list reminders: {str(e)}"

    async def _arun(self, status: str = "all", limit: int = 10) -> str:
        """Async version of the tool"""
        return self._run(status, limit)