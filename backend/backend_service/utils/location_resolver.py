"""
Resolve geographic coordinates from post metadata, text, subreddit/channel, EXIF, and IP.
"""
from __future__ import annotations

import hashlib
import ipaddress
import io
import re
from typing import Any, Dict, List, Optional

import requests
from PIL import Image
from PIL.ExifTags import GPSTAGS, TAGS

IP_PATTERN = re.compile(
    r"\b(?:(?:25[0-5]|2[0-4]\d|[01]?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d?\d)\b"
)
COORD_DECIMAL = re.compile(
    r"(?<![\d.])(-?\d{1,2}\.\d{3,8})\s*[,;/]\s*(-?\d{1,3}\.\d{3,8})(?![\d.])"
)
COORD_DMS = re.compile(
    r"(\d{1,2})[°\s]+(\d{1,2})['\s]+(\d{1,2}(?:\.\d+)?)\s*([NSns]).*?"
    r"(\d{1,3})[°\s]+(\d{1,2})['\s]+(\d{1,2}(?:\.\d+)?)\s*([EWew])",
    re.DOTALL,
)

# Cities, countries, conflict regions
KNOWN_LOCATIONS: Dict[str, Dict[str, Any]] = {
    "new york": {"lat": 40.7128, "lng": -74.0060, "label": "New York, USA"},
    "nyc": {"lat": 40.7128, "lng": -74.0060, "label": "New York, USA"},
    "los angeles": {"lat": 34.0522, "lng": -118.2437, "label": "Los Angeles, USA"},
    "san francisco": {"lat": 37.7749, "lng": -122.4194, "label": "San Francisco, USA"},
    "chicago": {"lat": 41.8781, "lng": -87.6298, "label": "Chicago, USA"},
    "houston": {"lat": 29.7604, "lng": -95.3698, "label": "Houston, USA"},
    "dallas": {"lat": 32.7767, "lng": -96.7970, "label": "Dallas, USA"},
    "miami": {"lat": 25.7617, "lng": -80.1918, "label": "Miami, USA"},
    "atlanta": {"lat": 33.7490, "lng": -84.3880, "label": "Atlanta, USA"},
    "phoenix": {"lat": 33.4484, "lng": -112.0740, "label": "Phoenix, USA"},
    "seattle": {"lat": 47.6062, "lng": -122.3321, "label": "Seattle, USA"},
    "denver": {"lat": 39.7392, "lng": -104.9903, "label": "Denver, USA"},
    "boston": {"lat": 42.3601, "lng": -71.0589, "label": "Boston, USA"},
    "las vegas": {"lat": 36.1699, "lng": -115.1398, "label": "Las Vegas, USA"},
    "texas": {"lat": 31.9686, "lng": -99.9018, "label": "Texas, USA"},
    "california": {"lat": 36.7783, "lng": -119.4179, "label": "California, USA"},
    "florida": {"lat": 27.6648, "lng": -81.5158, "label": "Florida, USA"},
    "united states": {"lat": 39.8283, "lng": -98.5795, "label": "United States"},
    "usa": {"lat": 39.8283, "lng": -98.5795, "label": "United States"},
    "america": {"lat": 39.8283, "lng": -98.5795, "label": "United States"},
    "london": {"lat": 51.5074, "lng": -0.1278, "label": "London, UK"},
    "paris": {"lat": 48.8566, "lng": 2.3522, "label": "Paris, France"},
    "berlin": {"lat": 52.5200, "lng": 13.4050, "label": "Berlin, Germany"},
    "moscow": {"lat": 55.7558, "lng": 37.6173, "label": "Moscow, Russia"},
    "saint petersburg": {"lat": 59.9311, "lng": 30.3609, "label": "Saint Petersburg, Russia"},
    "kyiv": {"lat": 50.4501, "lng": 30.5234, "label": "Kyiv, Ukraine"},
    "kiev": {"lat": 50.4501, "lng": 30.5234, "label": "Kyiv, Ukraine"},
    "kharkiv": {"lat": 49.9935, "lng": 36.2304, "label": "Kharkiv, Ukraine"},
    "odesa": {"lat": 46.4825, "lng": 30.7233, "label": "Odesa, Ukraine"},
    "odessa": {"lat": 46.4825, "lng": 30.7233, "label": "Odesa, Ukraine"},
    "donetsk": {"lat": 48.0159, "lng": 37.8028, "label": "Donetsk, Ukraine"},
    "crimea": {"lat": 45.3453, "lng": 34.4997, "label": "Crimea"},
    "bakhmut": {"lat": 48.5950, "lng": 38.0000, "label": "Bakhmut, Ukraine"},
    "mariupol": {"lat": 47.0971, "lng": 37.5434, "label": "Mariupol, Ukraine"},
    "ukraine": {"lat": 48.3794, "lng": 31.1656, "label": "Ukraine"},
    "tel aviv": {"lat": 32.0853, "lng": 34.7818, "label": "Tel Aviv, Israel"},
    "jerusalem": {"lat": 31.7683, "lng": 35.2137, "label": "Jerusalem, Israel"},
    "gaza": {"lat": 31.3547, "lng": 34.3088, "label": "Gaza"},
    "rafah": {"lat": 31.2969, "lng": 34.2435, "label": "Rafah"},
    "west bank": {"lat": 31.9, "lng": 35.2, "label": "West Bank"},
    "israel": {"lat": 31.0461, "lng": 34.8516, "label": "Israel"},
    "palestine": {"lat": 31.9522, "lng": 35.2332, "label": "Palestine"},
    "beirut": {"lat": 33.8938, "lng": 35.5018, "label": "Beirut, Lebanon"},
    "lebanon": {"lat": 33.8547, "lng": 35.8623, "label": "Lebanon"},
    "damascus": {"lat": 33.5138, "lng": 36.2765, "label": "Damascus, Syria"},
    "syria": {"lat": 34.8021, "lng": 38.9968, "label": "Syria"},
    "baghdad": {"lat": 33.3152, "lng": 44.3661, "label": "Baghdad, Iraq"},
    "iraq": {"lat": 33.2232, "lng": 43.6793, "label": "Iraq"},
    "tehran": {"lat": 35.6892, "lng": 51.3890, "label": "Tehran, Iran"},
    "iran": {"lat": 32.4279, "lng": 53.6880, "label": "Iran"},
    "istanbul": {"lat": 41.0082, "lng": 28.9784, "label": "Istanbul, Turkey"},
    "ankara": {"lat": 39.9334, "lng": 32.8597, "label": "Ankara, Turkey"},
    "turkey": {"lat": 38.9637, "lng": 35.2433, "label": "Turkey"},
    "dubai": {"lat": 25.2048, "lng": 55.2708, "label": "Dubai, UAE"},
    "riyadh": {"lat": 24.7136, "lng": 46.6753, "label": "Riyadh, Saudi Arabia"},
    "yemen": {"lat": 15.5527, "lng": 48.5164, "label": "Yemen"},
    "sanaa": {"lat": 15.3694, "lng": 44.1910, "label": "Sanaa, Yemen"},
    "cairo": {"lat": 30.0444, "lng": 31.2357, "label": "Cairo, Egypt"},
    "africa": {"lat": 8.7832, "lng": 20.5085, "label": "Africa"},
    "europe": {"lat": 50.0, "lng": 10.0, "label": "Europe"},
    "mumbai": {"lat": 19.0760, "lng": 72.8777, "label": "Mumbai, India"},
    "delhi": {"lat": 28.7041, "lng": 77.1025, "label": "Delhi, India"},
    "beijing": {"lat": 39.9042, "lng": 116.4074, "label": "Beijing, China"},
    "taiwan": {"lat": 23.6978, "lng": 120.9605, "label": "Taiwan"},
    "tokyo": {"lat": 35.6762, "lng": 139.6503, "label": "Tokyo, Japan"},
    "kabul": {"lat": 34.5553, "lng": 69.2075, "label": "Kabul, Afghanistan"},
    "afghanistan": {"lat": 33.9391, "lng": 67.7100, "label": "Afghanistan"},
    "pakistan": {"lat": 30.3753, "lng": 69.3451, "label": "Pakistan"},
    "india": {"lat": 20.5937, "lng": 78.9629, "label": "India"},
    "russia": {"lat": 61.5240, "lng": 105.3188, "label": "Russia"},
    "belarus": {"lat": 53.7098, "lng": 27.9534, "label": "Belarus"},
    "minsk": {"lat": 53.9006, "lng": 27.5590, "label": "Minsk, Belarus"},
    "warsaw": {"lat": 52.2297, "lng": 21.0122, "label": "Warsaw, Poland"},
    "poland": {"lat": 51.9194, "lng": 19.1451, "label": "Poland"},
    "germany": {"lat": 51.1657, "lng": 10.4515, "label": "Germany"},
    "france": {"lat": 46.2276, "lng": 2.2137, "label": "France"},
    "uk": {"lat": 55.3781, "lng": -3.4360, "label": "United Kingdom"},
    "britain": {"lat": 55.3781, "lng": -3.4360, "label": "United Kingdom"},
    "england": {"lat": 52.3555, "lng": -1.1743, "label": "England"},
    "mexico": {"lat": 23.6345, "lng": -102.5528, "label": "Mexico"},
    "brazil": {"lat": -14.2350, "lng": -51.9253, "label": "Brazil"},
    "sudan": {"lat": 12.8628, "lng": 30.2176, "label": "Sudan"},
    "ethiopia": {"lat": 9.1450, "lng": 40.4897, "label": "Ethiopia"},
    "somalia": {"lat": 5.1521, "lng": 46.1996, "label": "Somalia"},
    "nigeria": {"lat": 9.0820, "lng": 8.6753, "label": "Nigeria"},
    "caribbean": {"lat": 18.2208, "lng": -66.5901, "label": "Caribbean"},
    "combloc": {"lat": 55.0, "lng": 30.0, "label": "Eastern Europe / Combloc"},
    "eastern europe": {"lat": 50.0, "lng": 30.0, "label": "Eastern Europe"},
}

