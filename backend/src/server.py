import sys
import os
import logging
import uuid
from dataclasses import dataclass, field
from enum import Enum
import threading
# Log file path
LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'server.log')

# Configure logging - output to both stdout AND file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_FILE, mode='a')
    ],
    force=True
)
# Set uvicorn loggers to show our logs
logging.getLogger("uvicorn").setLevel(logging.INFO)
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)  # Less noise from access logs

logger = logging.getLogger("WeaponsDetectionAPI")
logger.setLevel(logging.DEBUG)

# Also print directly for immediate visibility
def log_print(msg):
    """Print and flush immediately for live logs"""
    print(msg, flush=True)
    logger.info(msg)

# Get the directory containing this file (src/)
src_dir = os.path.dirname(os.path.abspath(__file__))
# Get the backend root directory
backend_dir = os.path.dirname(src_dir)

# Add both src and backend root to path
sys.path.insert(0, src_dir)  # For relative imports within src/
sys.path.insert(0, backend_dir)  # For imports from backend root (config, generation)

# Standard library imports
from datetime import datetime  # noqa: E402
from typing import Dict, List, Any, Optional, Tuple as _Tuple, Literal  # noqa: E402
import json as _json  # noqa: E402
import re as _re  # noqa: E402
import asyncio  # noqa: E402
from concurrent.futures import ThreadPoolExecutor  # noqa: E402

# Third-party imports
from fastapi import FastAPI, HTTPException, Query as _Query  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from fastapi.responses import StreamingResponse, Response  # noqa: E402
from pydantic import BaseModel, Field  # noqa: E402
import requests as _requests  # noqa: E402
import uvicorn  # noqa: E402

# SSE streaming support
try:
    from sse_starlette.sse import EventSourceResponse
    SSE_AVAILABLE = True
except ImportError:
    SSE_AVAILABLE = False
    EventSourceResponse = None

# Local imports (after path setup)
from detection.text_analyzer import WeaponsTextAnalyzer  # noqa: E402
from config import AppConfig  # noqa: E402
from generation.content_generator import SyntheticContentGenerator, ContentParameters  # noqa: E402
from reports import build_osint_pdf  # noqa: E402 — lazy; reportlab loaded on first PDF only

# --- ENV / Config (uses your existing AppConfig where convenient) ---
_LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama").lower()
_OLLAMA_BASE = os.getenv("OLLAMA_BASE", "http://localhost:11434")
_OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")

# =============================================================================
# BACKGROUND JOB SYSTEM - Collections persist across page navigation/refresh
# =============================================================================


class JobStatus(str, Enum):
    PENDING = "pending"
    COLLECTING = "collecting"
    ANALYZING = "analyzing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class CollectionJob:
    """Represents a background collection job"""
    id: str
    platform: str
    sources: List[str]
    limit: int
    status: JobStatus = JobStatus.PENDING
    progress: int = 0
    total: int = 0
    phase_message: str = ""
    posts: List[Dict] = field(default_factory=list)
    summary: Optional[Dict] = None
    error: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "platform": self.platform,
            "sources": self.sources,
            "limit": self.limit,
            "status": self.status.value,
            "progress": self.progress,
            "total": self.total,
            "phase_message": self.phase_message,
            "posts_count": len(self.posts),
            "summary": self.summary,
            "error": self.error,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

class JobStore:
    """In-memory store for collection jobs - persists across frontend disconnects"""
    def __init__(self):
        self._jobs: Dict[str, CollectionJob] = {}
        self._lock = threading.Lock()
        self._current_job_id: Optional[str] = None  # Track active job
    
    def create_job(self, platform: str, sources: List[str], limit: int) -> CollectionJob:
        job_id = str(uuid.uuid4())[:8]
        job = CollectionJob(
            id=job_id,
            platform=platform,
            sources=sources,
            limit=limit,
            total=len(sources) * limit
        )
        with self._lock:
            self._jobs[job_id] = job
            self._current_job_id = job_id
        return job
    
    def get_job(self, job_id: str) -> Optional[CollectionJob]:
        return self._jobs.get(job_id)
    
    def get_current_job(self) -> Optional[CollectionJob]:
        if self._current_job_id:
            return self._jobs.get(self._current_job_id)
        return None
    
    def get_active_job(self) -> Optional[CollectionJob]:
        """Get any job that's currently running"""
        for job in self._jobs.values():
            if job.status in [JobStatus.PENDING, JobStatus.COLLECTING, JobStatus.ANALYZING]:
                return job
        return None
    
    def update_job(self, job_id: str, **kwargs):
        job = self._jobs.get(job_id)
        if job:
            for key, value in kwargs.items():
                if hasattr(job, key):
                    setattr(job, key, value)
            job.updated_at = datetime.now().isoformat()
    
    def add_post(self, job_id: str, post: Dict):
        job = self._jobs.get(job_id)
        if job:
            job.posts.append(post)
            job.progress = len(job.posts)
            job.updated_at = datetime.now().isoformat()
    
    def cancel_job(self, job_id: str):
        job = self._jobs.get(job_id)
        if job and job.status in [JobStatus.PENDING, JobStatus.COLLECTING, JobStatus.ANALYZING]:
            job.status = JobStatus.CANCELLED
            job.updated_at = datetime.now().isoformat()
            if self._current_job_id == job_id:
                self._current_job_id = None
    
    def list_jobs(self, limit: int = 10) -> List[Dict]:
        jobs = sorted(self._jobs.values(), key=lambda j: j.created_at, reverse=True)
        return [j.to_dict() for j in jobs[:limit]]
    
    def cleanup_old_jobs(self, max_age_hours: int = 24):
        """Remove jobs older than max_age_hours"""
        now = datetime.now()
        with self._lock:
            to_remove = []
            for job_id, job in self._jobs.items():
                created = datetime.fromisoformat(job.created_at)
                age_hours = (now - created).total_seconds() / 3600
                if age_hours > max_age_hours and job.status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]:
                    to_remove.append(job_id)
            for job_id in to_remove:
                del self._jobs[job_id]

# Global job store instance
job_store = JobStore()


# Create FastAPI app
app = FastAPI(
    title="Weapons Detection API",
    description="Academic research system for detecting illegal weapons trade patterns",
    version="2.1.0",
)

# Initialize components
analyzer = WeaponsTextAnalyzer()
content_generator = SyntheticContentGenerator()

# CORS middleware (localhost + 127.0.0.1, any port — PDF/blob fetch fails closed if origin mismatches)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)


async def _ollama_list_models() -> _Tuple[List[str], Optional[str]]:
    """Return (installed_model_names, error_message). error_message set if unreachable."""
    import httpx as _httpx

    base = (AppConfig.ollama.BASE or "").rstrip("/")
    if not base:
        return [], "OLLAMA_BASE is empty"
    try:
        async with _httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{base}/api/tags")
            if response.status_code != 200:
                return [], f"Ollama at {base} returned HTTP {response.status_code}"
            data = response.json()
            names = [m.get("name", "") for m in data.get("models", []) if m.get("name")]
            return names, None
    except Exception as e:
        return [], f"Cannot reach Ollama at {base}: {e}"


def _ollama_has_model(model_names: List[str], want: str) -> bool:
    if not want or not model_names:
        return False
    want_l = want.lower()
    for m in model_names:
        ml = m.lower()
        if want_l == ml or want_l in ml or ml in want_l:
            return True
    return False


async def _require_ollama_if_mandatory(*, llm: bool, vision: bool) -> None:
    """Raise HTTP 503 when OLLAMA_MANDATORY and Ollama or required models are unavailable."""
    if not AppConfig.ollama.MANDATORY:
        return
    names, err = await _ollama_list_models()
    if err:
        raise HTTPException(
            status_code=503,
            detail=f"Ollama is required (OLLAMA_MANDATORY=true) but unavailable: {err}",
        )
    if llm and not _ollama_has_model(names, AppConfig.ollama.MODEL):
        raise HTTPException(
            status_code=503,
            detail=(
                f"Ollama is required but text model '{AppConfig.ollama.MODEL}' is not available. "
                f"Installed: {names}. Example: ollama pull {AppConfig.ollama.MODEL}"
            ),
        )
    if vision and not _ollama_has_model(names, AppConfig.ollama.VISION_MODEL):
        raise HTTPException(
            status_code=503,
            detail=(
                f"Ollama is required for vision but model '{AppConfig.ollama.VISION_MODEL}' is not available. "
                f"Installed: {names}. Example: ollama pull {AppConfig.ollama.VISION_MODEL}"
            ),
        )


# =============================================================================
# JOB API ENDPOINTS - For persistent background collection jobs
# =============================================================================

@app.get("/api/jobs/current")
async def get_current_job():
    """Get the currently active job (if any) - for reconnecting after page refresh"""
    job = job_store.get_active_job()
    log_print(f"🔄 Checking for active job: {'Found ' + job.id if job else 'None'}")
    if job:
        return {
            "has_active_job": True,
            "job": job.to_dict(),
            "posts": job.posts[-50:]  # Return last 50 posts for live view
        }
    return {"has_active_job": False, "job": None, "posts": []}

