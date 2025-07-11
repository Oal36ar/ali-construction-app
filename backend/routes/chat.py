#!/usr/bin/env python3
"""
Chat API Routes
Enhanced with multi-modal support for text, files, and images
"""

import json
import asyncio
from typing import Optional, List, AsyncGenerator
from fastapi import APIRouter, HTTPException, Depends, Form, File, UploadFile, Request
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy.orm import Session
from pydantic import ValidationError

from utils.database import get_db
from schemas.chat import ChatRequest, DebugChatRequest
from schemas.response import ChatResponse, MultimodalChatResponse
from agents.orchestrator_agent import agent_manager
from utils.file_parser import parse_file_by_type, detect_file_type
from utils.embedding_manager import embedding_manager

router = APIRouter()

# Try to import LLM orchestrator if available
try:
    from services.llm_orchestrator import LLMOrchestrator
    llm_orchestrator = LLMOrchestrator()
    HAS_LLM_ORCHESTRATOR = True
except ImportError:
    print("⚠️ LLM Orchestrator not available in chat routes")
    HAS_LLM_ORCHESTRATOR = False

async def log_request_details(request: Request, endpoint_name: str):
    """Log detailed request information for debugging"""
    print(f"\n🔍 === {endpoint_name} REQUEST DEBUG ===")
    print(f"📍 Endpoint: {request.url.path}")
    print(f"🔧 Method: {request.method}")
    print(f"📋 Headers: {dict(request.headers)}")
    print(f"🔗 Query params: {dict(request.query_params)}")
    
    # Try to log body if possible
    try:
        content_type = request.headers.get("content-type", "")
        print(f"📄 Content-Type: {content_type}")
        
        if "application/json" in content_type:
            body = await request.body()
            if body:
                try:
                    body_json = json.loads(body.decode('utf-8'))
                    print(f"📝 Request JSON payload:")
                    print(json.dumps(body_json, indent=2))
                except:
                    print(f"📝 Request body (raw): {body.decode('utf-8', errors='ignore')[:500]}...")
        else:
            print(f"📄 Request type: {content_type} (body not logged)")
    except Exception as e:
        print(f"⚠️ Could not log request body: {e}")
    
    print(f"🔍 === END {endpoint_name} DEBUG ===\n")

async def process_uploaded_files(files: List[UploadFile]) -> str:
    """
    Process uploaded files and return their parsed content as text
    
    Args:
        files: List of uploaded files
        
    Returns:
        Formatted string with all file contents
    """
    if not files:
        return ""
    
    file_contents = []
    
    for i, file in enumerate(files):
        try:
            print(f"📄 Processing file {i+1}: {file.filename}")
            
            # Read file content
            content = await file.read()
            
            # Validate file size (10MB limit)
            MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
            if len(content) > MAX_FILE_SIZE:
                file_contents.append(f"[File {file.filename}: Too large (max 10MB)]")
                continue
            
            if len(content) == 0:
                file_contents.append(f"[File {file.filename}: Empty file]")
                continue
            
            # Detect and parse file
            file_type = detect_file_type(file.filename, file.content_type)
            
            if file_type == "unknown":
                # Try to decode as text
                try:
                    text_content = content.decode('utf-8')[:1000]
                    file_contents.append(f"=== File: {file.filename} (Text) ===\n{text_content}\n")
                except:
                    file_contents.append(f"[File {file.filename}: Unsupported file type]")
                continue
            
            # Parse the file
            parse_result = parse_file_by_type(file.filename, content)
            
            if "Error parsing" not in parse_result["text"]:
                file_contents.append(f"=== File: {file.filename} ({file_type.upper()}) ===")
                file_contents.append(f"Preview: {parse_result['preview']}")
                file_contents.append(f"Content:\n{parse_result['text']}")
                file_contents.append("=" * 50)
                
                # Optionally create embeddings for future retrieval
                if embedding_manager.is_available():
                    try:
                        embedding_manager.embed_file_content(parse_result["text"], file.filename)
                        print(f"✅ Created embeddings for {file.filename}")
                    except Exception as e:
                        print(f"⚠️ Embedding error for {file.filename}: {e}")
                        
            else:
                file_contents.append(f"[File {file.filename}: {parse_result['text']}]")
                
        except Exception as e:
            print(f"❌ Error processing file {file.filename}: {e}")
            file_contents.append(f"[File {file.filename}: Error processing - {str(e)}]")
    
    return "\n\n".join(file_contents)

