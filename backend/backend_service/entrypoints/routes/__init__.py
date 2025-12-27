"""
API Routes Module
"""

from .detection import router as detection_router
from .collection import router as collection_router
from .generation import router as generation_router
from .llm import router as llm_router

__all__ = [
    "detection_router",
    "collection_router", 
    "generation_router",
    "llm_router"
]

