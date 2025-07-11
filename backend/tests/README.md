# Backend Integration Tests

This directory contains comprehensive integration tests for the FastAPI + LangChain backend.

## Files

- `test_backend_all.py` - Main test script
- `sample.pdf` - Sample PDF file for upload testing
- `sample.csv` - Sample CSV file for upload testing

## Usage

1. **Start the backend first:**
   ```bash
   cd backend
   python main.py
   ```

2. **Run the tests:**
   ```bash
   cd backend
   python tests/test_backend_all.py
   ```

## What Gets Tested

✅ **Health Check** - `GET /health` → 200  
✅ **Startup Check** - `GET /startup-check` → 200 with `"all_routes_ready": true`  
✅ **Upload PDF** - `POST /upload` with sample PDF → returns `parsed` and `preview`  
✅ **Upload CSV** - `POST /upload` with CSV → returns rows as parsed text  
✅ **Chat Plain** - `POST /chat` with `message: Hello` → returns JSON with `"response"`  
✅ **Chat Contextual** - After upload, send `"Summarize..."` → response includes context  
✅ **Reminders** - `GET /reminders/all` → returns list or empty array  
✅ **History** - `GET /history/activity` → returns chat/upload logs  

## Expected Output

```bash
🧪 Backend Integration Test
🌐 Target URL: http://localhost:8000
📁 Test files directory: /path/to/backend/tests
============================================================
🚀 Starting comprehensive backend integration tests...

🔍 Testing Health Check...
✅ PASS /health

🚀 Testing Startup Check...
✅ PASS /startup-check

📄 Testing Upload PDF...
✅ PASS /upload (PDF)

📊 Testing Upload CSV...
✅ PASS /upload (CSV)

💬 Testing Chat (Plain)...
✅ PASS /chat (plain)

🗨️  Testing Chat (Contextual)...
✅ PASS /chat (context)

📋 Testing Reminders...
✅ PASS /reminders/all

📚 Testing History...
✅ PASS /history/activity

============================================================
🧪 TEST SUMMARY
============================================================
✅ Health Check
✅ Startup Check
✅ Upload PDF
✅ Upload CSV
✅ Chat Plain
✅ Chat Contextual
✅ Reminders
✅ History

📊 RESULTS: 8/8 tests passed
🎉 ALL TESTS PASSED
```

## Requirements

The test script uses only Python standard library plus `requests`:

```bash
pip install requests
```

## Troubleshooting

- **"Backend not accessible"** - Make sure `python main.py` is running in the backend directory
- **File not found errors** - Make sure you're running from the backend directory
- **Import errors** - The script adds the backend directory to the Python path automatically 