async def enhance_message_with_context(message: str, files: List[UploadFile] = None) -> str:
    """
    Enhance user message with file content and optionally with embedding retrieval
    
    Args:
        message: Original user message
        files: Optional uploaded files
        
    Returns:
        Enhanced message with context
    """
    enhanced_parts = []
    
    # Add file content if files are uploaded
    if files:
        print(f"🔄 Processing {len(files)} uploaded files...")
        file_content = await process_uploaded_files(files)
        if file_content:
            enhanced_parts.append(file_content)
    
    # Add embedding-based context if available and no files uploaded
    if not files and embedding_manager.is_available() and embedding_manager.vector_store is not None:
        try:
            retrieval_context = embedding_manager.get_retrieval_context(message, max_chunks=3)
            if retrieval_context:
                enhanced_parts.append(retrieval_context)
                print(f"✅ Added embedding-based context")
        except Exception as e:
            print(f"⚠️ Error retrieving context: {e}")
    
    # Combine all parts
    if enhanced_parts:
        enhanced_parts.append(f"User message: {message}")
        return "\n\n".join(enhanced_parts)
    else:
        return message

async def mock_llm_response(message: str, files: List = None) -> dict:
    """Mock LLM response when orchestrator is not available"""
    file_info = f" (with {len(files)} files)" if files else ""
    return {
        "response": f"Mock response for: {message[:50]}...{file_info}",
        "model": "mock-model",
        "plugin": None,
        "input_type": "file" if files else "text",
        "processed_files": len(files) if files else 0,
        "success": True
    }

