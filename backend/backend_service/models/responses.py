"""
Response models for API endpoints
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    service: str
    version: str
    timestamp: str
    reddit_configured: bool
    telegram_configured: bool = False
    llm_available: bool = False


class AnalysisResponse(BaseModel):
    """Response model for text analysis"""
    analysis_id: str
    status: str
    risk_score: float
    risk_level: str
    confidence: float
    flags: List[str]
    detected_keywords: List[str]
    detected_patterns: List[str]
    summary: str
    timestamp: str
    source: str = "rules"
    
    # LLM-specific fields (optional)
    llm_reasons: Optional[List[str]] = None
    llm_evidence_spans: Optional[List[str]] = None
    llm_misclassification_risk: Optional[str] = None
    llm_error: Optional[str] = None


class CollectionResponse(BaseModel):
    """Response model for data collection"""
    status: str
    message: str
    total_collected: int
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    saved_files: List[str]
    collection_timestamp: str
    platform: str
    collection_summary: Optional[Dict[str, int]] = None
    sources_collected: Optional[List[str]] = None


class GenerationResponse(BaseModel):
    """Response model for content generation"""
    status: str
    generated_count: int
    content: List[Dict[str, Any]]
    parameters: Dict[str, Any]
    timestamp: str


class BatchGenerationResponse(BaseModel):
    """Response model for batch generation"""
    status: str
    batch_results: Dict[str, List[Dict[str, Any]]]
    configuration: Dict[str, Any]
    timestamp: str


class BigDataGenerationResponse(BaseModel):
    """Response model for big data generation"""
    status: str
    message: str
    content: List[Dict[str, Any]]
    statistics: Dict[str, Any]
    configuration: Dict[str, Any]
    timestamp: str


class LLMStatusResponse(BaseModel):
    """Response model for LLM status check"""
    provider: str
    ollama_base: str
    model: str
    requests_installed: bool
    ollama_reachable: bool
    ok: bool
    problems: List[str]


class FileListResponse(BaseModel):
    """Response model for file listing"""
    raw_files: List[Dict[str, Any]]
    analyzed_files: List[Dict[str, Any]]
    total_files: int


class ReportResponse(BaseModel):
    """Response model for report generation"""
    status: str
    report_type: str
    summary: Dict[str, Any]
    high_risk_count: int
    total_analyzed: int
    generated_at: str
    report_file: Optional[str] = None


class EntityExtractionResponse(BaseModel):
    """Response model for entity extraction"""
    weapon_types: List[str]
    weapon_models: List[str]
    locations: List[str]
    contact_methods: List[str]
    prices: List[str]
    quantities: List[str]
    time_references: List[str]
    has_transaction_indicators: bool

