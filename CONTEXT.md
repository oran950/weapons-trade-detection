# 📋 Project Context & Technical Documentation

> This document provides detailed technical context for developers working on the Weapons Trade Detection System. It explains the architecture, design decisions, and component interactions.

---

## 🏛️ Architecture Overview

### Design Philosophy

The system follows a **modular, layered architecture** designed for:

1. **Separation of Concerns** - Each module has a single responsibility
2. **Testability** - Components are loosely coupled for easy testing
3. **Extensibility** - New data sources and analyzers can be added easily
4. **Backward Compatibility** - Legacy code continues to work via adapters
5. **Real-time Streaming** - SSE-based live data flow for responsive UX

### Layer Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React/TypeScript)               │
│  Dashboard │ Threats │ History │ Analytics │ Settings       │
│                                                              │
│  Components: Layout, Detection, Collection, shared          │
│  Hooks: useSSE, useCollection                               │
│  Context: AppContext (global state)                         │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP/REST + SSE Streaming
┌──────────────────────────▼──────────────────────────────────┐
│                   API Layer (FastAPI)                        │
│  src/server.py → /api/stream/{reddit,telegram} (SSE)        │
│  entrypoints/api.py → routes/{detection,collection,llm}.py  │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                  Business Logic Layer                        │
│  handlers/{reddit,telegram,analysis}_handler.py              │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                    Core Detection Layer                      │
│  core/{analyzer,scorer,detector}.py + _ai_operations.py     │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                   Data & Utilities Layer                     │
│  entities/ │ utils/ │ config.py │ globals.py                │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎨 Frontend Architecture (React/TypeScript)

### Multi-Page Navigation

The frontend uses **React Router v6** for client-side routing:

| Route | Page | Description |
|-------|------|-------------|
| `/` | Dashboard | Main control center with collection buttons and live stream |
| `/threats` | ThreatsPage | Active threats list with filtering and detail views |
| `/media` | MediaLibraryPage | Image/video gallery with weapon detection overlays |
| `/history` | HistoryPage | Collection session history and past results |
| `/analytics` | AnalyticsPage | Charts, statistics, and data visualization |
| `/settings` | SettingsPage | API configuration (Reddit, Telegram, Ollama) |

### Directory Structure

```
frontend/src/
├── api/
│   └── index.ts              # API client (fetch-based)
├── context/
│   └── AppContext.tsx        # Global app state (posts, stats, sessions)
├── hooks/
│   ├── useSSE.ts             # SSE connection hook for real-time streaming
│   └── useCollection.ts      # Collection state management
├── pages/
│   ├── Dashboard.tsx         # Main dashboard with live stream
│   ├── ThreatsPage.tsx       # Active threats list
│   ├── MediaLibraryPage.tsx  # Image/video gallery with weapon overlays
│   ├── HistoryPage.tsx       # Collection history
│   ├── AnalyticsPage.tsx     # Charts and statistics
│   └── SettingsPage.tsx      # API configuration
├── components/
│   ├── Layout/
│   │   ├── Header.tsx        # Top navigation bar with system status
│   │   ├── Sidebar.tsx       # Side navigation with threat counter
│   │   └── Layout.tsx        # Page wrapper component
│   ├── Detection/
│   │   ├── LiveStream.tsx    # Real-time detection stream display
│   │   ├── DetectionCard.tsx # Individual detection item (clickable)
│   │   └── DetailModal.tsx   # Full details modal on click
│   ├── Media/
│   │   └── MediaGallery.tsx  # Image gallery with weapon detection overlays
│   ├── Collection/
│   │   ├── CollectButton.tsx # Reddit/Telegram collection buttons
│   │   └── ProgressBar.tsx   # Animated collection progress
│   └── shared/
│       ├── StatCard.tsx      # Reusable statistics card
│       └── RiskBadge.tsx     # Risk level indicator (HIGH/MEDIUM/LOW)
├── types/
│   └── index.ts              # TypeScript interfaces
├── App.tsx                   # Router setup with Layout wrapper
└── index.tsx                 # React entry point
```

### Key Hooks

#### `useSSE` - Server-Sent Events Hook
```typescript
// Connects to SSE endpoint and handles events
const { connect, disconnect, isLoading, error } = useSSE({
  onPost: (post) => { /* Handle each post as it arrives */ },
  onComplete: (summary) => { /* Collection finished */ },
  onError: (err) => { /* Handle errors */ },
  onStart: (data) => { /* Collection started */ },
});

// Start streaming
connect('/api/stream/reddit?subreddits=news,technology&limit=10');
```