@app.get("/api/jobs/{job_id}")
async def get_job_status(job_id: str):
    """Get status and results of a specific job"""
    job = job_store.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {
        "job": job.to_dict(),
        "posts": job.posts  # Include all collected posts
    }

@app.get("/api/jobs/{job_id}/posts")
async def get_job_posts(job_id: str, offset: int = 0, limit: int = 50):
    """Get posts from a job with pagination"""
    job = job_store.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {
        "total": len(job.posts),
        "offset": offset,
        "limit": limit,
        "posts": job.posts[offset:offset + limit]
    }

@app.post("/api/jobs/{job_id}/cancel")
async def cancel_job(job_id: str):
    """Cancel a running job"""
    job = job_store.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status not in [JobStatus.PENDING, JobStatus.COLLECTING, JobStatus.ANALYZING]:
        raise HTTPException(status_code=400, detail="Job is not running")
    job_store.cancel_job(job_id)
    return {"success": True, "message": "Job cancelled"}

@app.get("/api/jobs")
async def list_jobs(limit: int = 10):
    """List recent jobs"""
    return {"jobs": job_store.list_jobs(limit)}


class StartJobRequest(BaseModel):
    platform: str = "reddit"
    sources: List[str]  # subreddits or channels
    limit: int = 10
    analyze_images: bool = True
    llm_analysis: bool = True


# Background collection task that runs independently of SSE connection
async def run_background_collection(job_id: str, platform: str, sources: List[str], 
                                     limit: int, analyze_images: bool, llm_analysis: bool):
    """Run collection in background - survives frontend disconnect"""
    job = job_store.get_job(job_id)
    if not job:
        return
    
    try:
        log_print(f"🚀 Background job {job_id} started: {platform} - {sources}")
        job_store.update_job(job_id, status=JobStatus.COLLECTING, phase_message="Collecting posts...")

        if platform == "telegram":
            tg = AppConfig.telegram
            if not tg.user_api_credentials_ok():
                raise RuntimeError(
                    "Telegram API not configured: " + ", ".join(tg.get_missing_user_api_config())
                )
            if not tg.has_session_file():
                searched = ", ".join(str(p) for p in tg.session_file_candidates())
                raise RuntimeError(
                    f"No Telegram session file found. Checked: {searched}. "
                    "Run: python scripts/telegram_auth.py (from backend/) or set TELEGRAM_SESSION_DIR."
                )

            from telethon import TelegramClient
            from backend_service.telegram_stream_analysis import (
                analyze_telegram_item,
                collect_telegram_items,
                telegram_session_arg_from_config,
            )

            client = TelegramClient(
                telegram_session_arg_from_config(tg),
                tg.API_ID,
                tg.API_HASH,
            )
            await client.connect()
            if not await client.is_user_authorized():
                await client.disconnect()
                raise RuntimeError("Telegram session not authorized. Run: python scripts/telegram_auth.py")

            try:
                all_items = await collect_telegram_items(client, sources, limit, log_print)
                log_print(f"📥 Job {job_id}: Collected {len(all_items)} Telegram messages")
                if not all_items:
                    job_store.update_job(
                        job_id,
                        status=JobStatus.COMPLETED,
                        phase_message="No Telegram messages collected.",
                        summary={
                            "total_collected": 0,
                            "high_risk_count": 0,
                            "medium_risk_count": 0,
                            "low_risk_count": 0,
                            "sources": sources,
                            "hint": "No messages from the given channels. Check usernames are public, "
                            "remove @ from URLs, or try t.me/username links. Verify login: python scripts/telegram_auth.py",
                            "timestamp": datetime.now().isoformat(),
                        },
                    )
                    log_print(f"⚠️ Job {job_id}: 0 Telegram messages — check channels and session")
                    return

                job_store.update_job(
                    job_id,
                    status=JobStatus.ANALYZING,
                    phase_message="Analyzing messages with AI...",
                    total=max(1, len(all_items)),
                )

                image_analyzer = None
                llm_analyzer_inst = None
                if analyze_images:
                    try:
                        from backend_service.handlers.image_analysis_handler import ImageAnalysisHandler
                        image_analyzer = ImageAnalysisHandler(
                            ollama_base=AppConfig.ollama.BASE,
                            vision_model=AppConfig.ollama.VISION_MODEL,
                            timeout=180,
                        )
                    except ImportError:
                        pass
                if llm_analysis:
                    try:
                        from backend_service.handlers.llm_text_analyzer import LLMTextAnalyzer
                        llm_analyzer_inst = LLMTextAnalyzer(
                            ollama_base=AppConfig.ollama.BASE,
                            model=AppConfig.ollama.MODEL,
                            timeout=120,
                        )
                    except ImportError:
                        pass

                vision_available = (
                    await image_analyzer.check_model_available() if image_analyzer else False
                )
                llm_available = (
                    await llm_analyzer_inst.check_model_available() if llm_analyzer_inst else False
                )

                # Analyze every collected message (matches Telegram SSE: full pass, then UI may filter).
                # Reddit jobs still pre-filter at 0.25; Telegram channels are often news text below that
                # until LLM runs, so pre-filtering here produced empty jobs and no Telegram in the UI.
                posts_to_analyze: List[Dict[str, Any]] = []
                for item in all_items:
                    if job_store.get_job(job_id).status == JobStatus.CANCELLED:
                        log_print(f"❌ Job {job_id} cancelled during collection")
                        return
                    posts_to_analyze.append(item)

                log_print(
                    f"📊 Job {job_id}: queued {len(posts_to_analyze)} Telegram messages for AI analysis"
                )
                job_store.update_job(job_id, total=max(1, len(posts_to_analyze)))

                analyzed_count = [0]
                for i, item in enumerate(posts_to_analyze):
                    if job_store.get_job(job_id).status == JobStatus.CANCELLED:
                        log_print(f"❌ Job {job_id} cancelled during Telegram analysis")
                        return
                    try:
                        result = await analyze_telegram_item(
                            analyzer=analyzer,
                            item=item,
                            client=client,
                            image_analyzer=image_analyzer,
                            llm_analyzer=llm_analyzer_inst,
                            vision_available=vision_available,
                            llm_available=llm_available,
                            analyze_images=analyze_images,
                            llm_analysis=llm_analysis,
                            idx=i + 1,
                            total=len(posts_to_analyze),
                            log_print=log_print,
                        )
                        job_store.add_post(job_id, result["post_data"])
                        analyzed_count[0] += 1
                        job_store.update_job(
                            job_id,
                            progress=analyzed_count[0],
                            phase_message=f"Analyzed {analyzed_count[0]}/{len(posts_to_analyze)} messages",
                        )
                    except Exception as msg_err:
                        log_print(f"❌ Job {job_id} Telegram message analysis failed: {msg_err}")

                job = job_store.get_job(job_id)
                summary = {
                    "total_collected": len(job.posts),
                    "high_risk_count": sum(
                        1
                        for p in job.posts
                        if p.get("risk_analysis", {}).get("risk_level") in ("HIGH", "CRITICAL")
                    ),
                    "medium_risk_count": sum(
                        1 for p in job.posts if p.get("risk_analysis", {}).get("risk_level") == "MEDIUM"
                    ),
                    "low_risk_count": sum(
                        1 for p in job.posts if p.get("risk_analysis", {}).get("risk_level") == "LOW"
                    ),
                    "sources": sources,
                    "timestamp": datetime.now().isoformat(),
                }
                job_store.update_job(
                    job_id, status=JobStatus.COMPLETED, summary=summary, phase_message="Complete!"
                )
                log_print(f"✅ Job {job_id} completed: {len(job.posts)} Telegram messages analyzed")
            finally:
                await client.disconnect()
            return

        # --- Reddit ---
        from backend_service.handlers.reddit_handler import RedditHandler
        
        handler = RedditHandler(
            client_id=AppConfig.reddit.CLIENT_ID,
            client_secret=AppConfig.reddit.CLIENT_SECRET,
            user_agent=AppConfig.reddit.USER_AGENT
        )
        
        # Collect posts (PRAW is synchronous — never call it on the asyncio event loop)
        all_posts = []
        for source in sources:
            if job_store.get_job(job_id).status == JobStatus.CANCELLED:
                log_print(f"❌ Job {job_id} cancelled during collection")
                return
            try:
                posts = await asyncio.to_thread(
                    handler.collect_subreddit_posts,
                    source,
                    "day",
                    limit,
                    "hot",
                )
                all_posts.extend(posts)
                log_print(f"📥 Job {job_id}: Collected {len(posts)} from r/{source}")
            except Exception as e:
                log_print(f"❌ Job {job_id}: Error collecting from r/{source}: {e}")
        
        job_store.update_job(job_id, 
                            status=JobStatus.ANALYZING, 
                            phase_message="Analyzing posts with AI...",
                            total=len(all_posts))
        
        # Initialize analyzers
        image_analyzer = None
        llm_analyzer_inst = None
        
        if analyze_images:
            try:
                from backend_service.handlers.image_analysis_handler import ImageAnalysisHandler
                image_analyzer = ImageAnalysisHandler(
                    ollama_base=AppConfig.ollama.BASE,
                    vision_model=AppConfig.ollama.VISION_MODEL,
                    timeout=180  # Allow 3 minutes for CPU-based vision
                )
            except ImportError:
                pass
        
        if llm_analysis:
            try:
                from backend_service.handlers.llm_text_analyzer import LLMTextAnalyzer
                llm_analyzer_inst = LLMTextAnalyzer(
                    ollama_base=AppConfig.ollama.BASE,
                    model=AppConfig.ollama.MODEL,
                    timeout=120  # 2 minutes for CPU-based LLM
                )
                log_print(f"📝 LLM initialized: model={AppConfig.ollama.MODEL}")
            except ImportError:
                pass
        
        # Pre-filter posts by text risk score (fast, no AI needed)
        posts_to_analyze = []
        for post in all_posts:
            combined_text = f"{post.title} {post.content or ''}"
            analysis = analyzer.analyze_text(combined_text)
            risk_score = analysis.get('risk_score', 0)
            if risk_score >= 0.25:  # Only analyze posts with some risk
                posts_to_analyze.append((post, analysis, risk_score))
        
        log_print(f"📊 Job {job_id}: {len(posts_to_analyze)}/{len(all_posts)} posts need AI analysis")
        job_store.update_job(job_id, total=len(posts_to_analyze))
        
        # Sequential analysis (Ollama CPU can only handle 1 at a time)
        semaphore = asyncio.Semaphore(1)
        analyzed_count = [0]  # Use list for mutable counter in closure
        
        async def analyze_single_post(post, analysis, base_risk_score):
            """Analyze a single post with LLM and image analysis"""
            async with semaphore:
                if job_store.get_job(job_id).status == JobStatus.CANCELLED:
                    return None
                
                risk_score = base_risk_score
                if risk_score >= 0.75:
                    risk_level = 'HIGH'
                elif risk_score >= 0.45:
                    risk_level = 'MEDIUM'
                else:
                    risk_level = 'LOW'
                
                # LLM analysis
                llm_result = None
                if llm_analyzer_inst:
                    try:
                        llm_response = await llm_analyzer_inst.analyze_post(
                            title=post.title,
                            content=post.content or '',
                            source=post.subreddit
                        )
                        llm_result = llm_response.to_dict()
                    except Exception as e:
                        log_print(f"⚠️ Job {job_id}: LLM error: {e}")
                
                # Image analysis (enabled with 60s timeout)
                image_analysis_result = None
                annotated_image = None
                if image_analyzer and post.image_url and not post.is_video:
                    try:
                        image_result = await image_analyzer.analyze_image(post.image_url)
                        if image_result.contains_weapons:
                            image_analysis_result = {
                                'contains_weapons': True,
                                'weapon_count': image_result.weapon_count,
                                'detections': [d.to_dict() for d in image_result.detections],
                                'overall_risk': image_result.overall_risk,
                                'analysis_notes': image_result.analysis_notes,
                                'processing_time_ms': image_result.processing_time_ms
                            }
                            annotated_image = image_result.annotated_image_base64
                            if image_result.overall_risk == 'HIGH':
                                risk_level = 'HIGH'
                                risk_score = max(risk_score, image_result.risk_score)
                        else:
                            image_analysis_result = {
                                'contains_weapons': False,
                                'weapon_count': 0,
                                'image_verified_safe': image_result.analysis_completed,
                                'analysis_completed': image_result.analysis_completed,
                                'analysis_notes': image_result.analysis_notes,
                                'processing_time_ms': image_result.processing_time_ms
                            }
                    except Exception as e:
                        log_print(f"⚠️ Job {job_id}: Image error: {e}")
                        image_analysis_result = {'error': str(e), 'contains_weapons': False}
                
                from backend_service.utils.location_resolver import resolve_post_location

                combined_for_geo = f"{post.title} {post.content or ''}"
                geo_location = resolve_post_location(
                    text=combined_for_geo,
                    image_url=post.image_url if not post.is_video else None,
                    subreddit=post.subreddit,
                    author_flair=getattr(post, 'author_flair_text', None),
                    link_flair=getattr(post, 'link_flair_text', None),
                    link_url=post.url,
                    domain=getattr(post, 'domain', None),
                    llm_text=(llm_result or {}).get('summary') if llm_result else None,
                )

                # Build post data
                post_data = {
                    'id': post.id,
                    'title': post.title,
                    'content': post.content[:500] if post.content else '',
                    'subreddit': post.subreddit,
                    'author_hash': post.author_hash,
                    'score': post.score,
                    'num_comments': post.num_comments,
                    'url': post.url,
                    'created_utc': post.created_at,
                    'collected_at': post.collected_at,
                    'platform': 'reddit',
                    'image_url': post.image_url,
                    'thumbnail': post.thumbnail,
                    'media_type': post.media_type,
                    'gallery_images': getattr(post, 'gallery_images', None),
                    'is_video': post.is_video,
                    'video_url': post.video_url,
                    'image_analysis': image_analysis_result,
                    'annotated_image': annotated_image,
                    'llm_analysis': llm_result,
                    'risk_analysis': {
                        'risk_score': risk_score,
                        'risk_level': risk_level,
                        'confidence': analysis.get('confidence', 0),
                        'flags': analysis.get('flags', []),
                        'detected_keywords': analysis.get('detected_keywords', []),
                        'detected_patterns': analysis.get('detected_patterns', [])
                    },
                    'geo_location': geo_location,
                }
                
                # Add post IMMEDIATELY as it completes (don't wait for others)
                job_store.add_post(job_id, post_data)
                analyzed_count[0] += 1
                job_store.update_job(job_id, progress=analyzed_count[0], 
                                    phase_message=f"Analyzed {analyzed_count[0]}/{len(posts_to_analyze)} posts")
                
                return post_data
        
        # Run all analyses in parallel (limited by semaphore)
        tasks = [analyze_single_post(post, analysis, risk_score) 
                 for post, analysis, risk_score in posts_to_analyze]
        await asyncio.gather(*tasks, return_exceptions=True)
        
        # Complete the job
        job = job_store.get_job(job_id)
        summary = {
            "total_collected": len(job.posts),
            "high_risk_count": sum(1 for p in job.posts if p.get('risk_analysis', {}).get('risk_level') == 'HIGH'),
            "medium_risk_count": sum(1 for p in job.posts if p.get('risk_analysis', {}).get('risk_level') == 'MEDIUM'),
            "low_risk_count": sum(1 for p in job.posts if p.get('risk_analysis', {}).get('risk_level') == 'LOW'),
            "sources": sources,
            "timestamp": datetime.now().isoformat()
        }
        job_store.update_job(job_id, status=JobStatus.COMPLETED, summary=summary, phase_message="Complete!")
        log_print(f"✅ Job {job_id} completed: {len(job.posts)} posts analyzed")
        
    except Exception as e:
        log_print(f"❌ Job {job_id} failed: {e}")
        job_store.update_job(job_id, status=JobStatus.FAILED, error=str(e))


