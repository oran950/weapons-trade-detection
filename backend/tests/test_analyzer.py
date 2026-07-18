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
            "Sunny skies this afternoon",
        ]
        results = self.analyzer.analyze_batch(texts)
        assert len(results) == 3
        # First should be low risk
        assert results[0].risk_score < 0.4
        # Second should be high risk
        assert results[1].risk_score >= 0.7
        # Third should be low risk
        assert results[2].risk_score < 0.4

    def test_batch_empty_list(self):
        assert self.analyzer.analyze_batch([]) == []

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

    def test_clean_text_normalizes(self):
        cleaned = self.analyzer.clean_text("  Hello, WORLD!!!  ")
        assert cleaned == "hello world"

    def test_explosives_keyword(self):
        result = self.analyzer.analyze_text("Looking for C4 and detonator supplies")
        assert result.risk_score >= 0.7
        assert any("explosives" in k for k in result.detected_keywords)

    def test_illegal_terms_keyword(self):
        result = self.analyzer.analyze_text("Ghost gun available, cash only meetup")
        assert result.risk_score >= 0.7
        assert len(result.flags) > 0

    def test_direct_weapon_model_minimum(self):
        result = self.analyzer.analyze_text("Check out this brand new M16")
        assert result.risk_score >= 0.8

    def test_score_capped_at_one(self):
        text = (
            "Sell guns firearms pistols rifles glock ak47 ar15 ammo "
            "cash only no questions ghost gun black market smuggling"
        )
        result = self.analyzer.analyze_text(text)
        assert result.risk_score <= 1.0

    def test_slang_weapon_terms(self):
        result = self.analyzer.analyze_text("Got a choppa and a strap for sale")
        assert result.risk_score >= 0.7

    def test_caliber_pattern(self):
        result = self.analyzer.analyze_text("Need 5.56 and 9mm rounds ASAP")
        assert result.risk_score >= 0.7
        assert len(result.detected_patterns) > 0 or len(result.detected_keywords) > 0


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

    def test_combine_scores_invalid_adjustment(self):
        combined, level = self.scorer.combine_scores(0.5, "not-a-number")
        assert combined == 0.5
        assert level == "MEDIUM"

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

    def test_always_use_llm_when_enabled(self):
        assert self.scorer.should_use_llm(0.1, llm_enabled=True, always_if_enabled=True)
        assert self.scorer.should_use_llm(0.99, llm_enabled=True, always_if_enabled=True)

    def test_get_risk_level_string(self):
        assert self.scorer.get_risk_level_string(0.1) == "LOW"
        assert self.scorer.get_risk_level_string(0.5) == "MEDIUM"
        assert self.scorer.get_risk_level_string(0.8) == "HIGH"
        assert self.scorer.get_risk_level_string(0.95) == "CRITICAL"

    def test_calculate_confidence_agreement(self):
        assert self.scorer.calculate_confidence(0.8) == 0.8
        boosted = self.scorer.calculate_confidence(0.8, 0.8, agreement=True)
        assert boosted > 0.8
        reduced = self.scorer.calculate_confidence(0.8, 0.8, agreement=False)
        assert reduced < boosted


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

