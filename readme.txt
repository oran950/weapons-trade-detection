================================================================================
🚨 WEAPONS TRADE DETECTION SYSTEM - QUICK START
================================================================================

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🐳 ONE-COMMAND DOCKER START (Recommended)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Configure your API keys:
   cp backend/.env.example backend/.env
   # Edit backend/.env with your Reddit API credentials

2. Start everything:
   docker compose up -d

3. Wait for models to download (~5-10 min first time), then open:
   - Frontend:  http://localhost:3000
   - Backend:   http://localhost:9000
   - API Docs:  http://localhost:9000/docs

4. View logs:
   docker compose logs -f backend

5. Stop everything:
   docker compose down


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🖥️  MANUAL START (Development)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Terminal 1 - Ollama:
   docker compose up -d ollama
   docker exec ollama ollama pull llama3.1:8b
   docker exec ollama ollama pull llava:7b

Terminal 2 - Backend:
   cd backend
   source venv/bin/activate
   pip install -r requirements.txt
   python -m uvicorn src.server:app --host 0.0.0.0 --port 9000 --reload

Terminal 3 - Frontend:
   cd frontend
   npm install
   npm start


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 VIEW LIVE LOGS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Docker:
   docker compose logs -f backend

Manual:
   tail -f backend/server.log


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 URLS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Frontend:     http://localhost:3000
Backend API:  http://localhost:9000
API Docs:     http://localhost:9000/docs
Ollama:       http://localhost:11434


================================================================================





# 1. Clone the repository
git clone https://github.com/YourUserName/weapons-trade-detection-system.git
cd weapons-trade-detection-system

# 2. Configure Reddit API credentials
cp backend/.env.example backend/.env
# Edit backend/.env with your Reddit API keys (get them at reddit.com/prefs/apps)

# 3. Start everything
docker compose up -d