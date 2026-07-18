"""
Tests for entity models
"""
import pytest
import sys
import os

# Add backend_service to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend_service.entities.post import Post, RedditPost, TelegramMessage
from backend_service.entities.analysis import (
    AnalysisResult,
    RiskAssessment,
    ExtractedEntities,
)
from backend_service.entities.risk import (
    RiskLevel,
    RiskClassification,
    EvasionPatterns,
    ConversationAnalysis,
)


class TestRedditPost:
    """Tests for RedditPost entity"""
    
    def test_create_reddit_post(self):
        """Test creating a Reddit post"""
        post = RedditPost(
            id="abc123",
            title="Test Title",
            content="Test content",
            subreddit="test",
            author_hash="hash123",
            score=10,
            num_comments=5,
            created_at=1234567890.0,
            url="https://reddit.com/r/test/abc123",
            collected_at="2024-01-01T00:00:00",
            platform="reddit"
        )
        
        assert post.id == "abc123"
        assert post.platform == "reddit"
        assert post.subreddit == "test"
    
    def test_reddit_post_to_dict(self):
        """Test converting Reddit post to dictionary"""
        post = RedditPost(
            id="abc123",
            title="Test",
            content="Content",
            subreddit="test",
            author_hash="hash",
            score=0,
            num_comments=0,
            created_at=0.0,
            url="",
            collected_at="",
            platform="reddit"
        )
        
        data = post.to_dict()
        assert isinstance(data, dict)
        assert data["id"] == "abc123"
        assert data["platform"] == "reddit"


class TestTelegramMessage:
    """Tests for TelegramMessage entity"""
    
    def test_create_telegram_message(self):
        """Test creating a Telegram message"""
        msg = TelegramMessage(
            id="123",
            content="Test message",
            author_hash="hash456",
            chat_id=12345,
            chat_title="Test Channel",
            chat_type="channel",
            created_at=1234567890.0,
            url="https://t.me/test/123",
            collected_at="2024-01-01T00:00:00",
            platform="telegram"
        )
        
        assert msg.id == "123"
        assert msg.platform == "telegram"
        assert msg.chat_type == "channel"


class TestAnalysisResult:
    """Tests for AnalysisResult entity"""
    
    def test_create_analysis_result(self):
        """Test creating an analysis result"""
        result = AnalysisResult(
            risk_score=0.75,
            confidence=0.9,
            flags=["HIGH RISK: Weapon detected"],
            detected_keywords=["firearms: gun"],
            detected_patterns=["buy gun"],
            analysis_time="2024-01-01T00:00:00",
            source="rules"
        )
        
        assert result.risk_score == 0.75
        assert result.risk_level == "HIGH"
        assert len(result.flags) == 1
    
    def test_risk_level_calculation(self):
        """Test risk level calculation from score"""
        low = AnalysisResult(risk_score=0.3, confidence=0.9, flags=[], 
                             detected_keywords=[], detected_patterns=[],
                             analysis_time="", source="rules")
        assert low.risk_level == "LOW"
        
        medium = AnalysisResult(risk_score=0.5, confidence=0.9, flags=[],
                                detected_keywords=[], detected_patterns=[],
                                analysis_time="", source="rules")
        assert medium.risk_level == "MEDIUM"
        
        high = AnalysisResult(risk_score=0.8, confidence=0.9, flags=[],
                              detected_keywords=[], detected_patterns=[],
                              analysis_time="", source="rules")
        assert high.risk_level == "HIGH"


class TestRiskLevel:
    """Tests for RiskLevel enum"""
    
    def test_risk_level_from_score(self):
        """Test RiskLevel.from_score()"""
        assert RiskLevel.from_score(0.1) == RiskLevel.LOW
        assert RiskLevel.from_score(0.5) == RiskLevel.MEDIUM
        assert RiskLevel.from_score(0.75) == RiskLevel.HIGH
        assert RiskLevel.from_score(0.95) == RiskLevel.CRITICAL


class TestRiskClassification:
    """Tests for RiskClassification"""
    
    def test_from_llm_response(self):
        """Test creating classification from LLM response"""
        response = {
            "final_label": "HIGH",
            "risk_adjustment": 0.3,
            "reasons": ["Weapon mentioned", "Transaction intent"],
            "evidence_spans": ["buy gun"],
            "misclassification_risk": "LOW"
        }
        
        classification = RiskClassification.from_llm_response(response)
        
        assert classification.final_label == "HIGH"
        assert classification.risk_adjustment == 0.3
        assert len(classification.reasons) == 2

    def test_from_llm_response_defaults(self):
        classification = RiskClassification.from_llm_response({})
        assert classification.final_label == "MEDIUM"
        assert classification.risk_adjustment == 0.0
        assert classification.reasons == []


class TestRiskAssessment:
    def _result(self, score: float) -> AnalysisResult:
        return AnalysisResult(
            risk_score=score,
            confidence=0.9,
            flags=[],
            detected_keywords=[],
            detected_patterns=[],
            analysis_time="",
            source="rules",
        )

    def test_risk_bands(self):
        high = RiskAssessment(analysis_id="1", content_hash="h", result=self._result(0.8))
        medium = RiskAssessment(analysis_id="2", content_hash="h", result=self._result(0.5))
        low = RiskAssessment(analysis_id="3", content_hash="h", result=self._result(0.2))
        assert high.is_high_risk and not high.is_low_risk
        assert medium.is_medium_risk
        assert low.is_low_risk

    def test_to_dict(self):
        assessment = RiskAssessment(
            analysis_id="a1",
            content_hash="abc",
            result=self._result(0.75),
            platform="reddit",
        )
        data = assessment.to_dict()
        assert data["analysis_id"] == "a1"
        assert data["result"]["risk_score"] == 0.75


class TestExtractedEntities:
    def test_has_transaction_indicators(self):
        empty = ExtractedEntities()
        assert empty.has_transaction_indicators is False
        with_price = ExtractedEntities(prices=["$500"])
        assert with_price.has_transaction_indicators is True


class TestEvasionAndConversation:
    def test_evasion_patterns(self):
        none = EvasionPatterns(patterns_detected=[], confidence=0.0, techniques=[], original_terms={})
        assert none.has_evasion is False
        found = EvasionPatterns(
            patterns_detected=["gvn"],
            confidence=0.7,
            techniques=["leet_speak"],
            original_terms={"gvn": "gun"},
        )
        assert found.has_evasion is True
        assert found.to_dict()["techniques"] == ["leet_speak"]

    def test_conversation_analysis_to_dict(self):
        conv = ConversationAnalysis(
            conversation_id="c1",
            message_count=3,
            participants_count=2,
            deal_progression="negotiation",
            buyer_indicators=["need"],
            seller_indicators=["have"],
            negotiation_patterns=["price talk"],
            risk_score=0.6,
            timeline_start="2024-01-01",
            timeline_end="2024-01-02",
        )
        data = conv.to_dict()
        assert data["conversation_id"] == "c1"
        assert data["deal_progression"] == "negotiation"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

