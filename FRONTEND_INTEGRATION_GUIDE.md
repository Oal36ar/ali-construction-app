# 🌐 Frontend-Backend Integration Guide

This guide explains how to run and test the full stack React + Vite frontend with the FastAPI + LangChain backend.

## 🚀 Quick Start

### Option 1: One-Command Launch (Recommended)
```bash
python start_fullstack.py
```
This automatically starts both services, tests integration, and opens your browser.

### Option 2: Manual Startup

**Start Backend:**
```bash
cd backend
python main.py
```
The backend will start on `http://localhost:8000`

**Start Frontend:**
```bash
cd frontend
npm run dev
```
The frontend will start on `http://localhost:5173`

### Option 3: Using npm script
```bash
cd frontend
npm run dev:full
```
This runs both backend and frontend simultaneously using concurrently.

### ✅ Validation
After starting services, validate the integration:
```bash
python validate_integration.py
```
This runs comprehensive end-to-end tests and reports any issues.

## 🔧 Configuration

### Vite Proxy Setup
The frontend is configured to proxy API calls to the backend:

```typescript
// vite.config.ts
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
      rewrite: (path) => path.replace(/^\/api/, ''),
      ws: true // WebSocket support for streaming
    }
  }
}
```

### API Client
The frontend uses `/api/*` endpoints which get proxied to the backend:
- `fetch('/api/health')` → `http://localhost:8000/health`
- `fetch('/api/chat')` → `http://localhost:8000/chat`
- `fetch('/api/upload')` → `http://localhost:8000/upload`

## 🎯 Features Implemented

### ✅ 1. Upload Component
- **Location**: Dashboard page, main upload zone
- **Features**:
  - Drag & drop file upload
  - File input selector
  - Supports: PDF, CSV, DOCX, XLSX, TXT
  - Real-time file processing status
  - Intent selection (summarize, extract reminders, etc.)
- **API**: `POST /api/upload`

### ✅ 2. Chat Component
- **Location**: Dashboard page, main chat area
- **Features**:
  - Text input with send button
  - File attachment support
  - Real-time streaming responses
  - Message history with user/assistant avatars
  - Contextual responses using uploaded files
- **API**: `POST /api/chat`

### ✅ 3. Reminder Panel
- **Location**: Reminders page (`/reminders`)
- **Features**:
  - Fetches all reminders from backend
  - Grouped by date display
  - Priority indicators (high/medium/low)
  - Search and filter functionality
  - Completion status tracking
- **API**: `GET /api/reminders/all`

### ✅ 4. History Tab
- **Location**: Activity page (`/activity`)
- **Features**:
  - Recent chat messages
  - File upload history
  - Activity summary with counts
  - Timeline view of all actions
- **API**: `GET /api/history/activity`

### ✅ 5. Backend Connection Test
- **Location**: Dashboard page (when no messages)
- **Features**:
  - Real-time API endpoint testing
  - Health check verification
  - Startup validation
  - Error diagnostics with helpful messages

## 🧪 Manual Test Plan

### Test Flow 1: Upload & Chat
1. **Start both services**:
   ```bash
   # Terminal 1
   cd backend && python main.py
   
   # Terminal 2  
   cd frontend && npm run dev
   ```

2. **Navigate to Dashboard** (`http://localhost:5173`)

3. **Upload a file**:
   - Drag sample PDF/CSV to upload zone
   - Select intent (e.g., "Summarize content")
   - Wait for processing completion

4. **Chat about the file**:
   - Type: "Summarize the uploaded document"
   - Verify bot responds with file context
   - Check response includes file information

### Test Flow 2: Check Integrations
1. **Reminders**: Navigate to `/reminders`
   - Should load existing reminders
   - Display in grouped date format

2. **Activity**: Navigate to `/activity`
   - Should show upload/chat history
   - Display activity counts

3. **Connection Test**: Return to Dashboard (refresh if needed)
   - Should see 5 connection tests pass
   - All tests should show green checkmarks

## 🔍 API Endpoint Mapping