#### `useCollection` - Collection State Management
```typescript
const {
  isCollecting,        // Boolean: currently collecting
  collectedPosts,      // Array: posts collected in current session
  summary,             // Object: final collection summary
  progress,            // Object: { current, total } for progress bar
  startRedditCollection,
  startTelegramCollection,
  cancelCollection,
} = useCollection();
```

### Global State (`AppContext`)

```typescript
interface AppState {
  // Live data
  posts: Post[];                    // All collected posts
  stats: { total, high, medium, low } // Risk breakdown
  
  // Status
  backendOnline: boolean;
  redditConfigured: boolean;
  telegramConfigured: boolean;
  ollamaAvailable: boolean;
  
  // Session tracking
  isCollecting: boolean;
  currentPlatform: 'reddit' | 'telegram' | null;
  sessions: CollectionSession[];    // Past collection sessions
  
  // Actions
  startCollection, stopCollection, addPost, addSession
}
```

### UI/UX Design

The frontend uses a **cinematic dark theme** with sci-fi aesthetics:

- **Color Palette**: Dark backgrounds (#0a0a0f, #151520) with cyan (#00ffff) and magenta (#ff00ff) accents
- **Typography**: Rajdhani (UI), Orbitron (headers) - tech/military aesthetic
- **Animations**: CSS keyframes for pulse, glow, scan effects
- **Components**: Glassmorphism cards, neon borders, animated progress bars

---

## 📁 Backend Directory Structure

### `backend_service/` - New Modular Architecture

This is the new, properly structured service layer introduced in v2.2.0.

#### `entities/` - Data Models
Pure data classes representing domain objects:

| File | Models | Purpose |
|------|--------|---------|
| `post.py` | `Post`, `RedditPost`, `TelegramMessage` | Content from platforms |
| `analysis.py` | `AnalysisResult`, `EntityExtractionResult` | Analysis outputs |
| `risk.py` | `RiskClassification` | Risk scoring results |

```python
# Example: entities/post.py
@dataclass
class RedditPost(Post):
    subreddit: str
    score: int
    num_comments: int
    url: str
```

#### `core/` - Detection Engine
The heart of the analysis system:

| File | Class | Responsibility |
|------|-------|----------------|
| `analyzer.py` | `TextAnalyzer` | Pattern matching, keyword detection |
| `scorer.py` | `RiskScorer` | Calculate weighted risk scores |
| `detector.py` | `Detector` | Orchestrate analyzer + scorer |

**Detection Flow:**
```
Text → TextAnalyzer.analyze_content() → AnalysisResult
                                              ↓
                                    RiskScorer.calculate_risk()
                                              ↓
                                    RiskClassification (risk_score, flags)
```

#### `handlers/` - Business Logic
Platform-specific data collection and processing:

| File | Class | Purpose |
|------|-------|---------|
| `reddit_handler.py` | `RedditHandler` | Reddit collection via PRAW |
| `telegram_handler.py` | `TelegramHandler` | Telegram collection via Telethon |
| `analysis_handler.py` | `AnalysisHandler` | Batch analysis orchestration |
| `image_analysis_handler.py` | `ImageAnalysisHandler` | Weapon detection in images via LLaVA |
| `llm_text_analyzer.py` | `LLMTextAnalyzer` | LLM-based text analysis for illegal trade |
| `text_analyzer.py` | `TextAnalyzer` | Rule-based keyword/pattern matching |

#### `entrypoints/` - API Layer
HTTP interface to the system:

```
entrypoints/
├── api.py              # FastAPI app, CORS, middleware
└── routes/
    ├── detection.py    # POST /analyze, /api/detection/batch
    ├── collection.py   # POST /api/collection/{reddit,telegram}
    ├── generation.py   # POST /api/generation/synthetic
    └── llm.py          # POST /api/llm/{analyze,extract,classify}
```

#### `workflows/` - Orchestration
Multi-step pipelines for batch processing:

| Workflow | Purpose |
|----------|---------|
| `collection_workflow.py` | Collect → Analyze → Store |
| `analysis_workflow.py` | Load → Analyze → Report |
| `report_workflow.py` | Aggregate → Format → Export |

#### `utils/` - Utilities
Reusable helper functions:

| File | Function | Purpose |
|------|----------|---------|
| `hashing.py` | `hash_string()` | SHA-256 author privacy |
| `rate_limiter.py` | `RateLimiter` | API rate limiting |
| `file_manager.py` | `FileManager` | Safe file I/O |

#### Special Files

| File | Purpose |
|------|---------|
| `_ai_operations.py` | All LLM/Ollama interactions |
| `_metrics.py` | Performance tracking |
| `_telemetry.py` | Logging and monitoring |
| `config.py` | Centralized configuration |
| `exceptions.py` | Custom exception types |
| `globals.py` | Global state (Ollama client, etc.) |
| `llm_globals.py` | LLM-specific config |

---

### `src/` - Legacy Code (Backward Compatible)

The original source code, still functional via adapters:

```
src/
├── detection/
│   └── text_analyzer.py   # Original WeaponsTextAnalyzer + Adapter
├── models/
│   └── schemas.py         # Original Pydantic models
├── reddit/
│   └── reddit_collector.py # Original AcademicRedditCollector
└── server.py              # Main FastAPI server (includes SSE endpoints)
```

**Backward Compatibility Adapter:**
```python
# In text_analyzer.py
class TextAnalyzerAdapter:
    """Adapts new TextAnalyzer to old interface"""
    def __init__(self):
        self.analyzer = TextAnalyzer()
    
    def analyze_text(self, text: str) -> Dict[str, Any]:
        result = self.analyzer.analyze_content(text)
        return {
            'risk_score': result.risk_score,
            'confidence': result.confidence,
            'flags': result.flags,
            # ... legacy format
        }
```

---

## 📡 SSE Streaming Endpoints

### Real-time Data Collection

The system uses **Server-Sent Events (SSE)** for real-time streaming of collected posts to the frontend.

#### `GET /api/stream/reddit`

Stream Reddit posts as they are collected and analyzed.

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `subreddits` | string | required | Comma-separated subreddit names |
| `limit` | int | 10 | Posts per subreddit (1-50) |
| `time_filter` | string | "day" | Time filter (hour, day, week, month, year, all) |
| `sort_method` | string | "hot" | Sort method (hot, new, top, rising) |

**Events:**
| Event | Data | Description |
|-------|------|-------------|
| `start` | `{subreddits, limit, timestamp}` | Collection started |
| `post` | `{id, title, content, risk_analysis, ...}` | Each post with analysis |
| `progress` | `{total, high_risk, subreddits_completed}` | Progress update |
| `complete` | `{total, high_risk, medium_risk, low_risk}` | Collection finished |
| `error` | `{message, subreddit}` | Error occurred |

**Example:**
```javascript
const eventSource = new EventSource(
  '/api/stream/reddit?subreddits=news,technology&limit=10'
);

eventSource.addEventListener('post', (e) => {
  const post = JSON.parse(e.data);
  console.log('Received:', post.title, post.risk_analysis.risk_level);
});

eventSource.addEventListener('complete', (e) => {
  const summary = JSON.parse(e.data);
  console.log('Done:', summary.total, 'posts collected');
  eventSource.close();
});
```

#### `GET /api/stream/telegram`

Stream Telegram messages (similar interface, placeholder implementation).

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `channels` | string | required | Comma-separated channel names |
| `limit` | int | 50 | Messages per channel |

---

## 🔌 External Integrations

### Reddit API (PRAW)

**Configuration:**
```env
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USER_AGENT=WeaponsDetection/2.0
```

**Rate Limits:**
- 60 requests/minute (OAuth)
- Automatic rate limiting via PRAW

**Key Classes:**
- `AcademicRedditCollector` (legacy)
- `RedditHandler` (new)

### Telegram API (Telethon)

**Configuration:**
```env
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
TELEGRAM_SESSION_NAME=weapons_detection_session
```

**Setup:**
1. Go to https://my.telegram.org
2. Log in with phone number
3. Create new application
4. Copy `api_id` and `api_hash`

**Capabilities:**
- Public channel message collection
- Global message search
- Media detection (photos, videos, files)
- Forward source tracking

**Key Classes:**
- `TelegramHandler` - Async collection using Telethon

### Ollama LLM

**Configuration:**
```env
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
OLLAMA_VISION_MODEL=llava:7b
```

**Required Models:**
```bash
ollama pull llama3.1:8b    # Text analysis
ollama pull llava:7b       # Vision/image analysis
```

**Supported Operations:**
| Operation | Model | Description |
|-----------|-------|-------------|
| Text Analysis | llama3.1:8b | Analyze post for weapon trade, legality |
| Vision Analysis | llava:7b | Detect weapons in images |
| Entity Extraction | llama3.1:8b | Extract weapons, locations, actors |
| Risk Classification | llama3.1:8b | Classify risk level |

**LLM Text Analysis Response:**
```json
{
  "is_weapon_related": true,
  "is_trade_related": true,
  "is_potentially_illegal": true,
  "risk_assessment": "HIGH",
  "reasoning": "Post offers firearm for sale..."
}
```

**Vision Analysis Response:**
```json
{
  "contains_weapons": true,
  "weapon_count": 2,
  "detections": [
    {"weapon_type": "handgun", "confidence": 0.95}
  ],
  "overall_risk": "HIGH"
}
```

**Error Handling:**
- Graceful fallback when Ollama unavailable
- Timeout handling (default: 30s)
- Retry logic for transient failures
- Detailed logging for debugging

---

## 🔄 Data Flow

### Collection → Analysis Pipeline (Two-Phase SSE Streaming)

The collection uses a **two-phase flow** for better UX:

```
PHASE 1: COLLECTING
1. User clicks "COLLECT FROM REDDIT" on Dashboard
         ↓
2. Frontend calls useCollection.startRedditCollection()
         ↓
3. useSSE connects to /api/stream/reddit endpoint
         ↓
4. Backend collects ALL posts from subreddits via PRAW
   - Yields "start" event with phase: "collecting"
   - Logs: 📥 Collected X posts from r/subreddit
         ↓
5. Backend yields "phase" event with phase: "analyzing"

PHASE 2: ANALYZING
6. Backend iterates through collected posts:
   - Text analysis with TextAnalyzer
   - LLM analysis with Ollama (llama3.1:8b)
   - Vision analysis with LLaVA (llava:7b)
   - Logs: 📝 Analyzing post X/Y: 'title...'
   - Yields "post" event for each post (if risk >= 25%)
         ↓
7. Frontend receives each "post" event:
   - Adds to AppContext.posts
   - Updates live stream display
   - Updates progress bar
         ↓
8. Backend yields "complete" event with summary
   - Logs: ✅ Collection complete: X scanned, Y HIGH...
         ↓
9. Frontend updates stats, closes EventSource
```

### Risk Score Thresholds

Posts are classified into risk levels based on their score:

| Level | Score Range | Action |
|-------|-------------|--------|
| **HIGH** | ≥ 75% | Displayed with red badge |
| **MEDIUM** | 45% - 74% | Displayed with orange badge |
| **LOW** | 25% - 44% | Displayed with yellow badge |
| **NONE** | < 25% | **Filtered out** (not sent to frontend) |

Risk scores are adjusted by:
- **LLM Analysis**: Can upgrade to HIGH/CRITICAL if illegal trade detected
- **Vision Analysis**: Can upgrade if weapons detected in images, or **reduce by 20%** if image is verified safe

### API Request Flow

```
HTTP Request
     ↓
FastAPI Router (routes/*.py)
     ↓
Request Validation (Pydantic models/requests.py)
     ↓
Handler (handlers/*.py)
     ↓
Core Logic (core/*.py + _ai_operations.py)
     ↓
Response Serialization (models/responses.py)
     ↓
HTTP Response
```

---

## 🧪 Testing Strategy

### Test Structure
```
tests/
├── __init__.py
├── test_analyzer.py      # Core analyzer tests
├── test_entities.py      # Data model tests
├── test_handlers.py      # Handler tests (mocked APIs)
└── test_api.py           # API endpoint tests
```

### Running Tests
```bash
cd backend
source venv/bin/activate
pytest tests/ -v
pytest tests/ -v --cov=backend_service  # With coverage
```

### Mocking External Services
```python
# Example: Mock Reddit API
@patch('backend_service.handlers.reddit_handler.praw.Reddit')
def test_reddit_collection(mock_reddit):
    mock_reddit.return_value.subreddit.return_value.hot.return_value = [
        MockSubmission(title="Test", selftext="Content")
    ]
    handler = RedditHandler()
    posts = handler.collect(subreddits=["test"], limit=10)
    assert len(posts) > 0
```

---

## ⚙️ Configuration Management

### Environment Variables

All configuration is centralized in `backend_service/config.py`:

```python
class Config:
    # Reddit
    REDDIT_CLIENT_ID: str = os.getenv("REDDIT_CLIENT_ID", "")
    REDDIT_CLIENT_SECRET: str = os.getenv("REDDIT_CLIENT_SECRET", "")
    
    # Telegram
    TELEGRAM_API_ID: int = int(os.getenv("TELEGRAM_API_ID", "0"))
    TELEGRAM_API_HASH: str = os.getenv("TELEGRAM_API_HASH", "")
    
    # Ollama
    OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
    
    @classmethod
    def is_reddit_configured(cls) -> bool:
        return bool(cls.REDDIT_CLIENT_ID and cls.REDDIT_CLIENT_SECRET)
    
    @classmethod
    def is_telegram_configured(cls) -> bool:
        return bool(cls.TELEGRAM_API_ID and cls.TELEGRAM_API_HASH)
```

### Feature Flags

Enable/disable features based on configuration:
- Reddit collection: Requires `REDDIT_CLIENT_ID` + `REDDIT_CLIENT_SECRET`
- Telegram collection: Requires `TELEGRAM_API_ID` + `TELEGRAM_API_HASH`
- LLM analysis: Requires running Ollama service

---

## 🔐 Security Considerations

### Privacy Protection

1. **Author Hashing** - All author identifiers are SHA-256 hashed
   ```python
   def hash_string(s: str) -> str:
       return hashlib.sha256(s.encode()).hexdigest()[:16]
   ```

2. **No PII Storage** - Personal information is never persisted

3. **Academic Disclaimer** - All collected data includes research disclaimers

### API Security

- CORS configured for localhost development
- Rate limiting on collection endpoints
- Input validation via Pydantic

### Credential Management

- Environment variables for secrets (never committed)
- `.env` file excluded from git (`.gitignore`)

---

## 📊 Monitoring & Observability

### Logging

The backend logs to **both stdout AND a file** for easy monitoring:

**Log File Location:**
```
backend/server.log
```

**View Live Logs:**
```bash
tail -f /path/to/weapons-trade-detection-system/backend/server.log
```

**Log Format:**
```
2025-12-31 18:30:02 | INFO | WeaponsDetectionAPI | 📡 SSE Stream started...
2025-12-31 18:30:03 | INFO | WeaponsDetectionAPI | 📥 Collected 5 posts from r/gundeals
2025-12-31 18:30:04 | INFO | WeaponsDetectionAPI | 📝 Analyzing post 1/5: 'WTS - Glock...'
2025-12-31 18:30:15 | INFO | WeaponsDetectionAPI | ✅ Collection complete: 5 scanned, 2 HIGH...
```

**Log Emojis:**
| Emoji | Meaning |
|-------|---------|
| 📡 | SSE stream started |
| 📥 | Posts collected from subreddit |
| 📊 | Total posts summary |
| 📝 | Analyzing individual post |
| 🔍 | Vision/LLM analysis enabled |
| ⚠️ | Warning (handler unavailable, etc.) |
| ❌ | Error occurred |
| ✅ | Operation completed successfully |
| 🏥 | Health check |

**Configuration (`src/server.py`):**
```python
import logging

LOG_FILE = os.path.join(os.path.dirname(__file__), '..', 'server.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_FILE, mode='a')
    ]
)
```

### Metrics (`_metrics.py`)

Track performance and usage:
- Collection counts per platform
- Analysis latency percentiles
- LLM token usage
- Error rates

---

## 🚀 Deployment

### Development
```bash
# Backend
cd backend && source venv/bin/activate
python -m uvicorn src.server:app --reload --port 9000

# Frontend
cd frontend && npm start
```

### Production (Docker)
```bash
docker-compose up -d
```

### Docker Services
| Service | Port | Description |
|---------|------|-------------|
| backend | 9000 | FastAPI server |
| frontend | 3000 | React app (Nginx) |
| ollama | 11434 | LLM service |

---

## 🔧 Common Development Tasks

### Adding a New Data Source

1. Create entity in `entities/` (extend `Post`)
2. Create handler in `handlers/`
3. Add SSE streaming endpoint in `src/server.py`
4. Add routes in `entrypoints/routes/`
5. Update frontend:
   - Add collection button in `CollectButton.tsx`
   - Update `useCollection` hook
6. Add CLI support in `cli/`

### Adding New Detection Patterns

1. Update keyword lists in `core/analyzer.py`
2. Adjust weights in `core/scorer.py`
3. Add tests for new patterns
4. Update LLM prompts if using AI analysis

### Adding New API Endpoint

1. Define request/response models in `models/`
2. Create route handler in `entrypoints/routes/`
3. Register route in `entrypoints/api.py`
4. Update API documentation

### Adding a New Page

1. Create page component in `frontend/src/pages/`
2. Add route in `frontend/src/App.tsx`
3. Add navigation item in `frontend/src/components/Layout/Sidebar.tsx`
4. Update `AppContext` if needed for page state

---

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SSE-Starlette](https://github.com/sysid/sse-starlette)
- [PRAW (Reddit API)](https://praw.readthedocs.io/)
- [Telethon (Telegram API)](https://docs.telethon.dev/)
- [Ollama](https://ollama.ai/)
- [React Documentation](https://react.dev/)
- [React Router v6](https://reactrouter.com/)

---

*Last Updated: December 2025 | Version 2.4.0*
