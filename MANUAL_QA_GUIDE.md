# 🧪 **Manual QA Testing Guide for FastAPI Backend**

## **Prerequisites Setup**

### 1. Environment Variables
Create a `.env` file in the `backend/` directory:
```bash
OPENROUTER_API_KEY=sk-or-your-actual-key-here
OPENAI_API_KEY=sk-proj-your-actual-key-here
DEBUG=True
```

### 2. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 3. Start Backend (PowerShell)
```powershell
cd backend
python main.py
```

Expected output:
```
[OK] Database models loaded
[OK] LangChain Orchestrator loaded
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000
```

---

## **🧪 Test Suite Execution**

### **Test 1: Basic Connectivity**

**Root Endpoint:**
```bash
curl http://localhost:8000/
```

**Expected Response:**
```json
{
  "message": "🤖 AI Orchestrator API",
  "version": "1.0.0",
  "status": "operational",
  "endpoints": {
    "chat": "/chat",
    "upload": "/upload", 
    "health": "/health"
  }
}
```

**Health Check:**
```bash
curl http://localhost:8000/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "services": {
    "database": "connected",
    "llm": "connected",
    "langchain": "available"
  }
}
```

### **Test 2: File Upload Testing**

**Upload Text File:**
```bash
curl -X POST "http://localhost:8000/upload/" \
  -F "file=@test_files/test.txt" \
  -F "intent=auto"
```

**Expected Response:**
```json
{
  "filename": "test.txt",
  "file_type": "text",
  "suggested_intent": "chat_about_file",
  "summary": "Successfully parsed test.txt. 15 lines, 3 paragraphs, 0 tables",
  "confirmation_prompt": "File 'test.txt' has been parsed successfully. You can now chat about its contents.",
  "extracted_data": {
    "file_type": "text",
    "size": 500,
    "text_length": 400,
    "preview": "15 lines, 3 paragraphs, 0 tables",
    "embedded": true
  },
  "needs_confirmation": false
}
```

**Upload CSV File:**
```bash
curl -X POST "http://localhost:8000/upload/" \
  -F "file=@test_files/test.csv" \
  -F "intent=auto"
```

**Expected Response:**
```json
{
  "filename": "test.csv",
  "file_type": "csv",
  "summary": "Successfully parsed test.csv. 10 rows, 5 columns",
  "preview": "10 rows, 5 columns"
}
```

### **Test 3: Embedding Statistics**

**Check Embedding Stats:**
```bash
curl http://localhost:8000/upload/embedding-stats
```

**Expected Response:**
```json
{
  "embedding_available": true,
  "total_chunks": 8,
  "has_vector_store": true,
  "unique_sources": 2,
  "sources": ["test.txt", "test.csv"]
}
```

### **Test 4: Chat Functionality**

**Simple Chat:**
```bash
curl -X POST "http://localhost:8000/chat" \
  -F "message=Hello, how are you?" \
  -F "session_id=test_session"
```

**Expected Response:**
```json
{
  "response": "Hello! I'm doing well, thank you for asking. I'm an AI assistant that can help you with file analysis, reminders, and general questions. How can I assist you today?",
  "model": "google/gemini-2.5-flash",
  "input_type": "text",
  "processed_files": 0,
  "session_id": "test_session",
  "success": true
}
```

**Chat with Context Retrieval:**
```bash
curl -X POST "http://localhost:8000/chat" \
  -F "message=What information is in the uploaded documents?" \
  -F "session_id=test_session"
```

**Expected Response:**
```json
{
  "response": "Based on the uploaded documents, I can see information about:\n=== RELEVANT FILE CONTEXT ===\n[Context 1 from test.txt]\nOmar visa renewal: 2027-11-20\nProject deadline: 2024-02-15\n...",
  "model": "google/gemini-2.5-flash",
  "input_type": "text",
  "success": true
}
```

### **Test 5: Chat with File Upload**