@app.post("/api/jobs/start")
async def start_collection_job(request: StartJobRequest):
    """Start a background collection job that persists across page navigation"""
    if request.platform not in ("reddit", "telegram"):
        d = "platform must be 'reddit' or 'telegram'"
        log_print(f"❌ POST /api/jobs/start 400: {d} (got platform={request.platform!r})")
        raise HTTPException(status_code=400, detail=d)
    if request.platform == "reddit" and not AppConfig.reddit.is_configured():
        d = "Reddit API not configured: " + ", ".join(AppConfig.reddit.get_missing_config())
        log_print(f"❌ POST /api/jobs/start 400: {d}")
        raise HTTPException(status_code=400, detail=d)
    if request.platform == "telegram":
        tg = AppConfig.telegram
        if not tg.user_api_credentials_ok():
            d = "Telegram user API not configured: " + ", ".join(tg.get_missing_user_api_config())
            log_print(f"❌ POST /api/jobs/start 400: {d}")
            raise HTTPException(status_code=400, detail=d)
        if not tg.has_session_file():
            searched = ", ".join(str(p) for p in tg.session_file_candidates())
            d = (
                f"No Telegram session file found. Checked: {searched}. "
                "Run: cd backend && python scripts/telegram_auth.py "
                "(or set TELEGRAM_SESSION_DIR to the folder that contains your .session file)."
            )
            log_print(f"❌ POST /api/jobs/start 400: {d}")
            raise HTTPException(status_code=400, detail=d)

    sources = list(request.sources)
    if request.platform == "telegram":
        from backend_service.telegram_stream_analysis import normalize_telegram_sources

        sources = normalize_telegram_sources(sources)
        if not sources:
            d = "No valid Telegram channel usernames. Use public @channel names or t.me/channel links."
            log_print(f"❌ POST /api/jobs/start 400: {d} (raw sources={request.sources!r})")
            raise HTTPException(status_code=400, detail=d)

    # Check if there's already an active job
    active = job_store.get_active_job()
    if active:
        d = f"A job is already running (ID: {active.id}). Cancel it first or wait for completion."
        log_print(f"❌ POST /api/jobs/start 400: {d}")
        raise HTTPException(status_code=400, detail=d)

    await _require_ollama_if_mandatory(llm=request.llm_analysis, vision=request.analyze_images)
    
    # Create the job
    job = job_store.create_job(
        platform=request.platform,
        sources=sources,
        limit=request.limit
    )
    
    # Start background task
    asyncio.create_task(run_background_collection(
        job_id=job.id,
        platform=request.platform,
        sources=sources,
        limit=request.limit,
        analyze_images=request.analyze_images,
        llm_analysis=request.llm_analysis
    ))
    
    return {
        "success": True,
        "job_id": job.id,
        "message": "Collection job started in background"
    }


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

