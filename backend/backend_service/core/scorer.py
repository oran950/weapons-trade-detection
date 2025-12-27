"""
Risk Scorer - Combines rule-based and LLM scores
"""
from typing import Optional, Tuple, Dict, Any
from ..entities.analysis import AnalysisResult
from ..entities.risk import RiskLevel, RiskClassification


class RiskScorer:
    """
    Combines scores from different analysis sources (rules, LLM)
    and produces final risk assessments.
    """
    
    def __init__(self, max_llm_shift: float = 0.2):
        """
        Initialize the risk scorer
        
        Args:
            max_llm_shift: Maximum amount LLM can shift the rule-based score
        """
        self.max_llm_shift = max_llm_shift
    
    def combine_scores(
        self, 
        rule_score: float, 
        llm_adjustment: float
    ) -> Tuple[float, str]:
        """
        Combine rule-based score with LLM adjustment
        
        Args:
            rule_score: Score from rule-based analysis (0-1)
            llm_adjustment: Adjustment from LLM (-1 to 1)
            
        Returns:
            Tuple of (combined_score, risk_level_string)
        """
        try:
            adj = float(llm_adjustment)
        except (TypeError, ValueError):
            adj = 0.0
        
        # Clamp adjustment
        adj = max(-1.0, min(1.0, adj))
        
        # Apply adjustment with max shift limit
        combined = max(0.0, min(1.0, float(rule_score) + adj * self.max_llm_shift))
        
        return combined, RiskLevel.from_score(combined).value
    
    def score_from_analysis(
        self, 
        analysis: AnalysisResult, 
        llm_result: Optional[RiskClassification] = None
    ) -> Tuple[float, RiskLevel]:
        """
        Calculate final score from analysis result and optional LLM result
        
        Args:
            analysis: Rule-based analysis result
            llm_result: Optional LLM classification result
            
        Returns:
            Tuple of (final_score, RiskLevel)
        """
        rule_score = analysis.risk_score
        
        if llm_result:
            final_score, _ = self.combine_scores(
                rule_score, 
                llm_result.risk_adjustment
            )
        else:
            final_score = rule_score
        
        return final_score, RiskLevel.from_score(final_score)
    
    def should_use_llm(
        self, 
        rule_score: float, 
        llm_enabled: bool = False,
        always_if_enabled: bool = False
    ) -> bool:
        """
        Determine whether to invoke LLM based on triage logic
        
        Args:
            rule_score: Score from rule-based analysis
            llm_enabled: Whether LLM is enabled by user
            always_if_enabled: Whether to always use LLM when enabled
            
        Returns:
            True if LLM should be invoked
        """
        if not llm_enabled:
            return False
        
        if always_if_enabled:
            return True
        
        # Triage band: use LLM for uncertain scores
        return 0.35 <= rule_score <= 0.75
    
    def get_risk_level_string(self, score: float) -> str:
        """Get risk level string from score"""
        return RiskLevel.from_score(score).value
    
    def calculate_confidence(
        self,
        rule_confidence: float,
        llm_confidence: Optional[float] = None,
        agreement: bool = True
    ) -> float:
        """
        Calculate combined confidence score
        
        Args:
            rule_confidence: Confidence from rule-based analysis
            llm_confidence: Confidence from LLM (if used)
            agreement: Whether rule and LLM results agree
            
        Returns:
            Combined confidence score
        """
        if llm_confidence is None:
            return rule_confidence
        
        # If they agree, boost confidence
        if agreement:
            return min(1.0, (rule_confidence + llm_confidence) / 2 + 0.1)
        else:
            # If they disagree, reduce confidence
            return max(0.5, (rule_confidence + llm_confidence) / 2 - 0.1)

