from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from datetime import datetime
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field

from detection.text_analyzer import WeaponsTextAnalyzer
import sys
import os

import asyncio
from concurrent.futures import ThreadPoolExecutor

# Import configuration
from config import AppConfig

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from generation.content_generator import SyntheticContentGenerator, ContentParameters

import json as _json
import re as _re
from typing import Tuple as _Tuple
import requests as _requests
from fastapi import Query as _Query

# --- ENV / Config (uses your existing AppConfig where convenient) ---
_LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama").lower()
_OLLAMA_BASE = os.getenv("OLLAMA_BASE", "http://localhost:11434")
_OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")


# Create FastAPI app
app = FastAPI(
    title="Weapons Detection API",
    description="Academic research system for detecting illegal weapons trade patterns",
    version="2.1.0",
)

# Initialize components
analyzer = WeaponsTextAnalyzer()
content_generator = SyntheticContentGenerator()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)




# Pydantic models for API requests
class ContentGenerationRequest(BaseModel):
    content_type: str = Field(..., description="Type of content to generate", pattern="^(post|message|ad|forum)$")
    intensity_level: str = Field(..., description="Intensity level", pattern="^(low|medium|high)$")
    quantity: int = Field(default=1, ge=1, le=50, description="Number of items to generate")
    language: str = Field(default="en", description="Language code")
    include_contact: bool = Field(default=False, description="Include contact information")
    include_pricing: bool = Field(default=False, description="Include pricing information")

class BatchGenerationRequest(BaseModel):
    quantity_per_type: int = Field(default=5, ge=1, le=20, description="Items per content type")
    include_contact: bool = Field(default=False, description="Include contact information")
    include_pricing: bool = Field(default=False, description="Include pricing information")

# Reddit collection models (updated for multiple subreddits)
class RedditCollectionParams(BaseModel):
    subreddits: List[str] = Field(default=["news"], description="List of subreddits to collect from")
    timeFilter: str = Field(default="day", description="Time filter for posts")
    sortMethod: str = Field(default="hot", description="Sort method for posts")
    limit_per_subreddit: int = Field(default=25, ge=1, le=50, description="Number of posts per subreddit")
    keywords: str = Field(default="", description="Keywords to search for")
    include_all_defaults: bool = Field(default=False, description="Include default subreddit list")

class RedditCollectionRequest(BaseModel):
    parameters: RedditCollectionParams

# Initialize Reddit collector
def init_reddit_collector():
    """Initialize Reddit collector when needed"""
    try:
        from reddit.reddit_collector import AcademicRedditCollector
        return AcademicRedditCollector
    except ImportError:
        return None

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Weapons Detection API v2.1 is running!"}

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "OK",
        "service": "Weapons Detection API",
        "version": "2.1.0",
        "timestamp": datetime.now().isoformat(),
        "python_version": "3.13",
        "reddit_configured": AppConfig.reddit.is_configured()
    }

@app.get("/api")
async def api_info():
    return {
        "message": "Weapons Detection API endpoints",
        "endpoints": [
            "/health", 
            "/api", 
            "/api/test", 
            "/api/detection/analyze", 
            "/api/generation/content",
            "/api/generation/batch",
            "/api/reddit/collect",
            "/api/reddit/config-status"
        ]
    }

@app.get("/api/test")
async def test_endpoint():
    return {
        "message": "API test successful!",
        "status": "working",
        "timestamp": datetime.now().isoformat(),
        "reddit_ready": AppConfig.reddit.is_configured()
    }

# Detection endpoints
@app.post("/api/detection/analyze")
async def analyze_content(request: Dict[str, Any]):
    content = request.get("content", "")
    
    if not content:
        raise HTTPException(status_code=400, detail="No content provided")
    
    analysis_results = analyzer.analyze_text(content)
    
    risk_score = analysis_results['risk_score']
    if risk_score >= 0.7:
        risk_level = "HIGH"
    elif risk_score >= 0.4:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"
    
    analysis_id = f"analysis_{int(datetime.now().timestamp())}"
    
    return {
        "analysis_id": analysis_id,
        "status": "completed",
        "risk_score": risk_score,
        "risk_level": risk_level,
        "confidence": analysis_results['confidence'],
        "flags": analysis_results['flags'],
        "detected_keywords": analysis_results['detected_keywords'],
        "detected_patterns": analysis_results['detected_patterns'],
        "summary": f"Analysis completed. Risk level: {risk_level}. Found {len(analysis_results['flags'])} potential indicators.",
        "timestamp": analysis_results['analysis_time']
    }

