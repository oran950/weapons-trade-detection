"""
Detection models and data structures
"""
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ContentType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    DOCUMENT = "document"
    URL = "url"

class DetectionRequest(BaseModel):
    content: str
    content_type: ContentType
    source: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class DetectionResult(BaseModel):
    analysis_id: str
    risk_score: float
    confidence: float
    risk_level: RiskLevel
    flags: List[str]
    summary: str
    detected_patterns: List[str]
    timestamp: datetime
    processing_time: float

class AnalysisStatus(BaseModel):
    analysis_id: str
    status: str  # pending, processing, completed, failed
    progress: float
    estimated_completion: Optional[datetime]
    error_message: Optional[str]