# Direct subreddit / Telegram channel -> region (from real community focus)
SOURCE_LOCATIONS: Dict[str, Dict[str, Any]] = {
    "ukraine": {"lat": 48.3794, "lng": 31.1656, "label": "Ukraine (source)", "source": "subreddit"},
    "ukrainianconflict": {"lat": 48.3794, "lng": 31.1656, "label": "Ukraine (source)", "source": "subreddit"},
    "comblocmarket": {"lat": 50.0, "lng": 30.0, "label": "Eastern Europe (r/ComblocMarket)", "source": "subreddit"},
    "milsurp": {"lat": 50.0, "lng": 30.0, "label": "Military surplus / global", "source": "subreddit"},
    "mosinnagant": {"lat": 55.7558, "lng": 37.6173, "label": "Russia (Mosin heritage)", "source": "subreddit"},
    "sks": {"lat": 39.9042, "lng": 116.4074, "label": "China (SKS heritage)", "source": "subreddit"},
    "ak47": {"lat": 50.0, "lng": 30.0, "label": "AK / Eastern bloc", "source": "subreddit"},
    "rybar": {"lat": 55.7558, "lng": 37.6173, "label": "Russia (Rybar)", "source": "channel"},
    "russianarms": {"lat": 55.7558, "lng": 37.6173, "label": "Russia (channel)", "source": "channel"},
    "uaweapons": {"lat": 48.3794, "lng": 31.1656, "label": "Ukraine (channel)", "source": "channel"},
    "nexta_tv": {"lat": 53.9006, "lng": 27.5590, "label": "Belarus (NEXTA)", "source": "channel"},
    "warmonitors": {"lat": 33.0, "lng": 38.0, "label": "Middle East conflicts", "source": "channel"},
    "armyrecognition": {"lat": 50.8503, "lng": 4.3517, "label": "Belgium (Army Recognition)", "source": "channel"},
    "thedeaddistrict": {"lat": 48.3794, "lng": 31.1656, "label": "Ukraine (war zone OSINT)", "source": "channel"},
    "defenceblog": {"lat": 51.5074, "lng": -0.1278, "label": "UK defence", "source": "channel"},
}

