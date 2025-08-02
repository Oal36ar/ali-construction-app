from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Form, Request
from sqlalchemy.orm import Session
from utils.database import get_db, FileUpload
from schemas.response import FileUploadResponse
from utils.file_parser import parse_file_by_type, detect_file_type
from utils.enhanced_embedding_manager import enhanced_embedding_manager
from typing import Optional
import uuid

router = APIRouter(prefix="/upload", tags=["upload"])

@router.post("/", response_model=FileUploadResponse)
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    intent: Optional[str] = Form(None),
    custom_command: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Upload and parse a file - returns clean text and preview
    
    Supports: PDF, CSV, DOCX, XLSX, and other text files
    """
    
    print(f"\n📤 === FILE UPLOAD ===")
    print(f"📄 File: {file.filename}")
    print(f"📋 Content-Type: {file.content_type}")
    print(f"🎯 Intent: {intent or 'auto'}")
    
    # Validate file size (10MB limit)
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    # Read file content
    content = await file.read()
    print(f"📊 File size: {len(content)} bytes")
    
    if len(content) > MAX_FILE_SIZE:
        print(f"❌ File too large: {len(content)} > {MAX_FILE_SIZE}")
        raise HTTPException(status_code=413, detail="File too large. Maximum size is 10MB.")
    
    if len(content) == 0:
        print(f"❌ Empty file uploaded")
        raise HTTPException(status_code=400, detail="Empty file uploaded.")

    try:
        # Detect file type
        file_type = detect_file_type(file.filename, file.content_type)
        print(f"🔍 Detected file type: {file_type}")
        
        if file_type == "unknown":
            print(f"❌ Unsupported file type")
            raise HTTPException(status_code=400, detail="Unsupported file type.")
        
        # Parse file content using the new parse_file_by_type function
        print(f"🔄 Parsing file content...")
        parse_result = parse_file_by_type(file.filename, content)
        
        if "Error parsing" in parse_result["text"]:
            print(f"❌ File parsing error: {parse_result['text']}")
            raise HTTPException(status_code=400, detail=f"Error parsing file: {parse_result['text']}")
        
        print(f"✅ File parsing complete - content length: {len(parse_result['text'])}")
        
        # Store file upload record with parsed content
        file_upload = FileUpload(
            filename=file.filename,
            file_type=file_type,
            file_size=len(content),
            intent=intent or "auto",
            processed=True,
            content=parse_result["text"]  # Store the parsed content
        )
        
        db.add(file_upload)
        db.commit()
        db.refresh(file_upload)
        print(f"💾 File record stored in database - ID: {file_upload.id}")
        
        # Optional: Create embeddings if available
        embedding_success = False
        if enhanced_embedding_manager.is_available():
            try:
                print(f"🔄 Creating embeddings...")
                embedding_success = await enhanced_embedding_manager.embed_file_content(
                    content=parse_result["text"], 
                    filename=file.filename,
                    file_type=file_type
                )
                if embedding_success:
                    print(f"✅ Embedding creation successful")
                else:
                    print(f"⚠️ Embedding creation failed")
            except Exception as e:
                print(f"⚠️ Embedding error (non-critical): {e}")
        
        # Prepare response
        summary = f"Successfully parsed {file.filename}. {parse_result['preview']}"
        if embedding_success:
            summary += f" Content has been embedded for enhanced search."
        
        # Generate a simple confirmation prompt
        confirmation_prompt = f"File '{file.filename}' has been parsed successfully. You can now chat about its contents."
        
        # Prepare extracted data
        extracted_data = {
            "file_type": file_type,
            "size": len(content),
            "text_length": len(parse_result["text"]),
            "preview": parse_result["preview"],
            "embedded": embedding_success,
            "upload_id": file_upload.id
        }
        
        print(f"✅ File upload successful: {file.filename}")
        print(f"📤 === UPLOAD COMPLETE ===\n")
        
        return FileUploadResponse(
            filename=file.filename,
            file_type=file_type,
            suggested_intent="chat_about_file",
            summary=summary,
            confirmation_prompt=confirmation_prompt,
            extracted_data=extracted_data,
            needs_confirmation=False  # No confirmation needed for simple parsing
        )
        
    except HTTPException:
        raise
    except Exception as e:
        # Clean up file record if created
        if 'file_upload' in locals():
            try:
                db.delete(file_upload)
                db.commit()
                print(f"🗑️ Cleaned up file record due to error")
            except:
                pass
        
        print(f"❌ File upload error: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@router.get("/history")
async def get_upload_history(
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get file upload history"""
    
    try:
        files = db.query(FileUpload).order_by(FileUpload.uploaded_at.desc()).limit(limit).all()
        
        return {
            "files": [
                {
                    "id": file.id,
                    "filename": file.filename,
                    "file_type": file.file_type,
                    "file_size": file.file_size,
                    "intent": file.intent,
                    "processed": file.processed,
                    "uploaded_at": file.uploaded_at.isoformat()
                }
                for file in files
            ]
        }
    except Exception as e:
        print(f"❌ Error getting upload history: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving upload history: {str(e)}")

@router.get("/embedding-stats")
async def get_embedding_stats():
    """Get embedding statistics."""
    try:
        stats = enhanced_embedding_manager.get_stats()
        
        # Extract relevant information for the frontend
        local_stats = stats.get("local_stats", {})
        supabase_stats = stats.get("supabase_stats", {})
        
        # Combine stats from both sources
        total_chunks = local_stats.get("total_chunks", 0) + supabase_stats.get("total_embeddings", 0)
        unique_sources = local_stats.get("unique_sources", 0) + supabase_stats.get("unique_documents", 0)
        has_vector_store = local_stats.get("has_vector_store", False) or supabase_stats.get("total_embeddings", 0) > 0
        
        # Combine sources from both
        sources = local_stats.get("sources", [])
        if "file_types_distribution" in supabase_stats:
            sources.extend(list(supabase_stats["file_types_distribution"].keys()))
        
        return {
            "embedding_available": stats.get("openai_available", False),
            "total_chunks": total_chunks,
            "has_vector_store": has_vector_store,
            "unique_sources": unique_sources,
            "sources": list(set(sources)),  # Remove duplicates
            "supabase_available": stats.get("supabase_available", False),
            "local_available": stats.get("local_available", False),
            "supabase_stats": supabase_stats,
            "local_stats": local_stats
        }
    except Exception as e:
        print(f"❌ Error getting embedding stats: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving embedding stats: {str(e)}")