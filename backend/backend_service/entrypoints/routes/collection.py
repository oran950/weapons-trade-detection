"""
Collection API Routes
"""
import asyncio
from concurrent.futures import ThreadPoolExecutor
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from datetime import datetime
import os

from ...models.requests import RedditCollectionRequest, TelegramCollectionRequest
from ...models.responses import CollectionResponse, FileListResponse
from ...handlers.reddit_handler import RedditHandler
from ...handlers.analysis_handler import AnalysisHandler
from ...utils.file_manager import FileManager
from ...config import config

router = APIRouter(prefix="/api", tags=["collection"])

file_manager = FileManager(config.DATA_DIR)


def _init_reddit_handler():
    """Initialize Reddit handler with configured credentials"""
    if not config.reddit_configured:
        return None
    
    try:
        return RedditHandler(
            client_id=config.REDDIT_CLIENT_ID,
            client_secret=config.REDDIT_CLIENT_SECRET,
            user_agent=config.REDDIT_USER_AGENT,
            data_dir=config.DATA_DIR
        )
    except Exception:
        return None


@router.post("/reddit/collect", response_model=CollectionResponse)
async def collect_reddit_data(request: RedditCollectionRequest):
    """
    Collect Reddit data for academic research
    """
    if not config.reddit_configured:
        missing = config.get_missing_reddit_config()
        raise HTTPException(
            status_code=500,
            detail=f"Reddit API not configured. Missing: {', '.join(missing)}"
        )
    
    handler = _init_reddit_handler()
    if not handler:
        raise HTTPException(
            status_code=500,
            detail="Failed to initialize Reddit handler"
        )
    
    params = request.parameters
    
    # Default subreddits list
    default_subreddits = [
        "news", "worldnews", "politics", "guns", "firearms", "CCW",
        "ar15", "ak47", "gundeals", "gunpolitics", "Military", "army",
        "navy", "airforce", "marines", "veterans", "EDC", "tacticalgear",
        "preppers", "survival"
    ]
    
    subreddits = default_subreddits if params.include_all_defaults else params.subreddits
    
    # Run collection in thread pool
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
        all_posts = []
        collection_summary = {}
        
        for subreddit in subreddits:
            try:
                if params.keywords:
                    keywords = [k.strip() for k in params.keywords.split(',')]
                    posts = await loop.run_in_executor(
                        executor,
                        lambda s=subreddit: handler.search_posts_by_keywords(
                            s, keywords, params.timeFilter, params.limit_per_subreddit
                        )
                    )
                else:
                    posts = await loop.run_in_executor(
                        executor,
                        lambda s=subreddit: handler.collect_subreddit_posts(
                            s, params.timeFilter, params.limit_per_subreddit, params.sortMethod
                        )
                    )
                
                all_posts.extend(posts)
                collection_summary[subreddit] = len(posts)
            except Exception as e:
                collection_summary[subreddit] = 0
                continue
    
    if not all_posts:
        return CollectionResponse(
            status="warning",
            message="No posts collected",
            total_collected=0,
            high_risk_count=0,
            medium_risk_count=0,
            low_risk_count=0,
            saved_files=[],
            collection_timestamp=datetime.now().isoformat(),
            platform="reddit",
            collection_summary=collection_summary,
            sources_collected=subreddits
        )
    
    # Analyze posts
    analyzed_posts = handler.analyze_posts(all_posts)
    
    # Generate filename
    if params.include_all_defaults:
        filename = f"multi_all_defaults_{params.timeFilter}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    else:
        names = "_".join(params.subreddits[:3])
        if len(params.subreddits) > 3:
            names += f"_and_{len(params.subreddits)-3}_more"
        filename = f"multi_{names}_{params.timeFilter}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Save files
    raw_files = handler.save_posts(all_posts, f"{filename}_raw")
    summary = handler.save_analyzed_posts(analyzed_posts, filename)
    
    saved_files = raw_files + [f"collected_data/analyzed_posts/{filename}_analyzed.json"]
    
    return CollectionResponse(
        status="success",
        message=f"Collected from {len(subreddits)} subreddits",
        total_collected=len(all_posts),
        high_risk_count=summary["analysis_info"]["high_risk_count"],
        medium_risk_count=summary["analysis_info"]["medium_risk_count"],
        low_risk_count=summary["analysis_info"]["low_risk_count"],
        saved_files=saved_files,
        collection_timestamp=datetime.now().isoformat(),
        platform="reddit",
        collection_summary=collection_summary,
        sources_collected=subreddits
    )


