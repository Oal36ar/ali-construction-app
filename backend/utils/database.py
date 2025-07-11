from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./orchestrator.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Reminder(Base):
    __tablename__ = "reminders"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    date = Column(String)  # YYYY-MM-DD format
    time = Column(String)  # HH:MM format
    priority = Column(String, default="medium")  # high, medium, low
    category = Column(String, default="general")
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(String, default="default")  # For multi-user support later

class ChatHistory(Base):
    __tablename__ = "chat_history"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)
    message_type = Column(String)  # user, assistant, system
    content = Column(Text)
    meta_data = Column(JSON)  # Store file info, intent, etc.
    timestamp = Column(DateTime, default=datetime.utcnow)
    user_id = Column(String, default="default")

class FileUpload(Base):
    __tablename__ = "file_uploads"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    file_type = Column(String)
    file_size = Column(Integer)
    intent = Column(String)  # extract_reminders, summarize, etc.
    processed = Column(Boolean, default=False)
    result = Column(JSON)  # Store processing results
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(String, default="default")

class ActionLog(Base):
    __tablename__ = "action_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    action_type = Column(String)  # reminder_created, email_sent, etc.
    description = Column(Text)
    status = Column(String)  # success, failed, pending
    meta_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(String, default="default")

# Create tables
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 