class BigDataGenerationRequest(BaseModel):
    total_quantity: int = Field(default=2000, ge=100, le=10000, description="Total number of posts to generate")
    platforms: List[str] = Field(default=["reddit", "twitter", "facebook", "instagram"], description="Platforms to generate for")
    content_lengths: List[str] = Field(default=["short", "medium", "long"], description="Content lengths to include")

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


class OsintPdfRequest(BaseModel):
    """Payload for OSINT-style PDF export (single item, text analysis, or multi-session digest)."""
    report_type: Literal["collection_item", "text_analysis", "collection_digest"]
    report_title: Optional[str] = None
    report_id: Optional[str] = None
    record_id: Optional[str] = None
    id: Optional[str] = None
    platform: Optional[str] = None
    title: Optional[str] = None
    content: Optional[str] = None
    source_url: Optional[str] = None
    url: Optional[str] = None
    author_hash: Optional[str] = None
    collected_at: Optional[str] = None
    channel: Optional[str] = None
    subreddit: Optional[str] = None
    risk_analysis: Optional[Dict[str, Any]] = None
    llm_analysis: Optional[Dict[str, Any]] = None
    image_analysis: Optional[Dict[str, Any]] = None
    source_text: Optional[str] = None
    context_title: Optional[str] = None
    analysis_id: Optional[str] = None
    risk_score: Optional[float] = None
    risk_level: Optional[str] = None
    confidence: Optional[float] = None
    flags: Optional[List[str]] = None
    detected_keywords: Optional[List[str]] = None
    detected_patterns: Optional[List[str]] = None
    summary: Optional[str] = None
    timestamp: Optional[str] = None
    status: Optional[str] = None
    # collection_digest: consolidated History + Dashboard workspace
    aggregate_stats: Optional[Dict[str, Any]] = None
    sessions: Optional[List[Dict[str, Any]]] = None
    standalone_posts: Optional[List[Dict[str, Any]]] = None
    job_summary: Optional[Dict[str, Any]] = None
    job_meta: Optional[Dict[str, Any]] = None


