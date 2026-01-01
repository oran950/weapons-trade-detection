# 🚨 Weapons Trade Detection System

> **Academic Research Project** - An AI-powered system for detecting suspicious weapons trade activities across online platforms using advanced NLP, LLM integration, and computer vision.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19.1+-blue.svg)](https://reactjs.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)
[![Ollama](https://img.shields.io/badge/Ollama-LLM-purple.svg)](https://ollama.ai)

---

## 🚀 Quick Start

### Option 1: One-Command Docker Start (Recommended)

```bash
# 1. Clone the repository
git clone https://github.com/YourUserName/weapons-trade-detection-system.git
cd weapons-trade-detection-system

# 2. Configure your API credentials
cp backend/.env.example backend/.env
# Edit backend/.env with your Reddit API keys

# 3. Start everything with one command
docker compose up -d

# 4. Wait for models to download (~5-10 min first time)
docker compose logs -f ollama-setup

# 5. Open the app
open http://localhost:3000
```

**That's it!** The system will be running at:
| Service | URL |
|---------|-----|
| 🌐 **Frontend Dashboard** | http://localhost:3000 |
| 🔧 **Backend API** | http://localhost:9000 |
| 📚 **API Documentation** | http://localhost:9000/docs |
| 🤖 **Ollama LLM** | http://localhost:11434 |

### Option 2: Manual Development Setup

<details>
<summary>Click to expand manual setup instructions</summary>

#### Prerequisites
- Python 3.8+
- Node.js 16+
- Docker Desktop (for Ollama)

#### Step 1: Start Ollama
```bash
docker compose up -d ollama
docker exec ollama ollama pull llama3.1:8b
docker exec ollama ollama pull llava:7b
```

#### Step 2: Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Run the server
python -m uvicorn src.server:app --host 0.0.0.0 --port 9000 --reload
```

#### Step 3: Frontend Setup
```bash
cd frontend
npm install
npm start
```

</details>

---

## 📋 Configuration

### Reddit API (Required)

1. Go to https://www.reddit.com/prefs/apps
2. Click "Create App" or "Create Another App"
3. Select "script" type
4. Copy `client_id` (under app name) and `client_secret`

```env
# backend/.env
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USER_AGENT=WeaponsDetection/2.4 (Academic Research)
```

### Telegram API (Optional)

1. Go to https://my.telegram.org
2. Log in with your phone number
3. Create new application
4. Copy `api_id` and `api_hash`

```env
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
```

---

## 📊 View Live Logs

```bash
# Docker
docker compose logs -f backend

# Manual
tail -f backend/server.log
```

**Log output example:**
```
📡 SSE Stream started: subreddits=gundeals, limit=5...
📥 Collected 5 posts from r/gundeals
📝 Analyzing post 1/5: 'WTS - Glock 19...' from r/gundeals
✅ Collection complete: 5 scanned, 2 HIGH, 1 MEDIUM, 1 LOW, 1 filtered
```

---

## 🎯 Features

### 🔍 Multi-Platform Data Collection
- **Reddit** - Subreddit monitoring with PRAW
- **Telegram** - Public channel scraping with Telethon

### 🤖 AI-Powered Analysis
- **LLM Text Analysis** - Ollama (llama3.1:8b) for illegal trade detection
- **Vision Analysis** - LLaVA (llava:7b) for weapon detection in images
- **Rule-Based Scoring** - Keyword and pattern matching

### 📱 Interactive Dashboard
- **Live Detection Stream** - Real-time SSE updates
- **Risk Classification** - HIGH (≥75%), MEDIUM (≥45%), LOW (≥25%)
- **Media Library** - Image gallery with weapon detection overlays
- **Collection History** - Past session tracking

### 🛡️ Privacy & Ethics
- **Author Hashing** - SHA-256 privacy protection
- **Academic Focus** - Research-only application
- **Synthetic Data** - Safe testing without real data

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React/TypeScript)               │
│  Dashboard │ Threats │ Media Library │ Analytics │ Settings │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP/REST + SSE Streaming
┌──────────────────────────▼──────────────────────────────────┐
│                   Backend (FastAPI/Python)                   │
│  /api/stream/reddit │ /api/stream/telegram │ /analyze       │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                    Ollama LLM Service                        │
│  llama3.1:8b (text) │ llava:7b (vision)                     │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
weapons-trade-detection-system/
├── 🐳 docker-compose.yml          # One-command startup
├── 📚 README.md                   # This file
├── 📋 CONTEXT.md                  # Technical documentation
│
├── 🖥️  backend/
│   ├── Dockerfile                 # Backend container
│   ├── .env.example               # Environment template
│   ├── requirements.txt           # Python dependencies
│   ├── server.log                 # Live logs (tail -f this)
│   ├── src/
│   │   └── server.py              # Main FastAPI server
│   └── backend_service/
│       ├── handlers/              # Reddit, Telegram, Image, LLM handlers
│       ├── core/                  # Detection engine
│       └── entities/              # Data models
│
└── 🎨 frontend/
    ├── Dockerfile                 # Frontend container
    ├── package.json
    └── src/
        ├── pages/                 # Dashboard, Threats, Media, etc.
        ├── components/            # Reusable UI components
        ├── hooks/                 # useSSE, useCollection
        └── context/               # Global state
```

---

## 🔧 Common Commands

```bash
# Start all services
docker compose up -d

# Stop all services
docker compose down

# View logs
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f ollama

# Rebuild after code changes
docker compose up -d --build

# Pull latest LLM models
docker exec ollama ollama pull llama3.1:8b
docker exec ollama ollama pull llava:7b

# Check service health
curl http://localhost:9000/health
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check with Ollama status |
| GET | `/api/stream/reddit` | SSE stream for Reddit collection |
| GET | `/api/stream/telegram` | SSE stream for Telegram collection |
| POST | `/analyze` | Analyze single text |
| POST | `/api/llm/analyze` | LLM-powered analysis |

---

## 🚨 Important Disclaimers

> **⚠️ Academic Research Only**: This system is designed exclusively for academic research and educational purposes.

> **🔒 Privacy First**: All data collection follows ethical guidelines. Author identities are hashed.

> **📚 Educational Purpose**: This project serves as a learning tool for AI applications in cybersecurity research.

---

## 📄 License

MIT License - see [LICENSE](./LICENSE) for details.

---

**🔬 Built for Academic Research | 🛡️ Privacy-First Design | 🚀 Open Source**

*Version 2.4.0 | December 2025*
