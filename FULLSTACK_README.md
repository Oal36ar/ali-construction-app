# 🏗️ Construction AI - Full Stack Application

A comprehensive AI-powered construction management system with file processing, chat interface, reminders, and activity tracking.

## 🌟 Features

- **📁 File Upload & Processing**: PDF, CSV, DOCX, XLSX support with AI analysis
- **💬 Intelligent Chat**: Context-aware conversations using uploaded files
- **📅 Reminders Management**: Create and track construction deadlines
- **📊 Activity History**: Complete logs of uploads, chats, and actions
- **🔗 Real-time Integration**: Seamless frontend-backend communication

## 🏗️ Architecture

```
Frontend (React + Vite)          Backend (FastAPI + LangChain)
├── Dashboard                 ←→ ├── /health
├── Upload Component          ←→ ├── /upload  
├── Chat Interface            ←→ ├── /chat
├── Reminders Page            ←→ ├── /reminders/all
├── Activity Page             ←→ ├── /history/activity
└── Proxy (localhost:5173)   ←→ └── API (localhost:8000)
```

## 🚀 Quick Start

### Option 1: One-Command Launch ⭐ (Recommended)
```bash
python start_fullstack.py
```
- Automatically starts both services
- Tests all integrations
- Opens browser to the app
- Provides status monitoring

### Option 2: Manual Startup
```bash
# Terminal 1: Backend
cd backend && python main.py

# Terminal 2: Frontend
cd frontend && npm run dev
```

### Option 3: Validate Integration
```bash
python validate_integration.py
```
Runs comprehensive end-to-end tests to verify everything works.

## ⚙️ Configuration

### Backend Requirements
- Python 3.8+
- FastAPI + LangChain
- SQLite database
- OpenRouter/OpenAI API keys (optional - works in mock mode)

### Frontend Requirements  
- Node.js 16+
- React 18 + Vite
- TailwindCSS for styling

### Environment Setup
Create `backend/.env` with your API keys:
```env
OPENROUTER_API_KEY=your_key_here
OPENAI_API_KEY=your_fallback_key
```

## 📋 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | System health check |
| `/startup-check` | GET | Route verification |
| `/upload` | POST | File upload & processing |
| `/chat` | POST | AI chat with context |
| `/reminders/all` | GET | Get all reminders |
| `/history/activity` | GET | Activity logs |

## 🧪 Testing

### Manual Testing Flow
1. **Start Application**: Use `python start_fullstack.py`
2. **Upload File**: Drag a PDF/CSV to the upload zone
3. **Chat Context**: Ask "Summarize the uploaded document"
4. **Check Pages**: Visit `/reminders` and `/activity`
5. **Verify Integration**: All features should work seamlessly

### Automated Testing
```bash
# Backend API tests
cd backend && python tests/test_backend_all.py

# Full integration tests
python validate_integration.py
```

## 📁 Project Structure

```
Construction app/
├── backend/                 # FastAPI backend
│   ├── main.py             # Main application
│   ├── routes/             # API endpoints
│   ├── agents/             # LangChain agents
│   ├── tools/              # AI tools
│   ├── utils/              # Utilities
│   └── tests/              # Backend tests
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Application pages
│   │   ├── services/       # API client
│   │   └── store/          # State management
│   ├── vite.config.ts      # Vite configuration
│   └── package.json        # Dependencies
├── start_fullstack.py      # One-command launcher
├── validate_integration.py # Integration tests
└── FRONTEND_INTEGRATION_GUIDE.md
```

## 🔧 Development

### Adding New Features
1. **Backend**: Add routes in `backend/routes/`
2. **Frontend**: Add components in `frontend/src/components/`
3. **API Integration**: Update `frontend/src/services/apiClient.ts`
4. **Testing**: Add tests to both backend and validation scripts

### Database Schema
- **Reminders**: title, date, time, priority, category
- **Chat History**: session_id, content, timestamp, metadata
- **File Uploads**: filename, type, size, processed status
- **Action Logs**: user actions and system responses

## 🐛 Troubleshooting

### Common Issues

**Port Already in Use**
```bash
# Kill processes on ports 8000/5173
lsof -ti:8000 | xargs kill -9
lsof -ti:5173 | xargs kill -9
```

**Backend Not Starting**
- Check Python version (3.8+ required)
- Install requirements: `pip install -r backend/requirements.txt`
- Check for missing dependencies

**Frontend Not Loading**
- Check Node.js version (16+ required)
- Install dependencies: `cd frontend && npm install`
- Clear cache: `rm -rf node_modules package-lock.json && npm install`

**API Connection Issues**
- Verify backend is running on port 8000
- Check proxy configuration in `vite.config.ts`
- Test direct backend access: `curl http://localhost:8000/health`

### Debug Mode
- **Backend Logs**: Check terminal output for detailed API logs
- **Frontend Logs**: Open browser DevTools → Console
- **Network Issues**: Check DevTools → Network tab

## 🎯 Production Deployment

### Backend
```bash
cd backend
pip install -r requirements.txt
python main.py
```

### Frontend
```bash
cd frontend
npm install
npm run build
npm run preview
```

### Environment Variables
- Set `OPENROUTER_API_KEY` for AI features
- Configure `DATABASE_URL` for production database
- Set `CORS_ORIGINS` for production domains

## 🌟 Key Features Explained

### File Processing
- **Upload**: Drag & drop or file picker
- **Parsing**: PDF, CSV, DOCX, XLSX support
- **Analysis**: AI-powered content extraction
- **Storage**: Database + embedding storage for search

### AI Chat
- **Context Aware**: References uploaded files
- **Streaming**: Real-time response streaming
- **History**: Persistent conversation history
- **Tools**: Reminder creation, file analysis

### Reminders
- **Creation**: From chat or manual entry
- **Priority**: High, medium, low levels
- **Categories**: Flexible categorization
- **Completion**: Track completion status

### Activity Tracking
- **Uploads**: File processing history
- **Chats**: Conversation logs
- **Actions**: System actions and responses
- **Analytics**: Usage patterns and statistics

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License.

## 📞 Support

For questions or issues:
- Check the troubleshooting section
- Run `python validate_integration.py` for diagnostics
- Review browser console and backend logs
- Open an issue with detailed error information

---

## 🚀 Ready to Start?

```bash
# Clone and start in one command
python start_fullstack.py
```

Your application will be running at:
- **Frontend**: http://localhost:5173
- **Backend**: http://localhost:8000

Happy building! 🏗️✨ 