# US-centric firearms subreddits (real community locale)
US_FIREARMS_SUBREDDITS = {
    "gundeals", "gunaccessoriesforsale", "comblocmarket", "gunaccessoryvendors", "gunsales",
    "gunsforsale", "airsoftmarket", "brassswap", "reloadingexchange", "gunholsterclassfieds",
    "knifeswap", "knifedeals", "balisongsale", "edcexchange", "opaborat", "gunoptics",
    "suppressednfa", "nfa", "form1", "firearms", "guns", "ar15", "glocks", "sigsauer",
    "smithandwesson", "czfirearms", "beretta", "hecklerkoch", "fnherstal", "ruger",
    "remington", "mossberg", "shotguns", "revolvers", "1911", "longrange", "plebeianar",
    "ar15build", "gunporn", "handguns", "ccw", "edc", "tacticalgear", "qualitytacticalgear",
    "militarycollecting", "ammo", "reloading", "instockammo", "liberalgunowners",
    "socialistra", "progun", "firearmsadvice", "gunmemes", "forgottenweapons", "mauser",
}

TLD_COUNTRY_HINTS: Dict[str, Dict[str, Any]] = {
    "uk": {"lat": 55.3781, "lng": -3.4360, "label": "United Kingdom (link TLD)"},
    "de": {"lat": 51.1657, "lng": 10.4515, "label": "Germany (link TLD)"},
    "fr": {"lat": 46.2276, "lng": 2.2137, "label": "France (link TLD)"},
    "ru": {"lat": 61.5240, "lng": 105.3188, "label": "Russia (link TLD)"},
    "ua": {"lat": 48.3794, "lng": 31.1656, "label": "Ukraine (link TLD)"},
    "il": {"lat": 31.0461, "lng": 34.8516, "label": "Israel (link TLD)"},
    "cn": {"lat": 35.8617, "lng": 104.1954, "label": "China (link TLD)"},
}

