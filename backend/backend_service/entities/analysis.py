"""
Analysis result entities
"""
from dataclasses import dataclass, asdict, field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


@dataclass
class AnalysisResult:
    """Result of text analysis"""
    risk_score: float
    confidence: float
    flags: List[str]
    detected_keywords: List[str]
    detected_patterns: List[str]
    analysis_time: str
    source: str = "rules"  # 'rules', 'llm', 'hybrid'
    
    # LLM-specific fields
    llm_reasons: Optional[List[str]] = None
    llm_evidence_spans: Optional[List[str]] = None
    llm_misclassification_risk: Optional[str] = None
    llm_error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @property
    def risk_level(self) -> str:
        """Get risk level string based on score"""
        if self.risk_score >= 0.7:
            return "HIGH"
        elif self.risk_score >= 0.4:
            return "MEDIUM"
        return "LOW"


@dataclass
class RiskAssessment:
    """Complete risk assessment for a piece of content"""
    analysis_id: str
    content_hash: str  # Hash of analyzed content for deduplication
    result: AnalysisResult
    post_id: Optional[str] = None
    platform: Optional[str] = None
    processed_at: str = field(default_factory=lambda: datetime.now().isoformat())
    processing_time_ms: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['result'] = self.result.to_dict()
        return data
    
    @property
    def is_high_risk(self) -> bool:
        return self.result.risk_score >= 0.7
    
    @property
    def is_medium_risk(self) -> bool:
        return 0.4 <= self.result.risk_score < 0.7
    
    @property
    def is_low_risk(self) -> bool:
        return self.result.risk_score < 0.4


@dataclass
class ExtractedEntities:
    """Entities extracted from content via LLM"""
    weapon_types: List[str] = field(default_factory=list)
    weapon_models: List[str] = field(default_factory=list)
    locations: List[str] = field(default_factory=list)
    contact_methods: List[str] = field(default_factory=list)
    prices: List[str] = field(default_factory=list)
    quantities: List[str] = field(default_factory=list)
    time_references: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @property
    def has_transaction_indicators(self) -> bool:
        """Check if there are indicators of a transaction"""
        return bool(self.prices or self.contact_methods or self.locations)