@router.post("/chat", response_model=MultimodalChatResponse)
async def chat_main(
    request: Request,
    message: str = Form(...),
    files: Optional[List[UploadFile]] = File(None),
    session_id: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Main chat endpoint that handles both text-only and file uploads
    Routes automatically to appropriate OpenRouter model:
    - Text-only messages → google/gemini-2.5-flash
    - Messages with files → google/gemma-3-27b-it with file-parser plugin
    """
    
    # ===== COMPREHENSIVE LOGGING =====
    print(f"\n🚀 === CHAT ENDPOINT HIT ===")
    print(f"📝 Incoming message: '{message[:100]}...' (length: {len(message) if message else 0})")
    print(f"📁 Files count: {len(files) if files else 0}")
    print(f"🔗 Session ID: {session_id or 'None'}")
    print(f"🌐 Request from: {request.client.host if request.client else 'Unknown'}")
    
    if files:
        for i, file in enumerate(files):
            print(f"  📄 File {i+1}: {file.filename} ({file.content_type})")
    
    try:
        # Log detailed request information for debugging
        await log_request_details(request, "MAIN CHAT")
        
        print(f"\n💬 === MAIN CHAT PROCESSING ===")
        print(f"📝 Message: '{message[:100]}...' (length: {len(message) if message else 0})")
        print(f"📁 Files count: {len(files) if files else 0}")
        print(f"🔗 Session ID: {session_id or 'None'}")
        
        # Validate message
        if not message or not message.strip():
            print(f"❌ Empty message validation failed")
            return JSONResponse(
                status_code=400,
                content={
                    "error": True,
                    "reason": "Message is required", 
                    "detail": "Please provide a non-empty message"
                }
            )
        
        # ===== ENHANCE MESSAGE WITH FILE CONTENT AND CONTEXT =====
        enhanced_message = await enhance_message_with_context(message.strip(), files)
        
        if enhanced_message != message.strip():
            print(f"✅ Enhanced message with file content and/or context")
            print(f"📊 Enhanced message length: {len(enhanced_message)}")
        
        # ===== MODEL SELECTION AND LOGGING =====
        current_model = "mock-model"
        if HAS_LLM_ORCHESTRATOR:
            try:
                from llm.openrouter_llm import OpenRouterLLM
                llm = OpenRouterLLM()
                current_model = llm.text_model if not files else llm.file_model
                print(f"🤖 Using model: {current_model}")
                print(f"🔧 LLM Orchestrator: Available")
            except Exception as e:
                print(f"⚠️ Model loading error: {e}")
                current_model = "error-loading-model"
        else:
            print(f"🤖 Using model: {current_model} (mock mode)")
            print(f"🔧 LLM Orchestrator: Not Available")
        
        # Process the enhanced message
        try:
            if HAS_LLM_ORCHESTRATOR:
                print(f"🔄 Processing with LLM Orchestrator...")
                # Use enhanced message instead of original
                result = await llm_orchestrator.process_message(
                    message=enhanced_message,
                    files=[],  # Files already processed into message content
                    session_id=session_id
                )
                print(f"✅ LLM Orchestrator result received")
            else:
                print(f"🔄 Processing with mock response...")
                result = await mock_llm_response(enhanced_message, files)
                print(f"✅ Mock response generated")
            
            # ===== RESPONSE LOGGING =====
            print(f"📊 LLM result summary:")
            print(f"  Model: {result.get('model', 'unknown')}")
            print(f"  Input type: {result.get('input_type', 'unknown')}")
            print(f"  Response length: {len(result.get('response', ''))}")
            print(f"  Success: {result.get('success', False)}")
            print(f"  Response preview: '{result.get('response', '')[:100]}...'")
            
            # Handle successful response
            if result.get("success", True):
                response_data = {
                    "response": result.get("response", "No response generated"),
                    "model": result.get("model", current_model),
                    "plugin": result.get("plugin"),
                    "input_type": result.get("input_type", "file" if files else "text"),
                    "processed_files": len(files) if files else result.get("processed_files", 0),
                    "session_id": session_id,
                    "success": True
                }
                
                # Add file previews if available
                if files:
                    file_previews = [f"{file.filename} ({file.content_type})" for file in files]
                    response_data["file_previews"] = file_previews
                elif "file_previews" in result:
                    response_data["file_previews"] = result["file_previews"]
                
                print(f"✅ Chat success - returning response")
                print(f"🚀 === CHAT ENDPOINT COMPLETE ===\n")
                return MultimodalChatResponse(**response_data)
            
            # Handle error response
            else:
                error_detail = result.get("error", "Unknown error occurred")
                print(f"❌ LLM orchestrator error: {error_detail}")
                print(f"🚀 === CHAT ENDPOINT COMPLETE (ERROR) ===\n")
                
                return JSONResponse(
                    status_code=500,
                    content={
                        "error": True,
                        "reason": "LLM processing failed",
                        "detail": error_detail,
                        "response": result.get("response", "I encountered an error processing your request"),
                        "session_id": session_id
                    }
                )
                
        except ValidationError as e:
            print(f"❌ Validation error in main chat: {e}")
            print(f"🚀 === CHAT ENDPOINT COMPLETE (VALIDATION ERROR) ===\n")
            return JSONResponse(
                status_code=400,
                content={
                    "error": True,
                    "reason": "Agent input format invalid",
                    "detail": f"LangChain OpenRouterLLM rejected unexpected field: {e}",
                    "session_id": session_id
                }
            )
        except Exception as e:
            print(f"❌ Unexpected error in main chat: {e}")
            print(f"❌ Exception type: {type(e).__name__}")
            print(f"❌ Exception details: {str(e)}")
            print(f"🚀 === CHAT ENDPOINT COMPLETE (UNEXPECTED ERROR) ===\n")
            return JSONResponse(
                status_code=500,
                content={
                    "error": True,
                    "reason": "Internal server error",
                    "detail": str(e),
                    "session_id": session_id
                }
            )
            
    except Exception as e:
        print(f"❌ Main chat endpoint error: {e}")
        print(f"❌ Exception type: {type(e).__name__}")
        print(f"❌ Exception details: {str(e)}")
        print(f"🚀 === CHAT ENDPOINT COMPLETE (ENDPOINT ERROR) ===\n")
        return JSONResponse(
            status_code=500,
            content={
                "error": True,
                "reason": "Endpoint error",
                "detail": str(e),
                "session_id": session_id
            }
        )

@router.post("/chat/test/debug")
async def debug_chat_endpoint(request: Request, payload: Optional[DebugChatRequest] = None):
    """
    Debug endpoint that accepts any payload and echoes back what FastAPI receives
    Helps trace which field is triggering 422 validation errors
    """
    try:
        # Log detailed request information
        await log_request_details(request, "DEBUG CHAT")
        
        print(f"\n🔧 === DEBUG CHAT ENDPOINT ===")
        print(f"📦 Received payload type: {type(payload)}")
        
        # Log the parsed payload
        if payload:
            payload_dict = payload.dict()
            print(f"📋 Parsed payload fields:")
            for field, value in payload_dict.items():
                if value is not None:
                    print(f"  ✅ {field}: {type(value)} = {repr(value)[:100]}")
                else:
                    print(f"  ❌ {field}: None")
        else:
            print(f"📋 No payload received or failed to parse")
        
        # Echo back what we received
        response_data = {
            "debug_info": {
                "endpoint": "/chat/test/debug",
                "method": request.method,
                "content_type": request.headers.get("content-type"),
                "payload_received": payload.dict() if payload else None,
                "validation_status": "✅ Payload successfully validated" if payload else "❌ No valid payload received"
            },
            "help": {
                "message": "Use this endpoint to test your payload structure",
                "example_json": {
                    "message": "Your chat message here",
                    "session_id": "optional_session_id",
                    "context": "optional_context",
                    "model": "optional_model_name"
                },
                "example_form": "Use form-data with message=your_message&session_id=optional_id"
            }
        }
        
        print(f"✅ Debug response prepared")
        print(f"🔧 === END DEBUG CHAT ===\n")
        
        return JSONResponse(
            status_code=200,
            content=response_data
        )
        
    except Exception as e:
        print(f"❌ Debug endpoint error: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "debug_info": {
                    "endpoint": "/chat/test/debug",
                    "error": str(e),
                    "validation_status": "❌ Error in debug endpoint"
                },
                "help": "This debug endpoint encountered an error while processing your request"
            }
        )

@router.get("/tools/available")
async def get_available_tools(db: Session = Depends(get_db)):
    """Get information about all available tools"""
    try:
        from tools.tool_registry import create_tool_registry
        
        tools = create_tool_registry()
        return {
            "available_tools": [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "type": "LangChain Tool"
                } for tool in tools
            ],
            "tool_count": len(tools),
            "status": "✅ Tools loaded successfully"
        }
    except ImportError:
        # Return mock tools if registry not available
        return {
            "available_tools": [
                {"name": "file_parser", "description": "Parse and analyze uploaded files", "type": "Built-in"},
                {"name": "reminder_creator", "description": "Create and manage reminders", "type": "Built-in"},
                {"name": "email_sender", "description": "Send email notifications", "type": "Built-in"}
            ],
            "tool_count": 3,
            "status": "⚠️ Using mock tools (LangChain not available)"
        }
    except Exception as e:
        print(f"❌ Error getting tools: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving tools: {str(e)}") 