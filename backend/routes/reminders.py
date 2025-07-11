from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from utils.database import get_db, Reminder
from schemas.chat import ReminderCreate
from schemas.response import ReminderResponse, RemindersGrouped
from typing import List, Optional
from utils.formatter import format_datetime
from datetime import datetime, timedelta

router = APIRouter(prefix="/reminders", tags=["reminders"])

@router.get("/", response_model=List[RemindersGrouped])
async def get_reminders_grouped(
    completed: Optional[bool] = Query(None, description="Filter by completion status"),
    db: Session = Depends(get_db)
):
    """Get all reminders grouped by date"""
    
    try:
        if completed is None:
            completed = False
        
        # Get reminders from database
        reminders = db.query(Reminder).filter(Reminder.completed == completed).order_by(Reminder.date.asc()).all()
        
        # Group manually
        grouped = {}
        for reminder in reminders:
            if reminder.date not in grouped:
                grouped[reminder.date] = []
            grouped[reminder.date].append(reminder)
        
        result = []
        for date_str in sorted(grouped.keys()):
            result.append(RemindersGrouped(
                date=date_str,
                reminders=[ReminderResponse.from_orm(r) for r in grouped[date_str]]
            ))
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching reminders: {str(e)}")

@router.get("/all", response_model=List[ReminderResponse])
async def get_all_reminders(db: Session = Depends(get_db)):
    """Get all reminders"""
    
    # ===== COMPREHENSIVE LOGGING =====
    print(f"\n📋 === GET ALL REMINDERS ENDPOINT HIT ===")
    print(f"🔍 Fetching all reminders from database")
    
    try:
        # Query all reminders from database
        reminders = db.query(Reminder).order_by(Reminder.date.asc()).all()
        
        print(f"📋 Retrieved {len(reminders)} reminders")
        print(f"📊 Reminder summary:")
        for i, reminder in enumerate(reminders[:5]):  # Show first 5
            print(f"  {i+1}. {reminder.title} - {reminder.date} ({reminder.priority})")
        if len(reminders) > 5:
            print(f"  ... and {len(reminders) - 5} more")
        
        # Convert to response format
        reminder_responses = []
        for reminder in reminders:
            reminder_responses.append(ReminderResponse(
                id=reminder.id,
                title=reminder.title,
                description=reminder.description or "",
                date=reminder.date,
                time=reminder.time or "09:00",
                priority=reminder.priority or "medium",
                category=reminder.category or "general",
                completed=reminder.completed,
                created_at=reminder.created_at
            ))
        
        print(f"✅ Successfully converted {len(reminder_responses)} reminders to response format")
        print(f"📋 === GET ALL REMINDERS ENDPOINT COMPLETE (SUCCESS) ===\n")
        return reminder_responses
        
    except Exception as e:
        print(f"❌ Error getting reminders: {e}")
        print(f"❌ Exception type: {type(e).__name__}")
        print(f"❌ Exception details: {str(e)}")
        print(f"📋 === GET ALL REMINDERS ENDPOINT COMPLETE (ERROR) ===\n")
        # Return empty list if database error
        return []

@router.post("/", response_model=ReminderResponse)
async def create_reminder(
    reminder: ReminderCreate,
    db: Session = Depends(get_db)
):
    """Create a new reminder"""
    
    # ===== COMPREHENSIVE LOGGING =====
    print(f"\n📝 === CREATE REMINDER ENDPOINT HIT ===")
    print(f"📝 Creating reminder: {reminder.title}")
    print(f"📅 Date: {reminder.date}, Time: {reminder.time}")
    print(f"📋 Description: {reminder.description}")
    print(f"🎯 Priority: {reminder.priority}")
    print(f"📁 Category: {reminder.category}")
    
    try:
        print(f"🔄 Creating reminder object...")
        
        # Create new reminder
        db_reminder = Reminder(
            title=reminder.title,
            description=reminder.description,
            date=reminder.date,
            time=reminder.time,
            priority=reminder.priority,
            category=reminder.category,
            completed=False,
            created_at=datetime.now()
        )
        
        print(f"💾 Saving to database...")
        db.add(db_reminder)
        db.commit()
        db.refresh(db_reminder)
        
        print(f"✅ Reminder created with ID: {db_reminder.id}")
        print(f"📊 Reminder details:")
        print(f"  ID: {db_reminder.id}")
        print(f"  Title: {db_reminder.title}")
        print(f"  Date: {db_reminder.date}")
        print(f"  Time: {db_reminder.time}")
        print(f"  Priority: {db_reminder.priority}")
        
        response = ReminderResponse(
            id=db_reminder.id,
            title=db_reminder.title,
            description=db_reminder.description or "",
            date=db_reminder.date,
            time=db_reminder.time or "09:00",
            priority=db_reminder.priority or "medium",
            category=db_reminder.category or "general",
            completed=db_reminder.completed,
            created_at=db_reminder.created_at
        )
        
        print(f"✅ Reminder created successfully")
        print(f"📝 === CREATE REMINDER ENDPOINT COMPLETE (SUCCESS) ===\n")
        return response
        
    except Exception as e:
        print(f"❌ Error creating reminder: {e}")
        print(f"❌ Exception type: {type(e).__name__}")
        print(f"❌ Exception details: {str(e)}")
        print(f"📝 === CREATE REMINDER ENDPOINT COMPLETE (ERROR) ===\n")
        raise HTTPException(
            status_code=500,
            detail=f"Error creating reminder: {str(e)}"
        )