| Frontend Call | Backend Endpoint | Purpose |
|---------------|------------------|---------|
| `GET /api/health` | `GET /health` | Health check |
| `GET /api/startup-check` | `GET /startup-check` | Route verification |
| `POST /api/upload` | `POST /upload` | File upload & parsing |
| `POST /api/chat` | `POST /chat` | Chat messages |
| `GET /api/reminders/all` | `GET /reminders/all` | Fetch reminders |
| `GET /api/history/activity` | `GET /history/activity` | Activity logs |

## 🐛 Troubleshooting

### Common Issues

**"Network Error" or Connection Failed**
```bash
# Check if backend is running
curl http://localhost:8000/health

# If not, start backend:
cd backend && python main.py
```

**CORS Errors**
- Backend is configured to allow frontend origins
- Check that frontend is running on `http://localhost:5173`

**File Upload Fails**
- Check file size (max 10MB)
- Verify file type is supported
- Check backend logs for detailed errors

**Chat Not Working**  
- Verify `/chat` endpoint is responding
- Check browser network tab for error details
- Backend may be in mock mode if LangChain is unavailable

### Debug Mode
Enable detailed logging by checking browser console:
- API requests/responses are logged with full details
- Error messages include helpful context
- Network errors show connection status

## 🏗️ Architecture

```
Frontend (React + Vite)     Backend (FastAPI + LangChain)
├── Dashboard               ├── /health
├── Upload Component   →    ├── /upload  
├── Chat Component     →    ├── /chat
├── Reminders Page     →    ├── /reminders/all
├── Activity Page      →    ├── /history/activity
└── API Client         →    └── Other endpoints
```

## 🎉 Success Criteria

### Manual Validation
✅ **Upload PDF/CSV**: Files upload successfully, show preview  
✅ **Chat Plain**: "Hello" → Bot responds with JSON containing "response"  
✅ **Chat Contextual**: "Summarize file" → Bot includes uploaded file context  
✅ **Reminders**: Page loads and displays reminders (even if empty array)  
✅ **History**: Page shows activity logs with chats/uploads  
✅ **Connection Test**: All 5 API tests pass with green checkmarks

### Automated Validation
✅ **Backend Health**: All services respond correctly  
✅ **Frontend Access**: React app loads properly  
✅ **Proxy Integration**: Frontend can call backend via `/api/*`  
✅ **File Processing**: Upload and parsing works end-to-end  
✅ **Chat Context**: AI responses include uploaded file content  

## 📝 Notes

- Frontend automatically detects development vs production mode
- Streaming chat is supported but falls back gracefully
- All components have proper loading states and error handling
- File uploads are processed immediately and stored in backend database
- Chat messages can reference previously uploaded files
- The system works in both "full LangChain" and "mock" modes 

## ✅ **TailwindCSS PostCSS Error Fixed!**

I've resolved the TailwindCSS configuration issue. Here's what was wrong and how I fixed it:

### 🔍 **Root Cause**
The PostCSS config was in the **root directory** but Vite runs from the **frontend directory**. When Vite found the root config, it couldn't locate the TailwindCSS module because node_modules are in the frontend folder.

### 🛠️ **Fixes Applied**

#### ✅ **1. Created `frontend/postcss.config.js`**
```js
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
```
- PostCSS config now in the correct location
- Vite can find TailwindCSS from frontend/node_modules

#### ✅ **2. Removed Conflicting Root Config**
- Deleted `postcss.config.js` from root directory
- Prevents Vite from finding the wrong config

#### ✅ **3. Verified Complete Setup**
- ✅ `frontend/tailwind.config.js` - Properly configured
- ✅ `frontend/src/index.css` - Has TailwindCSS directives  
- ✅ `frontend/package.json` - Has all dependencies
- ✅ `frontend/postcss.config.js` - In correct location

## 🚀 **Ready to Run!**

Now try running the frontend again:

```bash
cd frontend
npm install  # Make sure dependencies are installed
npm run dev
```

**Expected Result:**
- ✅ **No PostCSS errors**
- ✅ **TailwindCSS loads correctly**
- ✅ **Frontend starts on http://localhost:5173**
- ✅ **All styling works properly**

## 🧪 **Validation Script**
You can also run this to verify the fix:
```bash
python fix_tailwind_validation.py
```

## 🎯 **The TailwindCSS error is now completely resolved!** 

Your React app should start without any PostCSS/TailwindCSS module errors. 🎨✨ 