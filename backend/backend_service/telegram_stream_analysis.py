"""
Shared Telegram SSE / job analysis: collect messages, analyze like Reddit stream.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

LogFn = Callable[[str], None]


def normalize_telegram_channel(raw: str) -> str:
    """Strip @ and accept t.me URLs for Telethon get_entity."""
    s = (raw or "").strip()
    s = s.lstrip("@")
    low = s.lower()
    if "t.me/" in low:
        tail = low.split("t.me/", 1)[-1]
        if tail.startswith("s/"):
            tail = tail[2:]
        if tail.startswith("joinchat/") or tail.startswith("+"):
            return s
        s = tail.split("/")[0].split("?")[0]
    return s.strip()


def normalize_telegram_sources(sources: List[str]) -> List[str]:
    out: List[str] = []
    for x in sources:
        n = normalize_telegram_channel(x)
        if n and n not in out:
            out.append(n)
    return out


def _default_log(msg: str) -> None:
    print(msg, flush=True)


async def collect_telegram_items(
    client: Any,
    channel_list: List[str],
    limit: int,
    log_fn: Optional[LogFn] = None,
) -> List[Dict[str, Any]]:
    """Collect Telethon messages from public channels (text and/or photo)."""
    from telethon.errors import ChannelPrivateError, UsernameNotOccupiedError

    log = log_fn or _default_log
    items: List[Dict[str, Any]] = []

    for raw in channel_list:
        channel_username = normalize_telegram_channel(raw)
        if not channel_username:
            continue
        try:
            channel = await client.get_entity(channel_username)
            title = getattr(channel, "title", channel_username)
        except UsernameNotOccupiedError:
            log(f"Channel @{channel_username} not found, skipping")
            continue
        except ChannelPrivateError:
            log(f"Channel @{channel_username} is private, skipping")
            continue
        except Exception as e:
            log(f"Error resolving @{channel_username}: {e}")
            continue

        async for message in client.iter_messages(channel, limit=limit):
            has_text = bool(message.text and str(message.text).strip())
            has_photo = bool(getattr(message, "photo", None))
            if not has_text and not has_photo:
                continue
            items.append(
                {
                    "channel_username": channel_username,
                    "channel_title": title,
                    "message": message,
                }
            )

    return items


async def analyze_telegram_item(
    *,
    analyzer: Any,
    item: Dict[str, Any],
    client: Any,
    image_analyzer: Any,
    llm_analyzer: Any,
    vision_available: bool,
    llm_available: bool,
    analyze_images: bool,
    llm_analysis: bool,
    idx: int,
    total: int,
    log_print: LogFn,
) -> Dict[str, Any]:
    """
    Analyze one Telegram message (text + optional LLaVA + LLM).
    Returns the same structure as Reddit's analyze_single_post in server.py.
    """
    from backend_service.utils.hashing import hash_username

    message = item["message"]
    channel_username = item["channel_username"]
    channel_title = item["channel_title"]

    combined_text = (message.text or "").strip()
    analysis = analyzer.analyze_text(combined_text if combined_text else " ")
    risk_score = analysis.get("risk_score", 0.0)
    if risk_score >= 0.75:
        risk_level = "HIGH"
    elif risk_score >= 0.45:
        risk_level = "MEDIUM"
    elif risk_score >= 0.25:
        risk_level = "LOW"
    else:
        risk_level = "NONE"

    text_for_title = combined_text or "[photo]"
    title = text_for_title[:100] + ("..." if len(text_for_title) > 100 else "")
    content = (message.text or "")[:500]

    sender_id = str(message.sender_id) if message.sender_id else "anonymous"
    author_hash = hash_username(sender_id)

    is_video_msg = bool(getattr(message, "video", None))
    image_analysis = None
    annotated_image = None
    did_image_analysis = False
    weapons_found = False

    should_analyze_image = False
    if (
        analyze_images
        and vision_available
        and image_analyzer
        and getattr(message, "photo", None)
        and not is_video_msg
    ):
        should_analyze_image = (
            risk_score >= 0.25
            or risk_level in ("LOW", "MEDIUM", "HIGH")
            or (not combined_text and message.photo)
        )

    if should_analyze_image:
        try:
            image_bytes = await client.download_media(message, file=bytes)
            if image_bytes:
                label = f"tg:{channel_username}:{message.id}"
                image_result = await image_analyzer.analyze_image_bytes(
                    image_bytes, source_label=label
                )
                did_image_analysis = True
                if image_result.contains_weapons:
                    weapons_found = True
                    if image_result.overall_risk == "HIGH" and risk_level != "HIGH":
                        risk_level = "HIGH"
                        risk_score = max(risk_score, image_result.risk_score)
                    image_analysis = {
                        "contains_weapons": True,
                        "weapon_count": image_result.weapon_count,
                        "detections": [d.to_dict() for d in image_result.detections],
                        "overall_risk": image_result.overall_risk,
                        "analysis_notes": image_result.analysis_notes,
                        "processing_time_ms": image_result.processing_time_ms,
                    }
                    annotated_image = image_result.annotated_image_base64
                else:
                    is_verified = getattr(image_result, "analysis_completed", True)
                    risk_reduction = 0.2
                    if is_verified:
                        risk_score = max(0, risk_score - risk_reduction)
                        if risk_score >= 0.75:
                            risk_level = "HIGH"
                        elif risk_score >= 0.45:
                            risk_level = "MEDIUM"
                        elif risk_score >= 0.25:
                            risk_level = "LOW"
                        else:
                            risk_level = "NONE"
                    image_analysis = {
                        "contains_weapons": False,
                        "weapon_count": 0,
                        "image_verified_safe": is_verified,
                        "analysis_completed": is_verified,
                        "risk_reduction_applied": risk_reduction if is_verified else 0,
                        "analysis_notes": image_result.analysis_notes,
                        "processing_time_ms": image_result.processing_time_ms,
                    }
        except Exception as img_err:
            log_print(f"⚠️ Telegram image analysis error {channel_username}/{message.id}: {img_err}")
            image_analysis = {
                "error": str(img_err),
                "contains_weapons": False,
                "analysis_completed": False,
            }

    llm_result = None
    did_llm_analysis = False
    is_illegal = False

    if llm_analysis and llm_available and llm_analyzer:
        try:
            did_llm_analysis = True
            llm_response = await llm_analyzer.analyze_post(
                title=title,
                content=content or "",
                source=f"@{channel_username}",
            )
            llm_result = llm_response.to_dict()
            if llm_response.is_potentially_illegal:
                is_illegal = True
                if llm_response.risk_assessment == "CRITICAL":
                    risk_score = 1.0
                    risk_level = "CRITICAL"
                elif llm_response.risk_assessment == "HIGH" and risk_level != "CRITICAL":
                    risk_score = max(risk_score, 0.85)
                    risk_level = "HIGH"
            elif not llm_response.is_weapon_related and risk_score > 0:
                risk_reduction = 0.3
                risk_score = max(0, risk_score - risk_reduction)
                if risk_score >= 0.75:
                    risk_level = "HIGH"
                elif risk_score >= 0.45:
                    risk_level = "MEDIUM"
                elif risk_score >= 0.25:
                    risk_level = "LOW"
                else:
                    risk_level = "NONE"
        except Exception as llm_err:
            log_print(f"⚠️ Telegram LLM error {channel_username}/{message.id}: {llm_err}")
            llm_result = {"error": str(llm_err), "is_potentially_illegal": False}

    created = message.date.timestamp() if message.date else 0.0
    post_data = {
        "id": f"tg-{channel_username}-{message.id}",
        "title": title,
        "content": content,
        "subreddit": f"@{channel_username}",
        "channel": channel_username,
        "chat_title": channel_title,
        "chat_type": "channel",
        "author_hash": author_hash,
        "score": 0,
        "num_comments": 0,
        "url": f"https://t.me/{channel_username}/{message.id}",
        "created_utc": created,
        "collected_at": datetime.now().isoformat(),
        "platform": "telegram",
        "image_url": None,
        "thumbnail": None,
        "media_type": "photo" if message.photo else "text",
        "gallery_images": None,
        "is_video": is_video_msg,
        "video_url": None,
        "views": getattr(message, "views", None),
        "forwards": getattr(message, "forwards", None),
        "image_analysis": image_analysis,
        "annotated_image": annotated_image,
        "llm_analysis": llm_result,
        "risk_analysis": {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "confidence": analysis.get("confidence", 0),
            "flags": analysis.get("flags", []),
            "detected_keywords": analysis.get("detected_keywords", []),
            "detected_patterns": analysis.get("detected_patterns", []),
        },
    }

    log_print(
        f"📝 Telegram {idx}/{total}: @{channel_username} msg {message.id} -> {risk_level}"
    )

    return {
        "post_data": post_data,
        "risk_level": risk_level,
        "did_image_analysis": did_image_analysis,
        "weapons_found": weapons_found,
        "did_llm_analysis": did_llm_analysis,
        "is_illegal": is_illegal,
    }


def telegram_client_session_arg(session_path) -> str:
    """TelegramClient first arg: path without .session suffix (absolute)."""
    p = session_path
    if hasattr(p, "with_name"):
        return str(p.with_name(p.stem))
    s = str(p)
    if s.endswith(".session"):
        return s[: -len(".session")]
    return s


def telegram_session_arg_from_config(tg) -> str:
    """Use whichever .session file exists (backend dir, cwd, repo root)."""
    resolved = tg.resolved_session_file()
    path = resolved if resolved is not None else tg.session_path()
    return telegram_client_session_arg(path)
