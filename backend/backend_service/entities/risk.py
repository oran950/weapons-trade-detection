"""
Risk classification entities
"""
from dataclasses import dataclass, asdict, field
from typing import Optional, Dict, Any, List
from enum import Enum


class RiskLevel(str, Enum):
    """Risk level enumeration"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    
    @classmethod
    def from_score(cls, score: float) -> 'RiskLevel':
        """Get risk level from numeric score"""
        if score >= 0.9:
            return cls.CRITICAL
        elif score >= 0.7:
            return cls.HIGH
        elif score >= 0.4:
            return cls.MEDIUM
        return cls.LOW


@dataclass
class RiskClassification:
    """LLM-provided risk classification"""
    final_label: str  # HIGH, MEDIUM, LOW
    risk_adjustment: float  # -1.0 to 1.0
    reasons: List[str]
    evidence_spans: List[str]
    misclassification_risk: str  # LOW, MEDIUM, HIGH
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_llm_response(cls, response: Dict[str, Any]) -> 'RiskClassification':
        """Create from LLM response dictionary"""
        return cls(
            final_label=response.get('final_label', 'MEDIUM'),
            risk_adjustment=float(response.get('risk_adjustment', 0.0)),
            reasons=response.get('reasons', []),
            evidence_spans=response.get('evidence_spans', []),
            misclassification_risk=response.get('misclassification_risk', 'MEDIUM')
        )


@dataclass
class EvasionPatterns:
    """Detected evasion patterns in content"""
    patterns_detected: List[str]
    confidence: float
    techniques: List[str]  # 'codewords', 'misspelling', 'leet_speak', etc.
    original_terms: Dict[str, str]  # Maps detected pattern to likely original term
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @property
    def has_evasion(self) -> bool:
        return len(self.patterns_detected) > 0


@dataclass
class ConversationAnalysis:
    """Analysis of multi-message conversations"""
    conversation_id: str
    message_count: int
    participants_count: int
    deal_progression: str  # 'initial_contact', 'negotiation', 'agreement', 'completion'
    buyer_indicators: List[str]
    seller_indicators: List[str]
    negotiation_patterns: List[str]
    risk_score: float
    timeline_start: str
    timeline_end: str
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

