"""Tests for OSINT PDF helpers and PDF generation."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from reports.osint_pdf import (
    MAX_LIST_ITEMS,
    _truncate,
    _p,
    _risk_color,
    _clip_list,
    _exec_summary_collection,
    _exec_summary_text,
    _digest_post_table_data,
    build_osint_pdf,
    COLOR_ACCENT_HIGH,
    COLOR_ACCENT_MED,
    COLOR_ACCENT_LOW,
)


class TestOsintPdfHelpers:
    def test_truncate_empty(self):
        assert _truncate(None, 10) == ("", False)
        assert _truncate("", 10) == ("", False)

    def test_truncate_under_limit(self):
        assert _truncate("hello", 10) == ("hello", False)

    def test_truncate_over_limit(self):
        text, truncated = _truncate("x" * 200, 100)
        assert truncated is True
        assert "[Truncated for report length]" in text
        assert len(text) < 200

    def test_p_escapes_html(self):
        assert _p("a < b & c") == "a &lt; b &amp; c"
        assert _p("") == ""

    def test_risk_color(self):
        assert _risk_color("HIGH") == COLOR_ACCENT_HIGH
        assert _risk_color("CRITICAL") == COLOR_ACCENT_HIGH
        assert _risk_color("MEDIUM") == COLOR_ACCENT_MED
        assert _risk_color("LOW") == COLOR_ACCENT_LOW
        assert _risk_color(None) is not None

    def test_clip_list_under_cap(self):
        items, truncated = _clip_list(["a", "b"], "flags")
        assert items == ["a", "b"]
        assert truncated is False

    def test_clip_list_over_cap(self):
        items, truncated = _clip_list(list(range(MAX_LIST_ITEMS + 5)), "flags")
        assert truncated is True
        assert any("omitted" in x for x in items)

    def test_exec_summary_collection(self):
        text = _exec_summary_collection(
            {"risk_level": "HIGH", "risk_score": 0.8, "flags": ["a", "b"]},
            {"summary": "Weapon trade indicators present"},
        )
        assert "HIGH" in text
        assert "80%" in text
        assert "2 rule-based" in text
        assert "LLM narrative" in text

    def test_exec_summary_text(self):
        text = _exec_summary_text("MEDIUM", 0.5, "Borderline content", 3)
        assert "MEDIUM" in text
        assert "50%" in text
        assert "3 indicator" in text

    def test_digest_post_table_data(self):
        rows = _digest_post_table_data(
            [
                {
                    "id": "abc1234567890",
                    "title": "Test post",
                    "platform": "reddit",
                    "url": "https://example.com/x",
                    "risk_analysis": {"risk_level": "HIGH", "risk_score": 0.91},
                    "llm_analysis": {"is_potentially_illegal": True},
                },
                {
                    "id": "bad",
                    "title": None,
                    "risk_analysis": {"risk_score": "nope"},
                },
            ]
        )
        assert rows[0][0] == "Record"
        assert rows[1][3] == "HIGH"
        assert rows[1][4] == "91"
        assert rows[1][5] == "Y"
        assert rows[2][4] == "—"


class TestBuildOsintPdf:
    def test_text_analysis_pdf(self):
        pdf = build_osint_pdf(
            {
                "report_type": "text_analysis",
                "risk_level": "HIGH",
                "risk_score": 0.85,
                "summary": "Weapons keywords detected",
                "flags": ["HIGH RISK: gun"],
                "detected_keywords": ["firearms: gun"],
                "content": "Looking to buy a gun",
            }
        )
        assert isinstance(pdf, bytes)
        assert pdf.startswith(b"%PDF")

    def test_collection_item_pdf(self):
        pdf = build_osint_pdf(
            {
                "report_type": "collection_item",
                "title": "Sample listing",
                "content": "Synthetic research content",
                "platform": "reddit",
                "url": "https://example.com",
                "risk_analysis": {
                    "risk_level": "MEDIUM",
                    "risk_score": 0.55,
                    "flags": ["pattern match"],
                },
                "llm_analysis": {"summary": "Uncertain"},
            }
        )
        assert pdf.startswith(b"%PDF")