@router.get("/upcoming", response_model=List[ReminderResponse])
async def get_upcoming_reminders(
    days: int = Query(7, description="Number of days ahead to look"),
    db: Session = Depends(get_db)
):
    """Get upcoming reminders for the next N days"""
    
    try:
        # Calculate date range
        today = datetime.now().date().strftime('%Y-%m-%d')
        future_date = (datetime.now().date() + timedelta(days=days)).strftime('%Y-%m-%d')
        
        # Query upcoming reminders
        reminders = db.query(Reminder).filter(
            Reminder.date >= today,
            Reminder.date <= future_date,
            Reminder.completed == False
        ).order_by(Reminder.date.asc()).all()
        
        return [ReminderResponse.from_orm(reminder) for reminder in reminders]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching upcoming reminders: {str(e)}")

@router.get("/search", response_model=List[ReminderResponse])
async def search_reminders(
    q: str = Query(..., description="Search query"),
    db: Session = Depends(get_db)
):
    """Search reminders by title or description"""
    
    try:
        # Search in title and description
        reminders = db.query(Reminder).filter(
            (Reminder.title.contains(q)) | 
            (Reminder.description.contains(q))
        ).order_by(Reminder.date.asc()).all()
        
        return [ReminderResponse.from_orm(reminder) for reminder in reminders]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching reminders: {str(e)}")

@router.put("/{reminder_id}", response_model=ReminderResponse)
async def update_reminder(
    reminder_id: int,
    updates: dict,
    db: Session = Depends(get_db)
):
    """Update a reminder"""
    
    try:
        reminder = db.query(Reminder).filter(Reminder.id == reminder_id).first()
        
        if not reminder:
            raise HTTPException(status_code=404, detail="Reminder not found")
        
        # Update fields
        for field, value in updates.items():
            if hasattr(reminder, field):
                setattr(reminder, field, value)
        
        db.commit()
        db.refresh(reminder)
        
        return ReminderResponse.from_orm(reminder)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating reminder: {str(e)}")

@router.put("/{reminder_id}/complete")
async def complete_reminder(
    reminder_id: int,
    db: Session = Depends(get_db)
):
    """Mark a reminder as completed"""
    
    try:
        reminder = db.query(Reminder).filter(Reminder.id == reminder_id).first()
        
        if not reminder:
            raise HTTPException(status_code=404, detail="Reminder not found")
        
        reminder.completed = True
        db.commit()
        
        print(f"✅ Reminder {reminder_id} marked as completed")
        
        return {
            "status": "success",
            "message": f"Reminder '{reminder.title}' marked as completed",
            "reminder_id": reminder_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error completing reminder: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error completing reminder: {str(e)}"
        )

@router.delete("/{reminder_id}")
async def delete_reminder(
    reminder_id: int,
    db: Session = Depends(get_db)
):
    """Delete a reminder"""
    
    try:
        reminder = db.query(Reminder).filter(Reminder.id == reminder_id).first()
        
        if not reminder:
            raise HTTPException(status_code=404, detail="Reminder not found")
        
        title = reminder.title
        db.delete(reminder)
        db.commit()
        
        print(f"🗑️ Reminder {reminder_id} deleted")
        
        return {
            "status": "success",
            "message": f"Reminder '{title}' deleted successfully",
            "reminder_id": reminder_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error deleting reminder: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting reminder: {str(e)}"
        )

@router.get("/{reminder_id}", response_model=ReminderResponse)
async def get_reminder(
    reminder_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific reminder by ID"""
    
    try:
        reminder = db.query(Reminder).filter(Reminder.id == reminder_id).first()
        
        if not reminder:
            raise HTTPException(status_code=404, detail="Reminder not found")
        
        return ReminderResponse.from_orm(reminder)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching reminder: {str(e)}") 