---
name: Restructure & Expand Detection System
overview: Transform the weapons detection system into a professional, scalable architecture with Telegram integration (replacing Twitter due to API costs), improved folder structure, and deeper Ollama LLM integration throughout the detection and analysis pipeline.
todos:
  - id: restructure-folders
    content: Create new backend_service/ folder structure matching reference image
    status: completed
  - id: migrate-code
    content: Migrate existing code to new structure (entities, handlers, core, utils)
    status: completed
  - id: telegram-collector
    content: Implement TelegramCollector class using Telethon library
    status: completed
  - id: telegram-api-config
    content: Add Telegram API configuration (api_id, api_hash from my.telegram.org)
    status: completed
  - id: llm-operations
    content: Create _ai_operations.py with entity extraction, classification, and generation
    status: completed
  - id: workflows
    content: Build workflow orchestration for collection -> analysis -> reporting
    status: completed
  - id: cli-tools
    content: Add CLI commands for batch collection and analysis
    status: completed
  - id: frontend-telegram
    content: Add Telegram collection interface to frontend
    status: completed
isProject: false
---

# Weapons Detection System - Next Level Architecture

## Current State Analysis

Your existing system has:

- **Reddit Pipeline**: Collection, analysis, storage (`[reddit_collector.py](backend/src/reddit/reddit_collector.py)`)
- **Rule-based Detection**: Keyword/pattern matching (`[text_analyzer.py](backend/src/detection/text_analyzer.py)`)
- **Basic Ollama**: Hybrid analysis endpoint (`[server.py](backend/src/server.py)` lines 600-833)
- **Flat Structure**: Everything in `src/` with minimal organization

---

## 1. New Folder Structure (Based on Reference Image)

Restructure `backend/` to match professional architecture:

```javascript
backend/
├── backend_service/
│   ├── cli/                    # Command-line interface
│   │   ├── __init__.py
│   │   ├── collect.py          # CLI for data collection
│   │   └── analyze.py          # CLI for batch analysis
│   │
│   ├── core/                   # Core business logic
│   │   ├── __init__.py
│   │   ├── detector.py         # Main detection orchestrator
│   │   ├── analyzer.py         # Text analysis (refactored)
│   │   └── scorer.py           # Risk scoring logic
│   │
│   ├── entities/               # Data models & schemas
│   │   ├── __init__.py
│   │   ├── post.py             # Post entities (Reddit, Telegram)
│   │   ├── analysis.py         # Analysis result entities
│   │   └── risk.py             # Risk assessment entities
│   │
│   ├── entrypoints/            # API entry points
│   │   ├── __init__.py
│   │   ├── api.py              # FastAPI app definition
│   │   └── routes/
│   │       ├── detection.py    # Detection endpoints
│   │       ├── collection.py   # Data collection endpoints
│   │       ├── generation.py   # Content generation endpoints
│   │       └── llm.py          # LLM-specific endpoints
│   │
│   ├── handlers/               # Request handlers
│   │   ├── __init__.py
│   │   ├── reddit_handler.py   # Reddit collection logic
│   │   ├── telegram_handler.py # Telegram collection logic (NEW)
│   │   └── analysis_handler.py # Analysis orchestration
│   │
│   ├── models/                 # Pydantic models for API
│   │   ├── __init__.py
│   │   ├── requests.py         # Request models
│   │   └── responses.py        # Response models
│   │
│   ├── utils/                  # Utility functions
│   │   ├── __init__.py
│   │   ├── hashing.py          # Privacy hashing
│   │   ├── rate_limiter.py     # Rate limiting
│   │   └── file_manager.py     # File I/O operations
│   │
│   ├── workflows/              # Multi-step workflows
│   │   ├── __init__.py
│   │   ├── collection_workflow.py   # Data collection pipeline
│   │   ├── analysis_workflow.py     # Analysis pipeline
│   │   └── report_workflow.py       # Report generation
│   │
│   ├── _ai_operations.py       # All LLM/AI operations
│   ├── _metrics.py             # Metrics & telemetry
│   ├── _telemetry.py           # Logging & monitoring
│   ├── config.py               # Configuration management
│   ├── exceptions.py           # Custom exceptions
│   ├── globals.py              # Global state
│   └── llm_globals.py          # LLM configuration
│
├── collected_data/             # Data storage (unchanged)
├── tests/                      # Test suite (NEW)
├── notebooks/                  # Jupyter notebooks (NEW)
├── .env.example                # Environment template
└── requirements.txt
```

---

## 2. Telegram Pipeline Integration

### Why Telegram Instead of Twitter

- **Free API**: Telegram provides full API access at no cost
- **More Relevant**: Telegram is commonly used for underground trading due to encryption
- **Rich Features**: Groups, channels, and direct messages are all accessible
- **Better for Research**: Public channels often contain the content we're looking to detect

### Setup Requirements

