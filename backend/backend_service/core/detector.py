"""
Weapons Detector - Main detection orchestrator
Coordinates rule-based analysis and LLM validation
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
import hashlib

from .analyzer import TextAnalyzer
from .scorer import RiskScorer
from ..entities.analysis import AnalysisResult, RiskAssessment
from ..entities.risk import RiskLevel, RiskClassification


class WeaponsDetector:
    """
    Main orchestrator for weapons detection.
    Coordinates rule-based analysis and optional LLM validation.
    """
    
    def __init__(self, use_llm: bool = False, llm_operations=None):
        """
        Initialize the weapons detector
        
        Args:
            use_llm: Whether to use LLM for validation
            llm_operations: LLM operations module (if use_llm is True)
        """
        self.analyzer = TextAnalyzer()
        self.scorer = RiskScorer()
        self.use_llm = use_llm
        self.llm_operations = llm_operations
        
        print(f"WeaponsDetector initialized (LLM: {'enabled' if use_llm else 'disabled'})")
    
    def analyze(
        self, 
        content: str,
        use_llm_override: Optional[bool] = None,
        always_use_llm: bool = False
    ) -> RiskAssessment:
        """
        Analyze content for weapons trade indicators
        
        Args:
            content: Text content to analyze
            use_llm_override: Override the default LLM setting
            always_use_llm: Always use LLM regardless of triage
            
        Returns:
            RiskAssessment with complete analysis
        """
        start_time = datetime.now()
        
        # Generate content hash for deduplication
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:32]
        analysis_id = f"analysis_{int(start_time.timestamp())}"
        
        # Run rule-based analysis
        rule_result = self.analyzer.analyze_text(content)
        
        # Determine if LLM should be used
        use_llm = use_llm_override if use_llm_override is not None else self.use_llm
        should_use_llm = self.scorer.should_use_llm(
            rule_result.risk_score,
            use_llm,
            always_use_llm
        )
        
        final_result = rule_result
        
        # Run LLM validation if appropriate
        if should_use_llm and self.llm_operations:
            try:
                llm_classification = self.llm_operations.classify_risk(
                    content,
                    rule_result
                )
                
                # Update result with LLM data
                final_score, risk_level = self.scorer.score_from_analysis(
                    rule_result, 
                    llm_classification
                )
                
                final_result = AnalysisResult(
                    risk_score=final_score,
                    confidence=rule_result.confidence,
                    flags=rule_result.flags,
                    detected_keywords=rule_result.detected_keywords,
                    detected_patterns=rule_result.detected_patterns,
                    analysis_time=rule_result.analysis_time,
                    source="hybrid",
                    llm_reasons=llm_classification.reasons,
                    llm_evidence_spans=llm_classification.evidence_spans,
                    llm_misclassification_risk=llm_classification.misclassification_risk
                )
            except Exception as e:
                # LLM failure should not break analysis
                final_result = AnalysisResult(
                    risk_score=rule_result.risk_score,
                    confidence=rule_result.confidence,
                    flags=rule_result.flags,
                    detected_keywords=rule_result.detected_keywords,
                    detected_patterns=rule_result.detected_patterns,
                    analysis_time=rule_result.analysis_time,
                    source="rules",
                    llm_error=str(e)
                )
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return RiskAssessment(
            analysis_id=analysis_id,
            content_hash=content_hash,
            result=final_result,
            processing_time_ms=processing_time
        )
    
    def analyze_batch(
        self, 
        contents: List[str],
        use_llm_override: Optional[bool] = None
    ) -> List[RiskAssessment]:
        """
        Analyze multiple pieces of content
        
        Args:
            contents: List of text contents to analyze
            use_llm_override: Override the default LLM setting
            
        Returns:
            List of RiskAssessments
        """
        return [
            self.analyze(content, use_llm_override) 
            for content in contents
        ]
    
    def quick_scan(self, content: str) -> Dict[str, Any]:
        """
        Perform a quick scan without full analysis
        Returns basic risk indicators for triage
        
        Args:
            content: Text to scan
            
        Returns:
            Dictionary with basic risk indicators
        """
        result = self.analyzer.analyze_text(content)
        
        return {
            "has_risk": result.risk_score >= 0.4,
            "risk_level": result.risk_level,
            "risk_score": result.risk_score,
            "indicator_count": len(result.flags)
        }
    
    def is_high_risk(self, content: str) -> bool:
        """Quick check if content is high risk"""
        result = self.analyzer.analyze_text(content)
        return result.risk_score >= 0.7