# Content generation endpoints
@app.post("/api/generation/content")
async def generate_content(request: ContentGenerationRequest):
    """Generate synthetic content for academic research"""
    try:
        params = ContentParameters(
            content_type=request.content_type,
            intensity_level=request.intensity_level,
            quantity=request.quantity,
            language=request.language,
            include_contact=request.include_contact,
            include_pricing=request.include_pricing
        )
        
        generated_content = content_generator.generate_content(params)
        
        return {
            "status": "success",
            "generated_count": len(generated_content),
            "content": generated_content,
            "parameters": request.dict(),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Content generation failed: {str(e)}")

@app.post("/api/generation/batch")
async def generate_batch_content(request: BatchGenerationRequest):
    """Generate a batch of content across all types and intensities"""
    try:
        batch_config = {
            "quantity_per_type": request.quantity_per_type,
            "include_contact": request.include_contact,
            "include_pricing": request.include_pricing
        }
        
        batch_results = content_generator.generate_batch(batch_config)
        
        return {
            "status": "success",
            "batch_results": batch_results,
            "configuration": batch_config,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch generation failed: {str(e)}")

@app.get("/api/generation/templates")
async def get_generation_templates():
    """Get available templates and vocabulary for content generation"""
    return {
        "content_types": ["post", "message", "ad", "forum"],
        "intensity_levels": ["low", "medium", "high"],
        "vocabulary_sample": {
            "low": content_generator.vocabulary["low"],
            "medium": content_generator.vocabulary["medium"],
            "high": content_generator.vocabulary["high"]
        },
        "platform_styles": content_generator.platform_styles,
        "supported_languages": ["en"],
        "max_quantity": 50
    }

# Reddit collection endpoints (updated for backend configuration)
@app.post("/api/reddit/collect")
async def collect_reddit_data(request: RedditCollectionRequest):
    """
    Collect Reddit data for academic research using configured credentials
    """
    try:
        # Check if Reddit is configured
        if not AppConfig.reddit.is_configured():
            missing_config = AppConfig.reddit.get_missing_config()
            raise HTTPException(
                status_code=500, 
                detail=f"Reddit API not configured. Missing: {', '.join(missing_config)}. Please check your .env file."
            )
        
        # Import collector class
        AcademicRedditCollector = init_reddit_collector()
        if not AcademicRedditCollector:
            raise HTTPException(
                status_code=500, 
                detail="Reddit collector not available. Please install required dependencies: pip install praw"
            )
        
        # Initialize collector with configured credentials
        collector = AcademicRedditCollector(
            client_id=AppConfig.reddit.CLIENT_ID,
            client_secret=AppConfig.reddit.CLIENT_SECRET,
            user_agent=AppConfig.reddit.USER_AGENT
        )
        
        # Run collection in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            collected_posts = await loop.run_in_executor(
                executor,
                collect_and_analyze_posts,
                collector,
                request.parameters
            )
        
        return {
            "status": "success",
            "message": f"Multi-subreddit Reddit data collection completed from {len(collected_posts.get('subreddits_collected', []))} subreddits",
            "total_collected": len(collected_posts.get("all_posts", [])),
            "high_risk_count": len(collected_posts.get("high_risk_posts", [])),
            "medium_risk_count": len(collected_posts.get("medium_risk_posts", [])),
            "low_risk_count": len(collected_posts.get("low_risk_posts", [])),
            "saved_files": collected_posts.get("saved_files", []),
            "collection_timestamp": datetime.now().isoformat(),
            "configured_with_credentials": True,
            "collection_summary": collected_posts.get("collection_summary", {}),
            "subreddits_collected": collected_posts.get("subreddits_collected", [])
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Reddit collection failed: {str(e)}"
        )

def collect_and_analyze_posts(collector, params):
    """
    Helper function to collect and analyze Reddit posts from multiple subreddits
    This runs in a separate thread to avoid blocking the main FastAPI thread
    """
    try:
        all_collected_posts = []
        collection_summary = {}
        
        # Enhanced default subreddit list for comprehensive coverage
        default_subreddits = [
            "news", "worldnews", "politics", "PublicFreakout", "Conservative", 
            "liberal", "conspiracy", "AskReddit", "technology", "science",
            "todayilearned", "explainlikeimfive", "changemyview", "unpopularopinion",
            "legaladvice", "relationship_advice", "amitheasshole", "offmychest",
            "guns", "firearms", "CCW", "ar15", "ak47", "gundeals", "gunpolitics",
            "progun", "liberalgunowners", "socialistRA", "weekendgunnit",
            "Military", "army", "navy", "airforce", "marines", "veterans",
            "EDC", "tacticalgear", "preppers", "survival", "bugout",
            "combatfootage", "MilitaryPorn", "WarplanePorn", "TankPorn",
            "Bad_Cop_No_Donut", "ProtectAndServe", "police", "security",
            "Anarchism", "socialism", "communism", "capitalism", "libertarian",
            "funny", "pics", "gaming", "movies", "books", "music", "sports",
            "ukraine", "russia", "syriancivilwar", "geopolitics", "internationalnews",
            "dankmemes", "memeeconomy", "politicalhumor", "darkhumor",
            "IllegalLifeProTips", "UnethicalLifeProTips", "LifeProTips"
        ]
        
        # Determine which subreddits to collect from
        if params.include_all_defaults:
            subreddits_to_collect = default_subreddits
        else:
            subreddits_to_collect = params.subreddits
        
        print(f"Collecting from {len(subreddits_to_collect)} subreddits: {subreddits_to_collect}")
        
        # Collect from each subreddit
        for subreddit in subreddits_to_collect:
            try:
                print(f"Collecting from r/{subreddit}...")
                
                if params.keywords:
                    # Search for specific keywords
                    keywords = [k.strip() for k in params.keywords.split(',')]
                    collected_posts = collector.search_posts_by_keywords(
                        subreddit_name=subreddit,
                        keywords=keywords,
                        time_filter=params.timeFilter,
                        limit=params.limit_per_subreddit
                    )
                else:
                    # General collection from subreddit
                    collected_posts = collector.collect_subreddit_posts(
                        subreddit_name=subreddit,
                        time_filter=params.timeFilter,
                        limit=params.limit_per_subreddit,
                        sort_method=params.sortMethod
                    )
                
                all_collected_posts.extend(collected_posts)
                collection_summary[subreddit] = len(collected_posts)
                
                print(f"Collected {len(collected_posts)} posts from r/{subreddit}")
                
            except Exception as e:
                print(f"Error collecting from r/{subreddit}: {str(e)}")
                collection_summary[subreddit] = 0
                continue
        
        if not all_collected_posts:
            return {
                "all_posts": [],
                "high_risk_posts": [],
                "medium_risk_posts": [],
                "low_risk_posts": [],
                "saved_files": [],
                "collection_summary": collection_summary
            }
        
        print(f"Total collected: {len(all_collected_posts)} posts from {len(subreddits_to_collect)} subreddits")
        
        # Analyze collected posts using existing analyzer
        analyzed_posts = collector.analyze_collected_posts(all_collected_posts, analyzer)
        
        # Generate filename based on parameters
        if params.include_all_defaults:
            filename = f"multi_all_defaults_{params.timeFilter}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        else:
            subreddit_names = "_".join(params.subreddits[:3])  # Limit filename length
            if len(params.subreddits) > 3:
                subreddit_names += f"_and_{len(params.subreddits)-3}_more"
            filename = f"multi_{subreddit_names}_{params.timeFilter}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Save raw posts
        collector.save_posts_to_json(all_collected_posts, f"{filename}_raw")
        collector.save_posts_to_csv(all_collected_posts, f"{filename}_raw")
        
        # Save analyzed posts
        analysis_summary = collector.save_analyzed_posts(analyzed_posts, filename)
        
        # Add collection summary to analysis
        analysis_summary['collection_summary'] = collection_summary
        analysis_summary['subreddits_collected'] = subreddits_to_collect
        
        # Prepare return data
        saved_files = [
            f"collected_data/raw_posts/{filename}_raw.json",
            f"collected_data/raw_posts/{filename}_raw.csv",
            f"collected_data/analyzed_posts/{filename}_analyzed.json"
        ]
        
        return {
            "all_posts": analyzed_posts,
            "high_risk_posts": analysis_summary.get("high_risk_posts", []),
            "medium_risk_posts": analysis_summary.get("medium_risk_posts", []),
            "low_risk_posts": analysis_summary.get("low_risk_posts", []),
            "saved_files": saved_files,
            "collection_summary": collection_summary,
            "subreddits_collected": subreddits_to_collect
        }
        
    except Exception as e:
        raise Exception(f"Multi-subreddit collection and analysis failed: {str(e)}")

@app.get("/api/reddit/config-status")
async def reddit_config_status():
    """Check Reddit API configuration status"""
    return {
        "is_configured": AppConfig.reddit.is_configured(),
        "missing_config": AppConfig.reddit.get_missing_config(),
        "user_agent": AppConfig.reddit.USER_AGENT if AppConfig.reddit.USER_AGENT else "Not configured",
        "rate_limit_delay": AppConfig.reddit.RATE_LIMIT_DELAY,
        "max_posts_per_request": AppConfig.reddit.MAX_POSTS_PER_REQUEST,
        "data_directory": AppConfig.DATA_DIR
    }

@app.get("/api/reddit/status")
async def reddit_collector_status():
    """Check if Reddit collector is available and configured"""
    try:
        # Check if collector can be imported
        AcademicRedditCollector = init_reddit_collector()
        collector_available = AcademicRedditCollector is not None
        
        # Check if data directories exist
        data_dir_exists = os.path.exists(AppConfig.DATA_DIR)
        raw_posts_dir = os.path.exists(os.path.join(AppConfig.DATA_DIR, "raw_posts"))
        analyzed_posts_dir = os.path.exists(os.path.join(AppConfig.DATA_DIR, "analyzed_posts"))
        
        return {
            "collector_available": collector_available,
            "reddit_configured": AppConfig.reddit.is_configured(),
            "data_directory_exists": data_dir_exists,
            "raw_posts_directory": raw_posts_dir,
            "analyzed_posts_directory": analyzed_posts_dir,
            "required_dependencies": [
                "praw (Python Reddit API Wrapper)",
                "python-dotenv (Environment configuration)"
            ],
            "setup_status": "ready" if (collector_available and AppConfig.reddit.is_configured()) else "needs_setup"
        }
        
    except Exception as e:
        return {
            "collector_available": False,
            "reddit_configured": False,
            "error": str(e),
            "setup_status": "error"
        }

@app.get("/api/reddit/files")
async def list_collected_files():
    """List all collected Reddit data files"""
    try:
        files_info = {
            "raw_files": [],
            "analyzed_files": [],
            "total_files": 0
        }
        
        # Check raw posts directory
        raw_dir = os.path.join(AppConfig.DATA_DIR, "raw_posts")
        if os.path.exists(raw_dir):
            raw_files = []
            for filename in os.listdir(raw_dir):
                if filename.endswith(('.json', '.csv')):
                    file_path = os.path.join(raw_dir, filename)
                    file_size = os.path.getsize(file_path)
                    file_modified = os.path.getmtime(file_path)
                    
                    raw_files.append({
                        "filename": filename,
                        "size_bytes": file_size,
                        "modified": datetime.fromtimestamp(file_modified).isoformat(),
                        "path": file_path
                    })
            files_info["raw_files"] = raw_files
        
        # Check analyzed posts directory
        analyzed_dir = os.path.join(AppConfig.DATA_DIR, "analyzed_posts")
        if os.path.exists(analyzed_dir):
            analyzed_files = []
            for filename in os.listdir(analyzed_dir):
                if filename.endswith('.json'):
                    file_path = os.path.join(analyzed_dir, filename)
                    file_size = os.path.getsize(file_path)
                    file_modified = os.path.getmtime(file_path)
                    
                    analyzed_files.append({
                        "filename": filename,
                        "size_bytes": file_size,
                        "modified": datetime.fromtimestamp(file_modified).isoformat(),
                        "path": file_path
                    })
            files_info["analyzed_files"] = analyzed_files
        
        files_info["total_files"] = len(files_info["raw_files"]) + len(files_info["analyzed_files"])
        
        return files_info
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list files: {str(e)}")

@app.get("/api/reddit/requirements")
async def get_setup_requirements():
    """Get setup requirements and instructions for Reddit collection"""
    return {
        "dependencies": {
            "praw": {
                "name": "Python Reddit API Wrapper",
                "install_command": "pip install praw",
                "version": ">=7.0.0",
                "purpose": "Reddit API access"
            },
            "python-dotenv": {
                "name": "Python Environment Variables",
                "install_command": "pip install python-dotenv",
                "version": ">=0.19.0",
                "purpose": "Configuration management"
            }
        },
        "setup_steps": [
            "1. Install dependencies: pip install praw python-dotenv",
            "2. Create .env file in backend directory",
            "3. Add Reddit API credentials to .env file",
            "4. Restart backend server",
            "5. Check configuration status via /api/reddit/config-status"
        ],
        "env_file_example": {
            "REDDIT_CLIENT_ID": "your_client_id_here",
            "REDDIT_CLIENT_SECRET": "your_client_secret_here",
            "REDDIT_USER_AGENT": "academic_research:weapons_detection:v2.0 (by /u/yourusername)"
        },
        "academic_requirements": [
            "Institutional Review Board (IRB) approval",
            "Compliance with Reddit Terms of Service",
            "Proper data handling and privacy protection",
            "Rate limiting and respectful API usage"
        ],
        "data_storage": {
            "location": f"{AppConfig.DATA_DIR}/ directory in your project",
            "formats": ["JSON", "CSV"],
            "privacy": "Usernames are hashed for privacy protection"
        }
    }





# -----------------------------
# LLM (Ollama) – non-invasive add-on
# -----------------------------
# --- Helpers ---
def _llm_should_run(rule_risk: float, user_toggle: bool, always_if_toggled: bool = False) -> bool:
    """
    Decide whether to call LLM:
      - user_toggle must be True
      - if always_if_toggled: call regardless
      - else triage band
    """
    if not user_toggle:
        return False
    if always_if_toggled:
        return True
    return 0.35 <= float(rule_risk) <= 0.75

def _safe_json_parse(text: str) -> Dict[str, Any]:
    """Try to parse strict JSON; fallback to first {...} blob."""
    try:
        return _json.loads(text)
    except Exception:
        pass
    m = _re.search(r"\{[\s\S]*\}", text)
    if m:
        try:
            return _json.loads(m.group(0))
        except Exception:
            pass
    # fallback minimal object
    return {
        "final_label": "MEDIUM",
        "risk_adjustment": 0.0,
        "reasons": ["fallback-parser"],
        "evidence_spans": [],
        "misclassification_risk": "MEDIUM",
    }

_LLM_PROMPT = """You are validating *suspected illegal weapons trade* in academic research text.

Return STRICT JSON exactly with this schema (no prose, no backticks):
{
  "final_label": "HIGH"|"MEDIUM"|"LOW",
  "risk_adjustment": <number between -1.0 and 1.0>,
  "reasons": ["short bullet 1", "short bullet 2"],
  "evidence_spans": ["verbatim span 1", "verbatim span 2"],
  "misclassification_risk": "LOW"|"MEDIUM"|"HIGH"
}

Constraints:
- Do NOT invent evidence; spans must appear verbatim in the text.
- Consider benign contexts (airsoft, cosplay, museums, video games, news quotes) as LOW unless there is clear transaction intent.
- Strong indicators: weapon mention + transaction intent (buy/sell/price/contact), quantity, shipping/delivery, obfuscation.

INPUT
-----
TEXT:
\"\"\"{TEXT}\"\"\"

RULE_FLAGS: {RULE_FLAGS}
KEYWORDS: {KEYWORDS}
PATTERNS: {PATTERNS}
CURRENT_RULE_RISK: {RULE_RISK}
"""

def _ollama_classify(prompt: str) -> Dict[str, Any]:
    if _requests is None:
        raise RuntimeError("requests is not installed. Run: pip install requests")

    resp = _requests.post(
        f"{_OLLAMA_BASE}/api/chat",
        json={
            "model": _OLLAMA_MODEL,
            "messages": [
                {"role": "system", "content": "You are a precise risk classifier that returns strict JSON only."},
                {"role": "user", "content": prompt},
            ],
            "options": {"temperature": 0},
        },
        timeout=120,
    )
    resp.raise_for_status()
    data = resp.json()
    txt = data.get("message", {}).get("content", "{}")
    return _safe_json_parse(txt)

def _llm_validate(text: str,
                  rule_flags: List[str],
                  keywords: List[str],
                  patterns: List[str],
                  rule_risk: float) -> Dict[str, Any]:
    """Provider switch (Path A = Ollama only)."""
    if _LLM_PROVIDER != "ollama":
        return {}
    prompt = _LLM_PROMPT.format(
        TEXT=text[:8000],
        RULE_FLAGS=_json.dumps(rule_flags, ensure_ascii=False),
        KEYWORDS=_json.dumps(keywords, ensure_ascii=False),
        PATTERNS=_json.dumps(patterns, ensure_ascii=False),
        RULE_RISK=round(float(rule_risk), 3),
    )
    return _ollama_classify(prompt)

def _combine_scores(rule_score: float, llm_adj: float, max_shift: float = 0.2) -> _Tuple[float, str]:
    """Clamp LLM numeric influence to keep system stable."""
    try:
        adj = float(llm_adj)
    except Exception:
        adj = 0.0
    adj = max(-1.0, min(1.0, adj))
    combined = max(0.0, min(1.0, float(rule_score) + adj * max_shift))
    if combined >= 0.7:
        lvl = "HIGH"
    elif combined >= 0.4:
        lvl = "MEDIUM"
    else:
        lvl = "LOW"
    return combined, lvl

def _label_for(score: float) -> str:
    return "HIGH" if score >= 0.7 else "MEDIUM" if score >= 0.4 else "LOW"

# -----------------------------
# Status endpoint for LLM
# -----------------------------
@app.get("/api/llm/status")
async def llm_status():
    ok = True
    problems = []
    if _LLM_PROVIDER != "ollama":
        problems.append(f"LLM_PROVIDER={_LLM_PROVIDER} (expected 'ollama' for Path A).")
        ok = False
    if _requests is None:
        problems.append("python-requests not installed.")
        ok = False
    # Try a quick ping only if requests is available
    reachable = False
    if _requests is not None and _LLM_PROVIDER == "ollama":
        try:
            r = _requests.get(f"{_OLLAMA_BASE}/api/tags", timeout=3)
            reachable = r.status_code == 200
        except Exception as e:
            problems.append(f"Ollama not reachable at {_OLLAMA_BASE}: {e}")
            ok = False

    return {
        "provider": _LLM_PROVIDER,
        "ollama_base": _OLLAMA_BASE,
        "model": _OLLAMA_MODEL,
        "requests_installed": _requests is not None,
        "ollama_reachable": reachable,
        "ok": ok and reachable,
        "problems": problems,
    }

# -----------------------------
# NEW: Hybrid analyze endpoint (rules + optional LLM)
# Does NOT modify your existing /api/detection/analyze
# -----------------------------

@app.post("/api/detection/analyze_llm")
async def analyze_content_llm(
    request: Dict[str, Any],
    use_llm: bool = _Query(False, description="Enable LLM verification"),
    always_if_toggled: bool = _Query(False, description="If true, always call LLM when toggled (skip triage band)"),
):
    """
    Hybrid analysis:
      1) Run your existing rule engine (same as /api/detection/analyze)
      2) Optionally call LLM (Ollama) to verify/adjust
      3) Return combined result with provenance fields
    """
    content = request.get("content", "")
    if not content:
        raise HTTPException(status_code=400, detail="No content provided")

    # --- (1) Rules-first: reuse your analyzer as-is ---
    analysis_results = analyzer.analyze_text(content)
    rule_risk = float(analysis_results["risk_score"])
    rule_level = _label_for(rule_risk)

    base = {
        "analysis_id": f"analysis_{int(datetime.now().timestamp())}",
        "status": "completed",
        "risk_score": rule_risk,
        "risk_level": rule_level,
        "confidence": analysis_results["confidence"],
        "flags": analysis_results["flags"],
        "detected_keywords": analysis_results["detected_keywords"],
        "detected_patterns": analysis_results["detected_patterns"],
        "summary": f"Rules-only: {len(analysis_results['flags'])} indicators.",
        "timestamp": analysis_results["analysis_time"],
        "source": "rules",
    }

    # --- (2) Optional LLM stage ---
    if _llm_should_run(rule_risk, use_llm, always_if_toggled=always_if_toggled):
        try:
            llm = _llm_validate(
                text=content,
                rule_flags=base["flags"],
                keywords=base["detected_keywords"],
                patterns=base["detected_patterns"],
                rule_risk=rule_risk,
            ) or {}
            combined_score, combined_level = _combine_scores(rule_risk, llm.get("risk_adjustment", 0.0), max_shift=0.2)
            base.update({
                "risk_score": combined_score,
                "risk_level": llm.get("final_label", combined_level),
                "llm_reasons": llm.get("reasons", []),
                "llm_evidence_spans": llm.get("evidence_spans", []),
                "llm_misclassification_risk": llm.get("misclassification_risk", "MEDIUM"),
                "summary": f"Hybrid: rules + LLM ({llm.get('final_label', combined_level)})",
                "source": "hybrid",
            })
        except Exception as e:
            # LLM failure should never break analysis; fall back gracefully
            base.update({
                "llm_error": str(e),
                "source": "rules"
            })

    return base




if __name__ == "__main__":
    uvicorn.run("server:app", host=AppConfig.HOST, port=AppConfig.PORT, reload=AppConfig.DEBUG)