_ip_cache: Dict[str, Optional[Dict[str, Any]]] = {}
_nominatim_cache: Dict[str, Optional[Dict[str, Any]]] = {}


def _make_loc(lat: float, lng: float, label: str, source: str) -> Dict[str, Any]:
    return {"latitude": lat, "longitude": lng, "label": label, "source": source}


def _is_private_ip(ip: str) -> bool:
    try:
        addr = ipaddress.ip_address(ip)
        return addr.is_private or addr.is_loopback
    except ValueError:
        return True


def extract_ips(text: str) -> List[str]:
    if not text:
        return []
    seen: set[str] = set()
    result: List[str] = []
    for match in IP_PATTERN.findall(text):
        if match not in seen and not _is_private_ip(match):
            seen.add(match)
            result.append(match)
    return result


def geolocate_ip(ip: str, timeout: float = 5.0) -> Optional[Dict[str, Any]]:
    if _is_private_ip(ip):
        return None
    if ip in _ip_cache:
        return _ip_cache[ip]
    try:
        resp = requests.get(
            f"http://ip-api.com/json/{ip}?fields=status,lat,lon,city,country,query",
            timeout=timeout,
        )
        if resp.status_code != 200:
            _ip_cache[ip] = None
            return None
        data = resp.json()
        if data.get("status") != "success":
            _ip_cache[ip] = None
            return None
        loc = _make_loc(
            float(data["lat"]),
            float(data["lon"]),
            f"{data.get('city', 'Unknown')}, {data.get('country', '')} (IP: {data.get('query', ip)})",
            "ip",
        )
        _ip_cache[ip] = loc
        return loc
    except Exception:
        _ip_cache[ip] = None
        return None


def extract_decimal_coordinates(text: str) -> Optional[Dict[str, Any]]:
    if not text:
        return None
    for lat_s, lng_s in COORD_DECIMAL.findall(text):
        try:
            lat, lng = float(lat_s), float(lng_s)
            if -90 <= lat <= 90 and -180 <= lng <= 180:
                return _make_loc(lat, lng, f"Coordinates ({lat:.4f}, {lng:.4f})", "coordinates")
        except ValueError:
            continue
    for m in COORD_DMS.finditer(text):
        try:
            lat = int(m.group(1)) + int(m.group(2)) / 60 + float(m.group(3)) / 3600
            lng = int(m.group(5)) + int(m.group(6)) / 60 + float(m.group(7)) / 3600
            if m.group(4).upper() == "S":
                lat = -lat
            if m.group(8).upper() == "W":
                lng = -lng
            if -90 <= lat <= 90 and -180 <= lng <= 180:
                return _make_loc(lat, lng, f"Coordinates ({lat:.4f}, {lng:.4f})", "coordinates")
        except (ValueError, TypeError):
            continue
    return None


