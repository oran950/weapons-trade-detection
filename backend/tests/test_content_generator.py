"""Tests for synthetic content generation."""
import random
import sys
import os

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from generation.content_generator import ContentParameters, SyntheticContentGenerator


@pytest.fixture
def generator():
    return SyntheticContentGenerator()


class TestContentParameters:
    def test_defaults(self):
        params = ContentParameters(content_type="post", intensity_level="low")
        assert params.language == "en"
        assert params.quantity == 1
        assert params.include_contact is False
        assert params.include_pricing is False
        assert params.content_length == "medium"

    def test_all_fields(self):
        params = ContentParameters(
            content_type="ad",
            intensity_level="high",
            language="en",
            include_contact=True,
            include_pricing=True,
            quantity=5,
            platform="reddit",
            content_length="short",
        )
        assert params.platform == "reddit"
        assert params.quantity == 5


class TestSyntheticContentGenerator:
    def test_generate_contact_info(self, generator):
        random.seed(42)
        contact = generator.generate_contact_info()
        assert set(contact) == {"phone", "email", "username", "app"}
        assert contact["phone"].startswith("555-")
        assert contact["email"].endswith("@tempmail.com")
        assert contact["app"] in {"WhatsApp", "Telegram", "Signal", "Discord", "Wire"}

    def test_generate_pricing_ranges(self, generator):
        random.seed(1)
        low = generator.generate_pricing("low")
        medium = generator.generate_pricing("medium")
        high = generator.generate_pricing("high")
        assert isinstance(low, str) and len(low) > 0
        assert isinstance(medium, str) and len(medium) > 0
        assert isinstance(high, str) and len(high) > 0

    def test_generate_metadata(self, generator):
        random.seed(7)
        meta = generator.generate_metadata(platform="Reddit")
        assert meta["platform"] == "Reddit"
        assert "timestamp" in meta
        assert "location" in meta
        assert meta["user_id"].startswith("user_")
        assert meta["post_id"].startswith("post_")

    def test_generate_post_content_lengths(self, generator):
        for length in ("short", "medium", "long"):
            params = ContentParameters(
                content_type="post",
                intensity_level="low",
                content_length=length,
            )
            content = generator.generate_post_content(params)
            assert isinstance(content, str) and len(content) > 0

    def test_high_intensity_uses_weapon_vocab(self, generator):
        random.seed(99)
        params = ContentParameters(content_type="post", intensity_level="high")
        content = generator.generate_post_content(params).lower()
        vocab = generator.vocabulary["high"]["items"] + generator.vocabulary["high"]["descriptors"]
        assert any(term in content for term in vocab)

    def test_message_ad_forum_content(self, generator):
        params = ContentParameters(content_type="message", intensity_level="medium")
        assert generator.generate_message_content(params)
        assert generator.generate_ad_content(params)
        assert generator.generate_forum_content(params)

    def test_apply_platform_formatting_unknown(self, generator):
        original = "selling gear today"
        assert generator.apply_platform_formatting(original, "myspace") == original

    def test_apply_platform_formatting_twitter_truncates(self, generator):
        random.seed(0)
        long_text = "x" * 400
        result = generator.apply_platform_formatting(long_text, "twitter")
        assert len(result) <= 280
        assert result.endswith("...")

    def test_add_variations_high(self, generator):
        result = generator.add_variations("selling a gun for a deal", "high")
        assert "moving" in result
        assert "piece" in result
        assert "transaction" in result

    def test_add_variations_low_unchanged(self, generator):
        text = "selling a gun for a deal"
        assert generator.add_variations(text, "low") == text

    def test_generate_content_structure(self, generator):
        random.seed(3)
        params = ContentParameters(
            content_type="post",
            intensity_level="medium",
            quantity=3,
            include_contact=True,
            include_pricing=True,
        )
        items = generator.generate_content(params)
        assert len(items) == 3
        for item in items:
            assert item["id"].startswith("synthetic_")
            assert "content" in item
            assert item["parameters"]["type"] == "post"
            assert item["parameters"]["intensity"] == "medium"
            assert item["contact_info"] is not None
            assert item["pricing"] is not None
            assert "generated_at" in item

    def test_generate_content_without_extras(self, generator):
        params = ContentParameters(content_type="ad", intensity_level="low", quantity=1)
        item = generator.generate_content(params)[0]
        assert item["contact_info"] is None
        assert item["pricing"] is None

    def test_unknown_content_type_falls_back_to_post(self, generator):
        params = ContentParameters(content_type="unknown", intensity_level="low", quantity=1)
        items = generator.generate_content(params)
        assert len(items) == 1
        assert items[0]["parameters"]["type"] == "unknown"

    def test_generate_batch(self, generator):
        result = generator.generate_batch(
            {"quantity_per_type": 1, "include_contact": False, "include_pricing": False}
        )
        assert set(result) >= {
            "low_intensity",
            "medium_intensity",
            "high_intensity",
            "statistics",
        }
        # 3 intensities × 4 types × 1 = 12 per intensity bucket
        assert len(result["low_intensity"]) == 4
        assert len(result["medium_intensity"]) == 4
        assert len(result["high_intensity"]) == 4
        assert result["statistics"]["total_generated"] == 12

    def test_generate_big_data_batch_small(self, generator):
        result = generator.generate_big_data_batch(
            total_quantity=24,
            platforms=["reddit", "twitter"],
            content_lengths=["short", "medium"],
        )
        assert len(result["content"]) == 24
        stats = result["statistics"]
        assert stats["total_generated"] == 24
        assert "platform_distribution" in stats
        assert "intensity_distribution" in stats