1. Go to [https://my.telegram.org](https://my.telegram.org)
2. Log in with your phone number
3. Create an application to get `api_id` and `api_hash`
4. These credentials are free and permanent

### Telegram Collector Design (mirrors Reddit collector):

```python
# backend_service/handlers/telegram_handler.py
@dataclass
class TelegramMessage:
    id: int
    content: str
    author_hash: str          # Hashed user ID for privacy
    chat_id: int
    chat_title: str           # Channel/group name
    chat_type: str            # 'channel', 'group', 'supergroup'
    created_at: float
    views: Optional[int]      # For channels
    forwards: Optional[int]
    replies: Optional[int]
    media_type: Optional[str] # 'photo', 'video', 'document', None
    url: str
    collected_at: str
    risk_analysis: Optional[Dict] = None

class TelegramCollector:
    def __init__(self, api_id: int, api_hash: str, session_name: str):
        # Uses Telethon library for async Telegram API access
        
    async def collect_channel_messages(channel_username, limit) -> List[TelegramMessage]
    async def collect_group_messages(group_id, limit) -> List[TelegramMessage]
    async def search_messages(query, limit) -> List[TelegramMessage]
    async def collect_by_keywords(keywords, channels, limit) -> List[TelegramMessage]
    def analyze_collected_messages(messages, analyzer) -> List[TelegramMessage]
    def save_messages(messages, filename, format)
```

### Key Telegram Features to Leverage

1. **Public Channels**: Monitor channels related to weapons, military surplus, etc.
2. **Keyword Search**: Search across joined channels/groups
3. **Message History**: Access full message history of public channels
4. **Media Detection**: Identify posts with images/videos (potential weapon photos)
5. **Forward Tracking**: See where messages originated from

---

## 3. Enhanced Ollama LLM Integration

Currently Ollama is only used for validation. Expand to:

### A. Smarter Detection (Core Analysis)

```python
# _ai_operations.py
class LLMOperations:
    def classify_risk(text, rule_results) -> RiskClassification
    def extract_entities(text) -> ExtractedEntities  # NEW
    def explain_flags(text, flags) -> Explanation     # NEW
    def detect_evasion(text) -> EvasionPatterns       # NEW
```

### B. Entity Extraction

Extract structured data from posts:

- Weapon types and models
- Locations and meeting points
- Contact methods (phone, telegram, etc.)
- Prices and quantities
- Time references

### C. Content Generation Enhancement

Replace template-based generation with LLM-powered:

```python
def generate_synthetic_post(params) -> str:
    # Use Ollama to generate more realistic, varied content
    # Better for training detection models
```

### D. Report Generation

```python
def generate_analysis_report(posts, analysis_results) -> Report:
    # Summarize findings
    # Generate insights
    # Create executive summary
```

### E. Conversation Analysis

For detecting multi-message weapon deals:

```python
def analyze_conversation(messages) -> ConversationAnalysis:
    # Track deal progression
    # Identify buyer/seller roles
    # Detect negotiation patterns
```

---

## 4. Workflow Orchestration

Create proper pipelines that combine collection, analysis, and reporting:

```python
# workflows/analysis_workflow.py
class AnalysisWorkflow:
    def __init__(self, use_llm=True):
        self.collector = MultiPlatformCollector()
        self.analyzer = HybridAnalyzer(use_llm)
        self.reporter = ReportGenerator()
    
    async def run_full_analysis(self, config: WorkflowConfig):
        # 1. Collect from Reddit + Telegram
        posts = await self.collector.collect_all(config.sources)
        
        # 2. Rule-based analysis
        rule_results = self.analyzer.analyze_batch(posts)
        
        # 3. LLM enhancement (if enabled)
        if self.use_llm:
            enhanced = await self.analyzer.llm_enhance(rule_results)
        
        # 4. Generate report
        report = self.reporter.generate(enhanced)
        
        return report
```

---

## 5. Implementation Priority

### Phase 1: Restructure (Week 1)

1. Create new `backend_service/` folder structure
2. Migrate existing code to new locations
3. Update imports and ensure backwards compatibility
4. Add proper exception handling

### Phase 2: Telegram Integration (Week 2)

1. Implement TelegramCollector class using Telethon
2. Add Telegram API configuration (api_id, api_hash)
3. Create unified collection interface for Reddit + Telegram
4. Add Telegram routes and frontend interface

### Phase 3: LLM Enhancement (Week 3)

1. Create `_ai_operations.py` with all LLM functions
2. Add entity extraction
3. Implement LLM content generation
4. Add report generation

### Phase 4: Workflows & CLI (Week 4)

1. Build workflow orchestration
2. Add CLI tools for batch processing
3. Create Jupyter notebooks for analysis
4. Add metrics and telemetry

---

## Decisions Made

1. **Platform**: Using Telegram instead of Twitter (free API, more relevant for weapons trade detection)
2. **Libraries**: Telethon for Telegram API (async Python library)

## Remaining Questions

1. **Migration Approach**: Full refactor or incremental migration?
2. **LLM Priority**: Which LLM features are most important to you?
3. **Telegram Channels**: Do you have specific channels/groups to monitor?

---

## Dependencies to Add

```txt
# Telegram
telethon>=1.34.0        # Async Telegram client
cryptg>=0.4.0           # Optional: faster crypto for Telethon

# Async support
aiohttp>=3.9.0          # Async HTTP client
asyncio>=3.4.3          # Async support (built-in for Python 3.7+)


```