def _dms_to_decimal(dms: tuple, ref: str) -> float:
    degrees, minutes, seconds = dms
    decimal = float(degrees) + float(minutes) / 60.0 + float(seconds) / 3600.0
    if ref in ("S", "W"):
        decimal = -decimal
    return decimal


def extract_exif_gps(image_bytes: bytes) -> Optional[Dict[str, Any]]:
    if not image_bytes:
        return None
    try:
        image = Image.open(io.BytesIO(image_bytes))
        exif = image._getexif()
        if not exif:
            return None
        gps_info = {}
        for tag_id, value in exif.items():
            tag = TAGS.get(tag_id, tag_id)
            if tag == "GPSInfo":
                for gps_tag_id, gps_value in value.items():
                    gps_tag = GPSTAGS.get(gps_tag_id, gps_tag_id)
                    gps_info[gps_tag] = gps_value
        if "GPSLatitude" not in gps_info or "GPSLongitude" not in gps_info:
            return None
        lat = _dms_to_decimal(gps_info["GPSLatitude"], gps_info.get("GPSLatitudeRef", "N"))
        lng = _dms_to_decimal(gps_info["GPSLongitude"], gps_info.get("GPSLongitudeRef", "E"))
        return _make_loc(lat, lng, f"Photo GPS ({lat:.4f}, {lng:.4f})", "photo_exif")
    except Exception:
        return None


def extract_telegram_geo(message: Any) -> Optional[Dict[str, Any]]:
    try:
        geo = getattr(message, "geo", None)
        if geo is not None:
            lat = getattr(geo, "lat", None)
            lng = getattr(geo, "long", None)
            if lat is not None and lng is not None:
                return _make_loc(float(lat), float(lng), f"Telegram geo ({float(lat):.4f}, {float(lng):.4f})", "metadata")
        media = getattr(message, "media", None)
        if media is not None:
            media_geo = getattr(media, "geo", None)
            if media_geo is not None:
                lat = getattr(media_geo, "lat", None)
                lng = getattr(media_geo, "long", None)
                if lat is not None and lng is not None:
                    return _make_loc(float(lat), float(lng), f"Telegram venue ({float(lat):.4f}, {float(lng):.4f})", "metadata")
    except Exception:
        pass
    return None


def extract_text_location(text: str) -> Optional[Dict[str, Any]]:
    if not text:
        return None
    lower = text.lower()
    for name in sorted(KNOWN_LOCATIONS.keys(), key=len, reverse=True):
        if re.search(rf"\b{re.escape(name)}\b", lower):
            loc = KNOWN_LOCATIONS[name]
            return _make_loc(loc["lat"], loc["lng"], loc["label"], "text")
    return None


