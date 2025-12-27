"""
FastAPI Application Entry Point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

from ..config import config
from ..globals import state
from .routes import detection_router, collection_router, generation_router, llm_router


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application
    
    Returns:
        Configured FastAPI app
    """
    app = FastAPI(
        title="Weapons Detection API",
        description="Academic research system for detecting illegal weapons trade patterns",
        version="2.2.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://localhost:3001"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(detection_router)
    app.include_router(collection_router)
    app.include_router(generation_router)
    app.include_router(llm_router)
    
    # Root endpoint
    @app.get("/")
    async def root():
        return {
            "message": "Weapons Detection API v2.2 is running!",
            "docs": "/docs",
            "health": "/health"
        }
    
    # Health check
    @app.get("/health")
    async def health_check():
        return {
            "status": "OK",
            "service": "Weapons Detection API",
            "version": "2.2.0",
            "timestamp": datetime.now().isoformat(),
            "reddit_configured": config.reddit_configured,
            "telegram_configured": config.telegram_configured,
            "llm_configured": config.llm_configured
        }
    
    # API info
    @app.get("/api")
    async def api_info():
        return {
            "message": "Weapons Detection API endpoints",
            "endpoints": {
                "detection": [
                    "/api/detection/analyze",
                    "/api/detection/analyze_llm",
                    "/api/detection/batch",
                    "/api/detection/keywords"
                ],
                "collection": [
                    "/api/reddit/collect",
                    "/api/reddit/config-status",
                    "/api/reddit/files",
                    "/api/telegram/collect",
                    "/api/telegram/config-status"
                ],
                "generation": [
                    "/api/generation/content",
                    "/api/generation/batch",
                    "/api/generation/big-data",
                    "/api/generation/templates"
                ],
                "llm": [
                    "/api/llm/status",
                    "/api/llm/models",
                    "/api/llm/classify",
                    "/api/llm/extract-entities",
                    "/api/llm/explain"
                ]
            }
        }
    
    # Stats endpoint
    @app.get("/stats")
    async def get_stats():
        return state.get_stats()
    
    # Startup event
    @app.on_event("startup")
    async def startup_event():
        state.mark_started()
        print("=" * 50)
        print("Weapons Detection API v2.2.0 Started")
        print("=" * 50)
        print(f"Reddit configured: {config.reddit_configured}")
        print(f"Telegram configured: {config.telegram_configured}")
        print(f"LLM configured: {config.llm_configured}")
        print("=" * 50)
    
    return app


# Create the app instance for uvicorn
app = create_app()

