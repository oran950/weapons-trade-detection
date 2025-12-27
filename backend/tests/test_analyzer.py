"""
Tests for the text analyzer
"""
import pytest
import sys
import os

# Add backend_service to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend_service.core.analyzer import TextAnalyzer


class TestTextAnalyzer:
    """Tests for TextAnalyzer class"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.analyzer = TextAnalyzer()
    
    def test_low_risk_content(self):
        """Test that benign content gets low risk score"""
        text = "Had a great day at the park with my family"
        result = self.analyzer.analyze_text(text)
        assert result.risk_score < 0.4
        assert result.risk_level == "LOW"
    
    def test_high_risk_weapon_keyword(self):
        """Test that weapon keywords trigger high risk"""
        text = "Looking to buy a gun for protection"
        result = self.analyzer.analyze_text(text)
        assert result.risk_score >= 0.7
        assert result.risk_level == "HIGH"
        assert len(result.flags) > 0
    
    def test_high_risk_pattern(self):
        """Test that transaction patterns trigger high risk"""
        text = "WTS: AR-15 rifle, cash only, no questions asked"
        result = self.analyzer.analyze_text(text)
        assert result.risk_score >= 0.7
        assert "ar15" in str(result.detected_keywords).lower() or "cash only" in str(result.flags).lower()
    
    def test_multiple_keywords(self):
        """Test detection of multiple keywords"""
        text = "Need to buy ammunition and a pistol for self defense"
        result = self.analyzer.analyze_text(text)
        assert result.risk_score >= 0.7
        assert len(result.detected_keywords) > 0
    
    def test_batch_analysis(self):
        """Test batch analysis functionality"""
        texts = [
            "Hello world",
            "Looking to sell my glock",
            "Weather is nice today"
        ]
        results = self.analyzer.analyze_batch(texts)
        assert len(results) == 3
        # First should be low risk
        assert results[0].risk_score < 0.4
        # Second should be high risk
        assert results[1].risk_score >= 0.7
        # Third should be low risk
        assert results[2].risk_score < 0.4
    
    def test_empty_text(self):
        """Test handling of empty text"""
        result = self.analyzer.analyze_text("")
        assert result.risk_score == 0.0
    
    def test_confidence_score(self):
        """Test that confidence is always returned"""
        result = self.analyzer.analyze_text("Some random text")
        assert 0.0 <= result.confidence <= 1.0
    
    def test_analysis_time_recorded(self):
        """Test that analysis time is recorded"""
        result = self.analyzer.analyze_text("Test text")
        assert result.analysis_time is not None
        assert len(result.analysis_time) > 0


class TestRiskScorer:
    """Tests for RiskScorer class"""
    
    def setup_method(self):
        from backend_service.core.scorer import RiskScorer
        self.scorer = RiskScorer()
    
    def test_combine_scores_positive(self):
        """Test score combination with positive adjustment"""
        combined, level = self.scorer.combine_scores(0.5, 0.5)
        assert combined > 0.5
        assert combined <= 0.6  # Max shift is 0.2
    
    def test_combine_scores_negative(self):
        """Test score combination with negative adjustment"""
        combined, level = self.scorer.combine_scores(0.5, -0.5)
        assert combined < 0.5
        assert combined >= 0.4  # Max shift is 0.2
    
    def test_triage_band(self):
        """Test LLM triage decision"""
        # Below triage band
        assert not self.scorer.should_use_llm(0.2, llm_enabled=True)
        # In triage band
        assert self.scorer.should_use_llm(0.5, llm_enabled=True)
        # Above triage band
        assert not self.scorer.should_use_llm(0.9, llm_enabled=True)
        # Disabled
        assert not self.scorer.should_use_llm(0.5, llm_enabled=False)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