def _normalize_source_key(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", (name or "").lower().lstrip("@r/"))


def extract_source_location(
    subreddit: Optional[str] = None,
    channel: Optional[str] = None,
    chat_title: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    keys = []
    for raw in (subreddit, channel, chat_title):
        if raw:
            keys.append(_normalize_source_key(raw))

    for key in keys:
        if key in SOURCE_LOCATIONS:
            loc = SOURCE_LOCATIONS[key]
            return _make_loc(loc["lat"], loc["lng"], loc["label"], loc.get("source", "subreddit"))

    for key in keys:
        for name in sorted(KNOWN_LOCATIONS.keys(), key=len, reverse=True):
            norm = name.replace(" ", "")
            if norm in key or key in norm:
                loc = KNOWN_LOCATIONS[name]
                return _make_loc(loc["lat"], loc["lng"], f"{loc['label']} (from source: {key})", "subreddit")

    for key in keys:
        if key in US_FIREARMS_SUBREDDITS:
            return _make_loc(39.8283, -98.5795, f"United States (r/{key})", "subreddit")

    return None


def extract_link_domain_location(link_url: Optional[str] = None, domain: Optional[str] = None) -> Optional[Dict[str, Any]]:
    host = (domain or "").lower()
    if not host and link_url:
        m = re.search(r"https?://([^/]+)", link_url.lower())
        host = m.group(1) if m else ""
    host = host.split(":")[0]
    if host.startswith("www."):
        host = host[4:]
    parts = host.rsplit(".", 1)
    if len(parts) == 2 and parts[1] in TLD_COUNTRY_HINTS:
        loc = TLD_COUNTRY_HINTS[parts[1]]
        return _make_loc(loc["lat"], loc["lng"], loc["label"], "link_domain")
    return None


def geocode_place_name(place: str, timeout: float = 4.0) -> Optional[Dict[str, Any]]:
    key = place.strip().lower()
    if not key or len(key) < 3:
        return None
    if key in _nominatim_cache:
        return _nominatim_cache[key]
    try:
        resp = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": place, "format": "json", "limit": 1},
            headers={"User-Agent": "WeaponsTradeDetection/1.0 (academic research)"},
            timeout=timeout,
        )
        if resp.status_code != 200:
            _nominatim_cache[key] = None
            return None
        data = resp.json()
        if not data:
            _nominatim_cache[key] = None
            return None
        item = data[0]
        loc = _make_loc(
            float(item["lat"]),
            float(item["lon"]),
            item.get("display_name", place),
            "geocoded",
        )
        _nominatim_cache[key] = loc
        return loc
    except Exception:
        _nominatim_cache[key] = None
        return None


def extract_candidate_places(text: str) -> List[str]:
    """Pull capitalized multi-word phrases that may be place names."""
    if not text:
        return []
    candidates: List[str] = []
    for match in re.finditer(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2})\b", text):
        phrase = match.group(1).strip()
        if phrase.lower() in {"the", "and", "for", "with", "from", "this", "that"}:
            continue
        if len(phrase) >= 4:
            candidates.append(phrase)
    return candidates[:5]


def download_image_bytes(url: str, timeout: float = 8.0) -> Optional[bytes]:
    if not url or not url.startswith("http"):
        return None
    try:
        resp = requests.get(url, timeout=timeout, headers={"User-Agent": "WeaponsTradeDetection/1.0"})
        if resp.status_code == 200 and resp.content:
            return resp.content
    except Exception:
        pass
    return None


def resolve_post_location(
    *,
    text: str = "",
    message: Any = None,
    image_bytes: Optional[bytes] = None,
    image_url: Optional[str] = None,
    subreddit: Optional[str] = None,
    channel: Optional[str] = None,
    chat_title: Optional[str] = None,
    author_flair: Optional[str] = None,
    link_flair: Optional[str] = None,
    link_url: Optional[str] = None,
    domain: Optional[str] = None,
    llm_text: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """Resolve best geo point from all available post metadata."""
    combined = " ".join(
        filter(
            None,
            [text, author_flair, link_flair, llm_text, chat_title, subreddit, channel],
        )
    )

    if message is not None:
        meta_loc = extract_telegram_geo(message)
        if meta_loc:
            return meta_loc

    if image_bytes:
        exif_loc = extract_exif_gps(image_bytes)
        if exif_loc:
            return exif_loc
    elif image_url:
        downloaded = download_image_bytes(image_url)
        if downloaded:
            exif_loc = extract_exif_gps(downloaded)
            if exif_loc:
                return exif_loc

    coord_loc = extract_decimal_coordinates(combined)
    if coord_loc:
        return coord_loc

    text_loc = extract_text_location(combined)
    if text_loc:
        return text_loc

    for ip in extract_ips(combined):
        ip_loc = geolocate_ip(ip)
        if ip_loc:
            return ip_loc

    link_loc = extract_link_domain_location(link_url=link_url, domain=domain)
    if link_loc:
        return link_loc

    source_loc = extract_source_location(subreddit=subreddit, channel=channel, chat_title=chat_title)
    if source_loc:
        return source_loc

    for candidate in extract_candidate_places(combined):
        if candidate.lower() in KNOWN_LOCATIONS:
            loc = KNOWN_LOCATIONS[candidate.lower()]
            return _make_loc(loc["lat"], loc["lng"], loc["label"], "text")
        geo = geocode_place_name(candidate)
        if geo:
            return geo

    return None
