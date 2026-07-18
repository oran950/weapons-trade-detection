"""Tests for Pydantic request model validation."""
import sys
import os

import pytest
from pydantic import ValidationError

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend_service.models.requests import (
    AnalysisRequest,
    ContentGenerationRequest,
    BatchGenerationRequest,
    BigDataGenerationRequest,
    RedditCollectionParams,
    TelegramCollectionParams,
)


class TestAnalysisRequest:
    def test_defaults(self):
        req = AnalysisRequest(content="hello")
        assert req.use_llm is False
        assert req.always_use_llm is False

    def test_requires_content(self):
        with pytest.raises(ValidationError):
            AnalysisRequest()


class TestContentGenerationRequest:
    def test_valid(self):
        req = ContentGenerationRequest(content_type="post", intensity_level="high", quantity=5)
        assert req.quantity == 5
        assert req.language == "en"

    def test_invalid_content_type(self):
        with pytest.raises(ValidationError):
            ContentGenerationRequest(content_type="tweet", intensity_level="low")

    def test_invalid_intensity(self):
        with pytest.raises(ValidationError):
            ContentGenerationRequest(content_type="post", intensity_level="extreme")

    def test_quantity_bounds(self):
        with pytest.raises(ValidationError):
            ContentGenerationRequest(content_type="post", intensity_level="low", quantity=0)
        with pytest.raises(ValidationError):
            ContentGenerationRequest(content_type="post", intensity_level="low", quantity=51)


class TestBatchAndBigDataRequests:
    def test_batch_bounds(self):
        ok = BatchGenerationRequest(quantity_per_type=10)
        assert ok.quantity_per_type == 10
        with pytest.raises(ValidationError):
            BatchGenerationRequest(quantity_per_type=21)

    def test_big_data_defaults_and_bounds(self):
        req = BigDataGenerationRequest()
        assert req.total_quantity == 2000
        assert "reddit" in req.platforms
        with pytest.raises(ValidationError):
            BigDataGenerationRequest(total_quantity=50)
        with pytest.raises(ValidationError):
            BigDataGenerationRequest(total_quantity=20000)


class TestCollectionParams:
    def test_reddit_defaults(self):
        params = RedditCollectionParams()
        assert params.subreddits == ["news"]
        assert params.limit_per_subreddit == 25

    def test_telegram_defaults(self):
        params = TelegramCollectionParams()
        assert params.channels == []
        assert params.limit_per_source == 50
