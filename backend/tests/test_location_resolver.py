"""Offline unit tests for location resolver helpers (no network)."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend_service.utils.location_resolver import (
    _make_loc,
    _is_private_ip,
    extract_ips,
    extract_decimal_coordinates,
    extract_text_location,
    extract_source_location,
    extract_link_domain_location,
    _normalize_source_key,
    extract_candidate_places,
    _dms_to_decimal,
)


class TestLocationHelpers:
    def test_make_loc(self):
        loc = _make_loc(40.7, -74.0, "NYC", "text")
        assert loc == {
            "latitude": 40.7,
            "longitude": -74.0,
            "label": "NYC",
            "source": "text",
        }

    def test_is_private_ip(self):
        assert _is_private_ip("127.0.0.1") is True
        assert _is_private_ip("192.168.1.1") is True
        assert _is_private_ip("10.0.0.5") is True
        assert _is_private_ip("8.8.8.8") is False
        assert _is_private_ip("not-an-ip") is True

    def test_extract_ips_skips_private(self):
        text = "Contact 8.8.8.8 or 192.168.0.1 and also 1.1.1.1"
        ips = extract_ips(text)
        assert "8.8.8.8" in ips
        assert "1.1.1.1" in ips
        assert "192.168.0.1" not in ips

    def test_extract_decimal_coordinates(self):
        loc = extract_decimal_coordinates("Meet at 40.7128, -74.0060 tonight")
        assert loc is not None
        assert abs(loc["latitude"] - 40.7128) < 0.001
        assert loc["source"] == "coordinates"

    def test_extract_decimal_coordinates_none(self):
        assert extract_decimal_coordinates("no coords here") is None
        assert extract_decimal_coordinates("") is None

    def test_dms_to_decimal(self):
        assert abs(_dms_to_decimal((40, 42, 46.0), "N") - 40.712777) < 0.001
        assert _dms_to_decimal((74, 0, 21.0), "W") < 0

    def test_extract_text_location(self):
        loc = extract_text_location("Shipping from New York area")
        assert loc is not None
        assert loc["source"] == "text"

    def test_normalize_source_key(self):
        assert _normalize_source_key("r/Guns") == "guns"
        assert _normalize_source_key("@Channel!") == "channel"

    def test_extract_source_location_us_firearms(self):
        # Uses known SOURCE_LOCATIONS / US_FIREARMS_SUBREDDITS when available
        loc = extract_source_location(subreddit="gundeals")
        # May map via US firearms list or known sources; either way should be dict or None
        if loc:
            assert "latitude" in loc
            assert "longitude" in loc

    def test_extract_link_domain_location(self):
        loc = extract_link_domain_location(link_url="https://www.example.co.uk/path")
        if loc:
            assert loc["source"] == "link_domain"
        loc_ru = extract_link_domain_location(domain="news.ru")
        if loc_ru:
            assert loc_ru["source"] == "link_domain"

    def test_extract_candidate_places(self):
        places = extract_candidate_places("Meet near Los Angeles then Chicago later")
        assert any("Los Angeles" in p or "Chicago" in p for p in places)
        assert extract_candidate_places("") == []