**Chat with Attached File:**
```bash
curl -X POST "http://localhost:8000/chat" \
  -F "message=What reminders are in this document?" \
  -F "files=@test_files/reminder_doc.txt" \
  -F "session_id=test_file_session"
```

**Expected Response:**
```json
{
  "response": "I found several reminders in the document:\n=== File: reminder_doc.txt (TXT) ===\nPreview: 1 lines extracted\nContent: Important: Omar visa renewal due on 2027-11-20. Please prepare documents.\n\nUser message: What reminders are in this document?\n\nBased on the document, I can see one important reminder: Omar's visa renewal is due on November 20th, 2027. This appears to be a high-priority item that requires document preparation.",
  "model": "google/gemma-3-27b-it", 
  "input_type": "file",
  "processed_files": 1,
  "file_previews": ["reminder_doc.txt (application/octet-stream)"],
  "success": true
}
```

### **Test 6: Reminder Extraction**

**Upload File with Reminder Data:**
```bash
curl -X POST "http://localhost:8000/chat" \
  -F "message=Create a reminder for Omar visa renewal on 2027-11-20" \
  -F "session_id=test_reminder"
```

**Expected Response:**
```json
{
  "response": "I'll help you set up a reminder for Omar's visa renewal. I can see the date is November 20th, 2027. Would you like me to create a reminder for this important deadline?",
  "model": "google/gemini-2.5-flash",
  "success": true
}
```

### **Test 7: History Endpoints**

**Upload History:**
```bash
curl http://localhost:8000/upload/history
```

**Activity History:**
```bash
curl http://localhost:8000/history/activity
```

**Available Tools:**
```bash
curl http://localhost:8000/tools/available
```

---

## **🎯 Production Readiness Checklist**

### ✅ **Core Functionality**
- [ ] **Backend starts without errors**
- [ ] **Health endpoint returns 200**
- [ ] **File uploads parse correctly (PDF, CSV, DOCX, XLSX, TXT)**
- [ ] **Chat responds to basic queries**
- [ ] **File content integrated into chat messages**

### ✅ **Advanced Features**
- [ ] **Embeddings created and stored**
- [ ] **Context retrieval from previous uploads**
- [ ] **Multi-file chat sessions**
- [ ] **Reminder extraction from content**
- [ ] **History tracking functional**

### ✅ **LLM Routing**
- [ ] **Text-only → google/gemini-2.5-flash**
- [ ] **Files attached → google/gemma-3-27b-it**
- [ ] **Fallback to mock responses if API unavailable**

### ✅ **Error Handling**
- [ ] **Graceful parsing errors**
- [ ] **File size limits enforced (10MB)**
- [ ] **Unsupported file types handled**
- [ ] **Network errors don't crash server**

---

## **🚀 Expected Results Summary**

When all tests pass, you should see:

1. **File uploads → parsed cleanly** ✅
   - Text, CSV, PDF, DOCX, XLSX all supported
   - Clean text extraction with metadata

2. **Embeddings → created and stored** ✅
   - FAISS vector store populated
   - Semantic search functional

3. **Chat → contextually answers with embedded docs** ✅
   - Previous uploads accessible in chat
   - Context prepended to user messages

4. **Reminders → extracted and logged** ✅
   - Date detection in uploaded content
   - Integration with reminder system

5. **History → tracks all events** ✅
   - Upload history maintained
   - Chat activity logged

---

## **🔧 Troubleshooting**

### Common Issues:

1. **Backend won't start**
   - Check `.env` file encoding (UTF-8)
   - Verify Python dependencies installed
   - Check port 8000 availability

2. **File uploads fail**
   - Verify file size < 10MB
   - Check file permissions
   - Ensure proper multipart/form-data headers

3. **Embeddings not working**
   - Verify OPENAI_API_KEY set
   - Check internet connectivity
   - Review backend logs for embedding errors

4. **Chat responses empty**
   - Check OPENROUTER_API_KEY configuration
   - Verify LLM service availability
   - Review fallback mock responses

---

**🎯 Once all tests pass, the backend is production-ready for RAG workflows and Supabase integration!** 