def _osint_pdf_payload_char_estimate(obj: Any) -> int:
    if obj is None:
        return 0
    if isinstance(obj, str):
        return len(obj)
    if isinstance(obj, (int, float, bool)):
        return 0
    if isinstance(obj, dict):
        return sum(_osint_pdf_payload_char_estimate(v) for v in obj.values())
    if isinstance(obj, list):
        return sum(_osint_pdf_payload_char_estimate(v) for v in obj)
    return len(str(obj))


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
    logger.debug("🏥 Health check requested")
    telegram_configured = AppConfig.telegram.is_configured()
    
    # Check Ollama availability
    ollama_models: List[str] = []
    ollama_reachable = False
    try:
        import httpx
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{AppConfig.ollama.BASE}/api/tags")
            if response.status_code == 200:
                models_data = response.json()
                ollama_models = [m['name'] for m in models_data.get('models', [])]
                ollama_reachable = True
                logger.debug(f"✅ Ollama reachable, models={ollama_models}")
            else:
                logger.warning(f"⚠️ Ollama returned status {response.status_code}")
    except httpx.ConnectError as e:
        logger.warning(f"⚠️ Cannot connect to Ollama at {AppConfig.ollama.BASE}: {e}")
    except Exception as e:
        logger.warning(f"⚠️ Ollama check failed: {type(e).__name__}: {e}")

    text_model_ok = _ollama_has_model(ollama_models, AppConfig.ollama.MODEL) if ollama_reachable else False
    vision_model_ok = _ollama_has_model(ollama_models, AppConfig.ollama.VISION_MODEL) if ollama_reachable else False
    has_llm = any('llama' in m.lower() for m in ollama_models)
    has_vision = any('llava' in m.lower() for m in ollama_models)
    ollama_available = ollama_reachable and (has_vision or has_llm)
    mandatory = AppConfig.ollama.MANDATORY
    pipeline_ok = ollama_reachable and text_model_ok
    if mandatory and not pipeline_ok:
        overall = "degraded"
    else:
        overall = "OK"

    return {
        "status": overall,
        "service": "Weapons Detection API",
        "version": "2.2.0",
        "timestamp": datetime.now().isoformat(),
        "python_version": "3.13",
        "reddit_configured": AppConfig.reddit.is_configured(),
        "telegram_configured": telegram_configured,
        "ollama_mandatory": mandatory,
        "ollama_available": ollama_available,
        "ollama_text_model_ready": text_model_ok,
        "ollama_vision_model_ready": vision_model_ok,
        "ollama_models": ollama_models,
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
            "/api/reports/osint-pdf",
            "/api/generation/content",
            "/api/generation/batch",
            "/api/generation/big-data",
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
    if risk_score >= 0.75:
        risk_level = "HIGH"
    elif risk_score >= 0.45:
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


@app.post("/api/reports/osint-pdf")
async def export_osint_pdf(request: OsintPdfRequest):
    """Generate a professional OSINT-style PDF report (academic research disclaimer)."""
    data = request.model_dump(exclude_none=True)
    rt = data.get("report_type")
    if rt == "text_analysis":
        if not (data.get("source_text") or "").strip():
            raise HTTPException(status_code=400, detail="source_text is required for text_analysis reports")
    elif rt == "collection_item":
        if not (
            (data.get("content") or "").strip()
            or (data.get("title") or "").strip()
            or data.get("risk_analysis")
        ):
            raise HTTPException(
                status_code=400,
                detail="collection_item reports require content, title, and/or risk_analysis",
            )
    elif rt == "collection_digest":
        sessions = data.get("sessions") or []
        stand = data.get("standalone_posts") or []
        total_listed = sum(len(s.get("posts") or []) for s in sessions) + len(stand)
        js = data.get("job_summary") or {}
        has_job = bool(
            js.get("total_collected")
            or js.get("total_scanned")
            or js.get("high_risk_count") is not None
        )
        if total_listed == 0 and len(sessions) == 0 and not has_job:
            raise HTTPException(
                status_code=400,
                detail="No collection data to export. Collect posts or ensure history/sessions exist.",
            )
    else:
        raise HTTPException(status_code=400, detail="Invalid report_type")

    est = _osint_pdf_payload_char_estimate(data)
    est_limit = 1_800_000 if rt == "collection_digest" else 200_000
    if est > est_limit:
        raise HTTPException(
            status_code=413,
            detail="Payload too large for PDF export; try a smaller scope or export single items.",
        )

    try:
        pdf_bytes = build_osint_pdf(data)
    except ModuleNotFoundError as e:
        if "reportlab" in str(e).lower():
            logger.error("PDF export missing dependency: %s", e)
            raise HTTPException(
                status_code=503,
                detail=(
                    "PDF export requires 'reportlab'. In Docker: ensure the backend container runs "
                    "'pip install -r requirements.txt' on start or rebuild the image. "
                    "Locally: pip install -r backend/requirements.txt"
                ),
            ) from e
        raise
    except Exception as e:
        logger.exception("OSINT PDF generation failed: %s", e)
        raise HTTPException(status_code=500, detail="PDF generation failed") from e

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    if rt == "collection_digest":
        filename = f"OSINT-Digest-{stamp}.pdf"
    else:
        rid = data.get("report_id") or data.get("analysis_id") or data.get("record_id") or data.get("id") or "report"
        safe = _re.sub(r"[^\w\-.]+", "-", str(rid))[:48].strip("-") or "report"
        filename = f"OSINT-Report-{safe}-{stamp}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


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

@app.post("/api/generation/big-data")
async def generate_big_data(request: BigDataGenerationRequest):
    """Generate a large batch of content for big data analysis (2000+ posts)"""
    try:
        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            big_data_results = await loop.run_in_executor(
                executor,
                content_generator.generate_big_data_batch,
                request.total_quantity,
                request.platforms,
                request.content_lengths
            )
        
        return {
            "status": "success",
            "message": f"Generated {big_data_results['statistics']['total_generated']} posts for big data analysis",
            "content": big_data_results['content'],
            "statistics": big_data_results['statistics'],
            "configuration": {
                "total_quantity": request.total_quantity,
                "platforms": request.platforms,
                "content_lengths": request.content_lengths
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Big data generation failed: {str(e)}")

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
            "subreddits_collected": collected_posts.get("subreddits_collected", []),
            "all_posts": collected_posts.get("all_posts", [])
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


# ============================================================================
# SSE STREAMING ENDPOINTS
# ============================================================================

def stream_collect_posts_sync(collector, subreddits: List[str], limit_per_sub: int, time_filter: str, sort_method: str):
    """
    Generator that yields posts one by one as they're collected and analyzed.
    Designed to be wrapped in an async generator for SSE.
    """
    for subreddit in subreddits:
        try:
            # Collect posts from this subreddit
            collected_posts = collector.collect_subreddit_posts(
                subreddit_name=subreddit,
                time_filter=time_filter,
                limit=limit_per_sub,
                sort_method=sort_method
            )
            
            # Yield each post after analysis
            for post in collected_posts:
                try:
                    # Handle both dataclass RedditPost objects and dictionaries
                    if hasattr(post, 'title'):
                        # It's a RedditPost dataclass
                        title = post.title
                        content = post.content if hasattr(post, 'content') else ''
                        post_id = post.id
                        score = post.score if hasattr(post, 'score') else 0
                        num_comments = post.num_comments if hasattr(post, 'num_comments') else 0
                        url = post.url if hasattr(post, 'url') else f"https://reddit.com/r/{subreddit}"
                        created_utc = post.created_utc if hasattr(post, 'created_utc') else 0
                        author_hash = post.author_hash if hasattr(post, 'author_hash') else ''
                        # Image fields
                        image_url = getattr(post, 'image_url', None)
                        thumbnail = getattr(post, 'thumbnail', None)
                        media_type = getattr(post, 'media_type', 'text')
                        gallery_images = getattr(post, 'gallery_images', None)
                        is_video = getattr(post, 'is_video', False)
                        video_url = getattr(post, 'video_url', None)
                    else:
                        # It's a dictionary
                        title = post.get('title', '')
                        content = post.get('selftext', post.get('body', post.get('content', '')))
                        post_id = post.get('id', '')
                        score = post.get('score', 0)
                        num_comments = post.get('num_comments', 0)
                        url = post.get('url', f"https://reddit.com/r/{subreddit}")
                        created_utc = post.get('created_utc', 0)
                        author_hash = str(hash(post.get('author', '')))[:8]
                        # Image fields from dict
                        image_url = post.get('image_url')
                        thumbnail = post.get('thumbnail')
                        media_type = post.get('media_type', 'text')
                        gallery_images = post.get('gallery_images')
                        is_video = post.get('is_video', False)
                        video_url = post.get('video_url')
                    
                    # Analyze the post
                    combined_text = f"{title} {content}"
                    analysis = analyzer.analyze_text(combined_text)
                    
                    # Determine risk level
                    risk_score = analysis.get('risk_score', 0)
                    if risk_score >= 0.75:
                        risk_level = 'HIGH'
                    elif risk_score >= 0.45:
                        risk_level = 'MEDIUM'
                    else:
                        risk_level = 'LOW'
                    
                    # Create post object with analysis
                    post_data = {
                        'id': post_id,
                        'title': title,
                        'content': content[:500] if content else '',
                        'subreddit': subreddit,
                        'author_hash': author_hash,
                        'score': score,
                        'num_comments': num_comments,
                        'url': url,
                        'created_utc': created_utc,
                        'collected_at': datetime.now().isoformat(),
                        'platform': 'reddit',
                        # Image/media fields
                        'image_url': image_url,
                        'thumbnail': thumbnail,
                        'media_type': media_type,
                        'gallery_images': gallery_images,
                        'is_video': is_video,
                        'video_url': video_url,
                        'risk_analysis': {
                            'risk_score': risk_score,
                            'risk_level': risk_level,
                            'confidence': analysis.get('confidence', 0),
                            'flags': analysis.get('flags', []),
                            'detected_keywords': analysis.get('detected_keywords', []),
                            'detected_patterns': analysis.get('detected_patterns', [])
                        }
                    }
                    
                    yield post_data
                    
                except Exception as e:
                    print(f"Error analyzing post: {str(e)}")
                    continue
                    
        except Exception as e:
            print(f"Error collecting from r/{subreddit}: {str(e)}")
            # Yield an error event for this subreddit
            yield {
                'error': True,
                'subreddit': subreddit,
                'message': str(e)
            }
            continue


@app.get("/api/stream/reddit")
async def stream_reddit_collection(
    subreddits: str = _Query(..., description="Comma-separated list of subreddits"),
    limit: int = _Query(default=10, ge=1, le=50, description="Posts per subreddit"),
    time_filter: str = _Query(default="day", description="Time filter"),
    sort_method: str = _Query(default="hot", description="Sort method"),
    analyze_images: bool = _Query(default=True, description="Auto-analyze images for weapons using LLaVA"),
    llm_analysis: bool = _Query(default=True, description="Use LLM to analyze if post is illegal weapon trade")
):
    """
    Stream Reddit posts as they are collected and analyzed using Server-Sent Events.
    Each post is sent as a separate event, allowing real-time UI updates.
    When analyze_images=true, images are automatically analyzed for weapons using LLaVA.
    When llm_analysis=true, LLM reviews each post to determine if it's illegal weapon trade.
    """
    log_print(f"📡 SSE Stream started: subreddits={subreddits}, limit={limit}, images={analyze_images}, llm={llm_analysis}")
    if not SSE_AVAILABLE:
        raise HTTPException(
            status_code=500,
            detail="SSE streaming not available. Install sse-starlette package."
        )
    
    if not AppConfig.reddit.is_configured():
        raise HTTPException(
            status_code=400,
            detail=f"Reddit API not configured. Missing: {', '.join(AppConfig.reddit.get_missing_config())}"
        )
    
    # Parse subreddits
    subreddit_list = [s.strip() for s in subreddits.split(',') if s.strip()]
    if not subreddit_list:
        raise HTTPException(status_code=400, detail="No subreddits specified")

    await _require_ollama_if_mandatory(llm=llm_analysis, vision=analyze_images)
    
    # Use RedditHandler which has enhanced image extraction via from_praw_submission
    from backend_service.handlers.reddit_handler import RedditHandler
    
    handler = RedditHandler(
        client_id=AppConfig.reddit.CLIENT_ID,
        client_secret=AppConfig.reddit.CLIENT_SECRET,
        user_agent=AppConfig.reddit.USER_AGENT
    )
    
    # Collect posts from each subreddit (PRAW sync — off the event loop)
    all_posts = []
    for subreddit in subreddit_list:
        try:
            posts = await asyncio.to_thread(
                handler.collect_subreddit_posts,
                subreddit,
                time_filter,
                limit,
                sort_method,
            )
            all_posts.extend(posts)
            log_print(f"📥 Collected {len(posts)} posts from r/{subreddit}")
        except Exception as e:
            log_print(f"❌ Error collecting from r/{subreddit}: {str(e)}")
    
    log_print(f"📊 Total posts collected: {len(all_posts)}")
    
    # Initialize image analyzer if enabled
    image_analyzer = None
    vision_available = False
    if analyze_images:
        try:
            from backend_service.handlers.image_analysis_handler import ImageAnalysisHandler
            image_analyzer = ImageAnalysisHandler(
                ollama_base=AppConfig.ollama.BASE,
                vision_model=AppConfig.ollama.VISION_MODEL,
                timeout=180  # LLaVA needs 60-120s per image
            )
            # Check if vision model is available (non-blocking check)
        except ImportError:
            log_print("⚠️ Image analysis handler not available")
    
    # Initialize LLM text analyzer if enabled
    # Use AppConfig.ollama.BASE for Docker compatibility
    llm_analyzer = None
    llm_available = False
    if llm_analysis:
        try:
            from backend_service.handlers.llm_text_analyzer import LLMTextAnalyzer
            llm_analyzer = LLMTextAnalyzer(
                ollama_base=AppConfig.ollama.BASE,
                model=AppConfig.ollama.MODEL,
                timeout=180  # LLM can take time for detailed analysis
            )
        except ImportError:
            log_print("⚠️ LLM text analyzer not available")
    
    async def event_generator():
        """Generate SSE events for each collected post"""
        nonlocal vision_available, llm_available
        from dataclasses import asdict
        
        stats = {
            'total_scanned': 0,  # Total posts scanned before filtering
            'total': 0,          # Posts shown (after filtering NONE risk)
            'high_risk': 0,
            'medium_risk': 0,
            'low_risk': 0,
            'none_risk': 0,      # Filtered out (below 25% risk)
            'weapons_detected': 0,
            'images_analyzed': 0,
            'illegal_trade_detected': 0,
            'llm_analyzed': 0,
        }
        
        # Check vision model availability at start
        if image_analyzer:
            vision_available = await image_analyzer.check_model_available()
        
        # Check LLM model availability at start
        if llm_analyzer:
            llm_available = await llm_analyzer.check_model_available()
        
        # Send start event with collection phase
        yield {
            "event": "start",
            "data": _json.dumps({
                "phase": "collecting",
                "subreddits": subreddit_list,
                "limit": limit,
                "total_posts": len(all_posts),
                "analyze_images": analyze_images and vision_available,
                "vision_model": image_analyzer.vision_model if image_analyzer else None,
                "llm_analysis": llm_analysis and llm_available,
                "llm_model": llm_analyzer.model if llm_analyzer else None,
                "timestamp": datetime.now().isoformat()
            })
        }
        
        # Send phase change: COLLECTING complete, starting ANALYZING
        yield {
            "event": "phase",
            "data": _json.dumps({
                "phase": "analyzing",
                "message": f"📊 Collected {len(all_posts)} posts. Now analyzing with AI...",
                "total_to_analyze": len(all_posts),
                "vision_enabled": vision_available,
                "llm_enabled": llm_available
            })
        }
        
        # Send info about vision status
        if analyze_images:
            if vision_available:
                yield {
                    "event": "info",
                    "data": _json.dumps({
                        "message": f"🔍 Vision analysis enabled using {image_analyzer.vision_model}",
                        "type": "vision_enabled"
                    })
                }
            else:
                yield {
                    "event": "info", 
                    "data": _json.dumps({
                        "message": "⚠️ Vision model not available. Run: ollama pull llava:7b",
                        "type": "vision_unavailable"
                    })
                }
        
        # Send info about LLM status
        if llm_analysis:
            if llm_available:
                yield {
                    "event": "info",
                    "data": _json.dumps({
                        "message": f"🧠 LLM analysis enabled using {llm_analyzer.model} - checking for illegal weapon trade",
                        "type": "llm_enabled"
                    })
                }
            else:
                yield {
                    "event": "info", 
                    "data": _json.dumps({
                        "message": "⚠️ LLM model not available. Run: ollama pull llama3.1:8b",
                        "type": "llm_unavailable"
                    })
                }
        
        # =====================================================================
        # PARALLEL ANALYSIS - Process posts concurrently for faster results
        # Note: Ollama GPU can only process 1 image at a time, so we limit to 3
        # to allow text analysis and I/O to overlap with vision processing
        # =====================================================================
        
        # Semaphore to limit concurrent API calls (3 is optimal for Ollama)
        analysis_semaphore = asyncio.Semaphore(3)
        
        async def analyze_single_post(post, post_index: int):
            """Analyze a single post with vision and LLM - runs in parallel"""
            async with analysis_semaphore:
                log_print(f"📝 Analyzing post {post_index}/{len(all_posts)}: '{post.title[:50]}...' from r/{post.subreddit}")
                
                # Analyze the post content (text analysis - fast, CPU-bound)
                combined_text = f"{post.title} {post.content}"
                analysis = analyzer.analyze_text(combined_text)
                
                # Determine risk level from text
                risk_score = analysis.get('risk_score', 0)
                if risk_score >= 0.75:
                    risk_level = 'HIGH'
                elif risk_score >= 0.45:
                    risk_level = 'MEDIUM'
                elif risk_score >= 0.25:
                    risk_level = 'LOW'
                else:
                    risk_level = 'NONE'
                
                # Image weapon detection - ONLY if text analysis shows some risk
                # This saves ~60s per post with no text indicators
                image_analysis = None
                annotated_image = None
                did_image_analysis = False
                weapons_found = False
                
                image_to_analyze = post.image_url or post.thumbnail
                # Only analyze images if text risk >= 25% (LOW) to save time
                should_analyze_image = risk_score >= 0.25 or risk_level in ['LOW', 'MEDIUM', 'HIGH']
                if vision_available and image_analyzer and image_to_analyze and not post.is_video and should_analyze_image:
                    try:
                        did_image_analysis = True
                        image_result = await image_analyzer.analyze_image(image_to_analyze)
                        
                        if image_result.contains_weapons:
                            weapons_found = True
                            if image_result.overall_risk == 'HIGH' and risk_level != 'HIGH':
                                risk_level = 'HIGH'
                                risk_score = max(risk_score, image_result.risk_score)
                            
                            image_analysis = {
                                'contains_weapons': True,
                                'weapon_count': image_result.weapon_count,
                                'detections': [d.to_dict() for d in image_result.detections],
                                'overall_risk': image_result.overall_risk,
                                'analysis_notes': image_result.analysis_notes,
                                'processing_time_ms': image_result.processing_time_ms
                            }
                            annotated_image = image_result.annotated_image_base64
                        else:
                            # Only mark as verified safe if analysis actually completed
                            # (not if it timed out or errored)
                            is_verified = getattr(image_result, 'analysis_completed', True)
                            
                            if is_verified:
                                risk_reduction = 0.2
                                risk_score = max(0, risk_score - risk_reduction)
                                
                                if risk_score >= 0.75:
                                    risk_level = 'HIGH'
                                elif risk_score >= 0.45:
                                    risk_level = 'MEDIUM'
                                elif risk_score >= 0.25:
                                    risk_level = 'LOW'
                                else:
                                    risk_level = 'NONE'
                            
                            image_analysis = {
                                'contains_weapons': False,
                                'weapon_count': 0,
                                'image_verified_safe': is_verified,  # Only True if analysis completed
                                'analysis_completed': is_verified,
                                'risk_reduction_applied': risk_reduction if is_verified else 0,
                                'analysis_notes': image_result.analysis_notes,
                                'processing_time_ms': image_result.processing_time_ms
                            }
                    except Exception as img_err:
                        log_print(f"⚠️ Image analysis error for {post.id}: {img_err}")
                        image_analysis = {'error': str(img_err), 'contains_weapons': False, 'analysis_completed': False}
                
                # LLM analysis for illegal weapon trade detection
                llm_result = None
                did_llm_analysis = False
                is_illegal = False
                
                if llm_available and llm_analyzer:
                    try:
                        did_llm_analysis = True
                        llm_response = await llm_analyzer.analyze_post(
                            title=post.title,
                            content=post.content or '',
                            source=post.subreddit
                        )
                        
                        llm_result = llm_response.to_dict()
                        
                        if llm_response.is_potentially_illegal:
                            is_illegal = True
                            if llm_response.risk_assessment == 'CRITICAL':
                                risk_score = 1.0
                                risk_level = 'CRITICAL'
                            elif llm_response.risk_assessment == 'HIGH' and risk_level != 'CRITICAL':
                                risk_score = max(risk_score, 0.85)
                                risk_level = 'HIGH'
                        elif not llm_response.is_weapon_related and risk_score > 0:
                            risk_reduction = 0.3
                            risk_score = max(0, risk_score - risk_reduction)
                            
                            if risk_score >= 0.75:
                                risk_level = 'HIGH'
                            elif risk_score >= 0.45:
                                risk_level = 'MEDIUM'
                            elif risk_score >= 0.25:
                                risk_level = 'LOW'
                            else:
                                risk_level = 'NONE'
                                    
                    except Exception as llm_err:
                        log_print(f"⚠️ LLM analysis error for {post.id}: {llm_err}")
                        llm_result = {'error': str(llm_err), 'is_potentially_illegal': False}
                
                # Build post data
                post_data = {
                    'id': post.id,
                    'title': post.title,
                    'content': post.content[:500] if post.content else '',
                    'subreddit': post.subreddit,
                    'author_hash': post.author_hash,
                    'score': post.score,
                    'num_comments': post.num_comments,
                    'url': post.url,
                    'created_utc': post.created_at,
                    'collected_at': post.collected_at,
                    'platform': 'reddit',
                    'image_url': post.image_url,
                    'thumbnail': post.thumbnail,
                    'media_type': post.media_type,
                    'gallery_images': post.gallery_images,
                    'is_video': post.is_video,
                    'video_url': post.video_url,
                    'image_analysis': image_analysis,
                    'annotated_image': annotated_image,
                    'llm_analysis': llm_result,
                    'risk_analysis': {
                        'risk_score': risk_score,
                        'risk_level': risk_level,
                        'confidence': analysis.get('confidence', 0),
                        'flags': analysis.get('flags', []),
                        'detected_keywords': analysis.get('detected_keywords', []),
                        'detected_patterns': analysis.get('detected_patterns', [])
                    }
                }
                
                return {
                    'post_data': post_data,
                    'risk_level': risk_level,
                    'did_image_analysis': did_image_analysis,
                    'weapons_found': weapons_found,
                    'did_llm_analysis': did_llm_analysis,
                    'is_illegal': is_illegal
                }
        
        try:
            # Create analysis tasks for all posts
            tasks = [
                asyncio.create_task(analyze_single_post(post, idx + 1))
                for idx, post in enumerate(all_posts)
            ]
            
            # Process results as they complete (faster posts come first)
            for completed_task in asyncio.as_completed(tasks):
                try:
                    result = await completed_task
                    
                    # Update stats
                    stats['total_scanned'] += 1
                    risk_level = result['risk_level']
                    
                    if risk_level == 'HIGH' or risk_level == 'CRITICAL':
                        stats['high_risk'] += 1
                    elif risk_level == 'MEDIUM':
                        stats['medium_risk'] += 1
                    elif risk_level == 'LOW':
                        stats['low_risk'] += 1
                    else:
                        stats['none_risk'] += 1
                    
                    if result['did_image_analysis']:
                        stats['images_analyzed'] += 1
                    if result['weapons_found']:
                        stats['weapons_detected'] += 1
                    if result['did_llm_analysis']:
                        stats['llm_analyzed'] += 1
                    if result['is_illegal']:
                        stats['illegal_trade_detected'] += 1
                    
                    # Skip posts with NONE risk (below 25%)
                    if risk_level == 'NONE':
                        continue
                    
                    stats['total'] += 1
                    
                    # Send post event
                    yield {
                        "event": "post",
                        "data": _json.dumps(result['post_data'])
                    }
                    
                except Exception as task_err:
                    log_print(f"⚠️ Task error: {task_err}")
            
        except Exception as e:
            log_print(f"❌ Collection error: {e}")
            yield {
                "event": "error",
                "data": _json.dumps({"message": str(e), "fatal": True})
            }
        
        # Log completion summary
        log_print(f"✅ Collection complete: {stats['total_scanned']} scanned, {stats['high_risk']} HIGH, {stats['medium_risk']} MEDIUM, {stats['low_risk']} LOW, {stats['none_risk']} filtered")
        
        # Send completion event
        yield {
            "event": "complete",
            "data": _json.dumps({
                "total_scanned": stats['total_scanned'],  # Total posts scanned
                "total_collected": stats['total'],         # Posts with risk >= 25%
                "high_risk_count": stats['high_risk'],
                "medium_risk_count": stats['medium_risk'],
                "low_risk_count": stats['low_risk'],
                "filtered_out": stats['none_risk'],        # Posts below 25% risk, not shown
                "images_analyzed": stats['images_analyzed'],
                "weapons_detected": stats['weapons_detected'],
                "llm_analyzed": stats['llm_analyzed'],
                "illegal_trade_detected": stats['illegal_trade_detected'],
                "vision_enabled": vision_available,
                "llm_enabled": llm_available,
                "subreddits_collected": subreddit_list,
                "timestamp": datetime.now().isoformat()
            })
        }
    
    return EventSourceResponse(event_generator())


@app.get("/api/stream/telegram")
async def stream_telegram_collection(
    channels: str = _Query(..., description="Comma-separated list of channels/groups"),
    limit: int = _Query(default=50, ge=1, le=200, description="Messages per channel"),
    analyze_images: bool = _Query(default=True, description="Analyze photos with LLaVA when applicable"),
    llm_analysis: bool = _Query(default=True, description="Use LLM for illegal trade analysis"),
):
    """
    Stream Telegram messages (collect then analyze) with the same SSE shape as Reddit.
    Requires TELEGRAM_API_ID, TELEGRAM_API_HASH, and an authorized session file.
    """
    if not SSE_AVAILABLE:
        raise HTTPException(
            status_code=500,
            detail="SSE streaming not available. Install sse-starlette package."
        )

    tg = AppConfig.telegram
    if not tg.user_api_credentials_ok():
        raise HTTPException(
            status_code=400,
            detail="Telegram API not configured. Missing: "
            + ", ".join(tg.get_missing_user_api_config())
            + ". Get credentials from https://my.telegram.org",
        )

    from backend_service.telegram_stream_analysis import normalize_telegram_sources

    channel_list = normalize_telegram_sources(channels.split(","))
    if not channel_list:
        raise HTTPException(status_code=400, detail="No channels specified")

    await _require_ollama_if_mandatory(llm=llm_analysis, vision=analyze_images)

    log_print(
        f"📡 Telegram SSE: channels={channel_list}, limit={limit}, images={analyze_images}, llm={llm_analysis}"
    )

    async def event_generator():
        from backend_service.telegram_stream_analysis import (
            analyze_telegram_item,
            collect_telegram_items,
            telegram_session_arg_from_config,
        )

        stats = {
            "total_scanned": 0,
            "total": 0,
            "high_risk": 0,
            "medium_risk": 0,
            "low_risk": 0,
            "none_risk": 0,
            "weapons_detected": 0,
            "images_analyzed": 0,
            "illegal_trade_detected": 0,
            "llm_analyzed": 0,
        }
        vision_available = False
        llm_available = False
        client = None

        try:
            from telethon import TelegramClient
        except ImportError:
            yield {
                "event": "error",
                "data": _json.dumps(
                    {"message": "Telethon not installed. Run: pip install telethon", "fatal": True}
                ),
            }
            return

        try:
            session_arg = telegram_session_arg_from_config(tg)
            client = TelegramClient(session_arg, tg.API_ID, tg.API_HASH)
            await client.connect()
            if not await client.is_user_authorized():
                yield {
                    "event": "error",
                    "data": _json.dumps(
                        {
                            "message": "Not authenticated. Run: python scripts/telegram_auth.py",
                            "configured": False,
                            "fatal": True,
                        }
                    ),
                }
                return

            me = await client.get_me()
            yield {
                "event": "info",
                "data": _json.dumps(
                    {
                        "message": f"Connected as: {me.first_name} (@{me.username})",
                        "configured": True,
                        "method": "user_api",
                    }
                ),
            }

            all_items = await collect_telegram_items(client, channel_list, limit, log_print)
            log_print(f"📊 Telegram collected {len(all_items)} messages (pre-analysis)")

            image_analyzer = None
            if analyze_images:
                try:
                    from backend_service.handlers.image_analysis_handler import ImageAnalysisHandler

                    image_analyzer = ImageAnalysisHandler(
                        ollama_base=AppConfig.ollama.BASE,
                        vision_model=AppConfig.ollama.VISION_MODEL,
                        timeout=180,
                    )
                except ImportError:
                    log_print("⚠️ Image analysis handler not available")

            llm_analyzer = None
            if llm_analysis:
                try:
                    from backend_service.handlers.llm_text_analyzer import LLMTextAnalyzer

                    llm_analyzer = LLMTextAnalyzer(
                        ollama_base=AppConfig.ollama.BASE,
                        model=AppConfig.ollama.MODEL,
                        timeout=180,
                    )
                except ImportError:
                    log_print("⚠️ LLM text analyzer not available")

            if image_analyzer:
                vision_available = await image_analyzer.check_model_available()
            if llm_analyzer:
                llm_available = await llm_analyzer.check_model_available()

            yield {
                "event": "start",
                "data": _json.dumps(
                    {
                        "phase": "collecting",
                        "channels": channel_list,
                        "subreddits": [],
                        "limit": limit,
                        "total_posts": len(all_items),
                        "analyze_images": analyze_images and vision_available,
                        "vision_model": image_analyzer.vision_model if image_analyzer else None,
                        "llm_analysis": llm_analysis and llm_available,
                        "llm_model": llm_analyzer.model if llm_analyzer else None,
                        "timestamp": datetime.now().isoformat(),
                    }
                ),
            }

            yield {
                "event": "phase",
                "data": _json.dumps(
                    {
                        "phase": "analyzing",
                        "message": f"📊 Collected {len(all_items)} messages. Now analyzing with AI...",
                        "total_to_analyze": len(all_items),
                        "vision_enabled": vision_available,
                        "llm_enabled": llm_available,
                    }
                ),
            }

            if analyze_images:
                if vision_available:
                    yield {
                        "event": "info",
                        "data": _json.dumps(
                            {
                                "message": f"🔍 Vision analysis enabled using {image_analyzer.vision_model}",
                                "type": "vision_enabled",
                            }
                        ),
                    }
                else:
                    yield {
                        "event": "info",
                        "data": _json.dumps(
                            {
                                "message": "⚠️ Vision model not available. Run: ollama pull llava:7b",
                                "type": "vision_unavailable",
                            }
                        ),
                    }

            if llm_analysis:
                if llm_available:
                    yield {
                        "event": "info",
                        "data": _json.dumps(
                            {
                                "message": f"🧠 LLM analysis enabled using {llm_analyzer.model}",
                                "type": "llm_enabled",
                            }
                        ),
                    }
                else:
                    yield {
                        "event": "info",
                        "data": _json.dumps(
                            {
                                "message": "⚠️ LLM model not available. Run: ollama pull llama3.1:8b",
                                "type": "llm_unavailable",
                            }
                        ),
                    }

            analysis_semaphore = asyncio.Semaphore(3)

            async def analyze_one(item: Dict[str, Any], idx: int):
                async with analysis_semaphore:
                    return await analyze_telegram_item(
                        analyzer=analyzer,
                        item=item,
                        client=client,
                        image_analyzer=image_analyzer,
                        llm_analyzer=llm_analyzer,
                        vision_available=vision_available,
                        llm_available=llm_available,
                        analyze_images=analyze_images,
                        llm_analysis=llm_analysis,
                        idx=idx,
                        total=len(all_items),
                        log_print=log_print,
                    )

            tasks = [
                asyncio.create_task(analyze_one(item, i + 1)) for i, item in enumerate(all_items)
            ]

            for completed_task in asyncio.as_completed(tasks):
                try:
                    result = await completed_task
                    stats["total_scanned"] += 1
                    risk_level = result["risk_level"]
                    if risk_level in ("HIGH", "CRITICAL"):
                        stats["high_risk"] += 1
                    elif risk_level == "MEDIUM":
                        stats["medium_risk"] += 1
                    elif risk_level == "LOW":
                        stats["low_risk"] += 1
                    else:
                        stats["none_risk"] += 1

                    if result["did_image_analysis"]:
                        stats["images_analyzed"] += 1
                    if result["weapons_found"]:
                        stats["weapons_detected"] += 1
                    if result["did_llm_analysis"]:
                        stats["llm_analyzed"] += 1
                    if result["is_illegal"]:
                        stats["illegal_trade_detected"] += 1

                    if risk_level == "NONE":
                        continue

                    stats["total"] += 1
                    yield {
                        "event": "post",
                        "data": _json.dumps(result["post_data"]),
                    }
                except Exception as task_err:
                    log_print(f"⚠️ Telegram task error: {task_err}")

        except Exception as e:
            log_print(f"❌ Telegram collection error: {e}")
            yield {
                "event": "error",
                "data": _json.dumps({"message": str(e), "fatal": True}),
            }
        finally:
            if client:
                await client.disconnect()

        log_print(
            f"✅ Telegram complete: {stats['total_scanned']} scanned, {stats['high_risk']} HIGH, "
            f"{stats['medium_risk']} MEDIUM, {stats['low_risk']} LOW, {stats['none_risk']} filtered"
        )
        yield {
            "event": "complete",
            "data": _json.dumps(
                {
                    "total_scanned": stats["total_scanned"],
                    "total_collected": stats["total"],
                    "high_risk_count": stats["high_risk"],
                    "medium_risk_count": stats["medium_risk"],
                    "low_risk_count": stats["low_risk"],
                    "filtered_out": stats["none_risk"],
                    "images_analyzed": stats["images_analyzed"],
                    "weapons_detected": stats["weapons_detected"],
                    "llm_analyzed": stats["llm_analyzed"],
                    "illegal_trade_detected": stats["illegal_trade_detected"],
                    "vision_enabled": vision_available,
                    "llm_enabled": llm_available,
                    "channels_collected": channel_list,
                    "subreddits_collected": channel_list,
                    "timestamp": datetime.now().isoformat(),
                }
            ),
        }

    return EventSourceResponse(event_generator())


@app.get("/api/telegram/config-status")
async def telegram_config_status():
    """Check Telegram API configuration status (user API + session + optional bot)."""
    tg = AppConfig.telegram
    missing_user = tg.get_missing_user_api_config()
    resolved = tg.resolved_session_file()
    session_path = str(resolved) if resolved else str(tg.session_path())
    session_exists = tg.has_session_file()

    result: Dict[str, Any] = {
        "is_configured": tg.is_configured(),
        "user_api_credentials_ok": tg.user_api_credentials_ok(),
        "missing_user_api_config": missing_user,
        "session_name": tg.SESSION_NAME,
        "session_file_path": session_path,
        "session_paths_checked": [str(p) for p in tg.session_file_candidates()],
        "session_file_exists": session_exists,
        "user_api_ready_for_collection": tg.user_api_credentials_ok() and session_exists,
        "bot_token_set": bool(tg.BOT_TOKEN),
        "method": (
            "bot_api"
            if tg.BOT_TOKEN and not tg.user_api_credentials_ok()
            else ("user_api" if tg.user_api_credentials_ok() else None)
        ),
    }

    if tg.BOT_TOKEN:
        try:
            from backend_service.handlers.telegram_bot_handler import TelegramBotHandler
            handler = TelegramBotHandler(bot_token=tg.BOT_TOKEN)
            verification = handler.verify_token()
            result["bot_verified"] = verification.get('ok', False)
            result["bot_username"] = verification.get('bot_username')
            result["bot_name"] = verification.get('bot_name')
            if not verification.get('ok'):
                result["bot_error"] = verification.get('error')
        except Exception as e:
            result["bot_verified"] = False
            result["bot_error"] = str(e)

    return result


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

_LLM_PROMPT = """You are a senior OSINT analyst validating suspected illegal weapons-trade text for an academic monitoring stack.
You are precise, evidence-bound, and skeptical of sensationalism; you return machine-readable JSON only.

Return STRICT JSON exactly with this schema (no prose, no backticks):
{{
  "final_label": "HIGH"|"MEDIUM"|"LOW",
  "risk_adjustment": <number between -1.0 and 1.0>,
  "reasons": ["short bullet 1", "short bullet 2"],
  "evidence_spans": ["verbatim span 1", "verbatim span 2"],
  "misclassification_risk": "LOW"|"MEDIUM"|"HIGH"
}}

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
                {
                    "role": "system",
                    "content": "You are a senior OSINT analyst. You only output strict JSON for downstream parsers.",
                },
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
        await _require_ollama_if_mandatory(llm=True, vision=False)
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




# -----------------------------
# Image Analysis Endpoints (Weapon Detection with LLaVA)
# -----------------------------

@app.get("/api/image/status")
async def image_analysis_status():
    """Check if image analysis (LLaVA vision model) is available."""
    try:
        from backend_service.handlers.image_analysis_handler import ImageAnalysisHandler
        handler = ImageAnalysisHandler()
        model_available = await handler.check_model_available()
        
        return {
            "status": "ready" if model_available else "model_not_found",
            "ollama_base": handler.ollama_base,
            "vision_model": handler.vision_model,
            "model_available": model_available,
            "message": "LLaVA vision model is ready for weapon detection" if model_available 
                       else f"Vision model '{handler.vision_model}' not found. Run: ollama pull llava:7b"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": "Image analysis unavailable"
        }


@app.post("/api/image/analyze")
async def analyze_image_for_weapons(request: Dict[str, Any]):
    """
    Analyze a single image for weapons using LLaVA vision model.
    
    Request body:
    {
        "image_url": "https://example.com/image.jpg"
    }
    
    Returns weapon detections with annotated image.
    """
    image_url = request.get("image_url")
    if not image_url:
        raise HTTPException(status_code=400, detail="image_url is required")
    
    try:
        from backend_service.handlers.image_analysis_handler import ImageAnalysisHandler
        handler = ImageAnalysisHandler()
        
        # Check if model is available
        if not await handler.check_model_available():
            raise HTTPException(
                status_code=503,
                detail=f"Vision model '{handler.vision_model}' not available. Run: ollama pull llava:7b"
            )
        
        result = await handler.analyze_image(image_url)
        return result.to_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/api/image/analyze_batch")
async def analyze_images_batch(request: Dict[str, Any]):
    """
    Analyze multiple images for weapons.
    
    Request body:
    {
        "image_urls": ["url1", "url2", ...],
        "max_concurrent": 3  // optional
    }
    
    Returns list of weapon detection results.
    """
    image_urls = request.get("image_urls", [])
    max_concurrent = request.get("max_concurrent", 3)
    
    if not image_urls:
        raise HTTPException(status_code=400, detail="image_urls list is required")
    
    if len(image_urls) > 20:
        raise HTTPException(status_code=400, detail="Maximum 20 images per batch")
    
    try:
        from backend_service.handlers.image_analysis_handler import ImageAnalysisHandler
        handler = ImageAnalysisHandler()
        
        if not await handler.check_model_available():
            raise HTTPException(
                status_code=503,
                detail=f"Vision model '{handler.vision_model}' not available. Run: ollama pull llava:7b"
            )
        
        results = await handler.analyze_batch(image_urls, max_concurrent=max_concurrent)
        
        return {
            "total_analyzed": len(results),
            "weapons_found": sum(1 for r in results if r.contains_weapons),
            "high_risk_images": sum(1 for r in results if r.overall_risk == "HIGH"),
            "results": [r.to_dict() for r in results]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch analysis failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    # Run the server
    # Recommended: Run from backend directory with: uvicorn src.server:app --reload --host 0.0.0.0 --port 9000
    # Or run directly: python src/server.py
    uvicorn.run(
        app,
        host=AppConfig.HOST,
        port=AppConfig.PORT,
        reload=False,
        log_level="info"
    )