@router.post("/telegram/collect")
async def collect_telegram_data(request: TelegramCollectionRequest):
    """
    Collect Telegram data for academic research
    """
    if not config.telegram_configured:
        raise HTTPException(
            status_code=500,
            detail="Telegram API not configured. Set TELEGRAM_API_ID and TELEGRAM_API_HASH in .env"
        )
    
    try:
        from ...handlers.telegram_handler import TelegramHandler
        
        handler = TelegramHandler(
            api_id=config.TELEGRAM_API_ID,
            api_hash=config.TELEGRAM_API_HASH,
            data_dir=config.DATA_DIR
        )
        
        if not await handler.connect():
            raise HTTPException(status_code=500, detail="Failed to connect to Telegram")
        
        params = request.parameters
        all_messages = []
        collection_summary = {}
        
        # Collect from channels
        for channel in params.channels:
            messages = await handler.collect_channel_messages(channel, params.limit_per_source)
            all_messages.extend(messages)
            collection_summary[channel] = len(messages)
        
        # Collect from groups
        for group_id in params.groups:
            messages = await handler.collect_group_messages(group_id, params.limit_per_source)
            all_messages.extend(messages)
            collection_summary[str(group_id)] = len(messages)
        
        # Search by keywords
        if params.search_globally and params.keywords:
            for keyword in params.keywords:
                messages = await handler.search_messages(keyword, params.limit_per_source)
                all_messages.extend(messages)
        
        await handler.disconnect()
        
        if not all_messages:
            return {
                "status": "warning",
                "message": "No messages collected",
                "total_collected": 0,
                "platform": "telegram"
            }
        
        # Analyze messages
        analyzed = handler.analyze_messages(all_messages)
        
        # Categorize
        high_risk = [m for m in analyzed if m.risk_analysis and m.risk_analysis.get('risk_score', 0) >= 0.7]
        medium_risk = [m for m in analyzed if m.risk_analysis and 0.4 <= m.risk_analysis.get('risk_score', 0) < 0.7]
        low_risk = [m for m in analyzed if m.risk_analysis and m.risk_analysis.get('risk_score', 0) < 0.4]
        
        # Save
        filename = f"telegram_collection_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        saved_files = handler.save_messages(all_messages, filename)
        
        return {
            "status": "success",
            "message": f"Collected {len(all_messages)} messages",
            "total_collected": len(all_messages),
            "high_risk_count": len(high_risk),
            "medium_risk_count": len(medium_risk),
            "low_risk_count": len(low_risk),
            "saved_files": saved_files,
            "collection_timestamp": datetime.now().isoformat(),
            "platform": "telegram",
            "collection_summary": collection_summary
        }
        
    except ImportError:
        raise HTTPException(
            status_code=500,
            detail="Telethon library required. Install with: pip install telethon"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reddit/config-status")
async def reddit_config_status():
    """Check Reddit API configuration status"""
    return {
        "is_configured": config.reddit_configured,
        "missing_config": config.get_missing_reddit_config(),
        "user_agent": config.REDDIT_USER_AGENT or "Not configured",
        "data_directory": config.DATA_DIR
    }


@router.get("/telegram/config-status")
async def telegram_config_status():
    """Check Telegram API configuration status"""
    return {
        "is_configured": config.telegram_configured,
        "missing_config": config.get_missing_telegram_config(),
        "data_directory": config.DATA_DIR
    }


@router.get("/reddit/files", response_model=FileListResponse)
async def list_collected_files():
    """List all collected data files"""
    raw_files = []
    analyzed_files = []
    
    for filename in file_manager.list_files("raw"):
        info = file_manager.get_file_info(filename, "raw")
        if info:
            raw_files.append(info)
    
    for filename in file_manager.list_files("analyzed"):
        info = file_manager.get_file_info(filename, "analyzed")
        if info:
            analyzed_files.append(info)
    
    return FileListResponse(
        raw_files=raw_files,
        analyzed_files=analyzed_files,
        total_files=len(raw_files) + len(analyzed_files)
    )

