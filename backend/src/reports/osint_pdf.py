"""
OSINT-style academic research PDF reports (ReportLab, no system PDF deps).
"""
from __future__ import annotations

from datetime import datetime, timezone
from io import BytesIO
from typing import Any, Dict, List, Optional, Tuple
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.pdfgen import canvas as pdfcanvas

# Limits to keep single requests bounded
MAX_BODY_CHARS = 14_000
MAX_FIELD_CHARS = 4_000
MAX_LIST_ITEMS = 80
# Multi-session digest: cap rows so PDF stays bounded
MAX_DIGEST_POST_ROWS_TOTAL = 340

TOOL_NAME = "Weapons Trade Detection System"
CLASSIFICATION = "ACADEMIC RESEARCH — SYNTHETIC / OPEN-SOURCE ASSESSMENT"

COLOR_HEADER = HexColor("#1a1a2e")
COLOR_ACCENT_HIGH = HexColor("#c41e3a")
COLOR_ACCENT_MED = HexColor("#b8860b")
COLOR_ACCENT_LOW = HexColor("#2d6a4f")
COLOR_BORDER = HexColor("#333355")
COLOR_SHADE = HexColor("#f4f4f8")


def _truncate(s: Optional[str], max_len: int) -> Tuple[str, bool]:
    if not s:
        return "", False
    t = str(s)
    if len(t) <= max_len:
        return t, False
    return t[: max_len - 80] + "\n\n[Truncated for report length]", True


def _p(text: str) -> str:
    return escape(str(text)) if text else ""


def _risk_color(level: Optional[str]) -> Any:
    if not level:
        return colors.black
    u = level.upper()
    if u in ("HIGH", "CRITICAL"):
        return COLOR_ACCENT_HIGH
    if u == "MEDIUM":
        return COLOR_ACCENT_MED
    return COLOR_ACCENT_LOW


def _footer_canvas(canv: pdfcanvas.Canvas, doc: Any) -> None:
    canv.saveState()
    canv.setFont("Helvetica", 7)
    canv.setFillColor(colors.grey)
    line1 = (
        f"{TOOL_NAME} | Rule-based and optional automated models | "
        "For research only; not operational intelligence."
    )
    line2 = "No warranty of accuracy or completeness."
    canv.drawString(inch * 0.75, 0.52 * inch, line1[:118] + ("…" if len(line1) > 118 else ""))
    canv.drawString(inch * 0.75, 0.42 * inch, line2)
    canv.drawRightString(letter[0] - 0.75 * inch, 0.47 * inch, f"Page {canv.getPageNumber()}")
    canv.restoreState()


def _styles() -> Tuple[Any, ParagraphStyle, ParagraphStyle, ParagraphStyle, ParagraphStyle, ParagraphStyle]:
    base = getSampleStyleSheet()
    h1 = ParagraphStyle(
        name="OSINT_H1",
        parent=base["Heading1"],
        fontSize=16,
        textColor=COLOR_HEADER,
        spaceAfter=10,
        alignment=TA_LEFT,
    )
    h2 = ParagraphStyle(
        name="OSINT_H2",
        parent=base["Heading2"],
        fontSize=11,
        textColor=COLOR_HEADER,
        spaceBefore=14,
        spaceAfter=8,
        borderPadding=4,
    )
    body = ParagraphStyle(
        name="OSINT_Body",
        parent=base["Normal"],
        fontSize=9,
        leading=12,
        textColor=colors.black,
    )
    mono = ParagraphStyle(
        name="OSINT_Mono",
        parent=base["Code"],
        fontName="Courier",
        fontSize=7,
        leading=9,
        textColor=colors.HexColor("#222222"),
    )
    small = ParagraphStyle(
        name="OSINT_Small",
        parent=base["Normal"],
        fontSize=8,
        leading=10,
        textColor=colors.grey,
    )
    return base, h1, h2, body, mono, small


def _table_kv(rows: List[List[str]], col_widths: Optional[List[float]] = None) -> Table:
    t = Table(rows, colWidths=col_widths)
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), COLOR_SHADE),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
                ("GRID", (0, 0), (-1, -1), 0.25, COLOR_BORDER),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return t


def _clip_list(items: List[Any], label: str) -> Tuple[List[str], bool]:
    out: List[str] = []
    truncated = False
    for i, x in enumerate(items[:MAX_LIST_ITEMS]):
        s, _ = _truncate(str(x), MAX_FIELD_CHARS)
        out.append(s)
    if len(items) > MAX_LIST_ITEMS:
        truncated = True
        out.append(f"[{len(items) - MAX_LIST_ITEMS} more {label} omitted]")
    return out, truncated


def _exec_summary_collection(risk: Dict[str, Any], llm: Optional[Dict[str, Any]]) -> str:
    level = str(risk.get("risk_level") or "UNKNOWN").upper()
    score = float(risk.get("risk_score") or 0)
    flags_n = len(risk.get("flags") or [])
    parts = [
        f"Automated assessment indicates {level} risk (score {score:.0%}). "
        f"{flags_n} rule-based indicator(s) recorded.",
    ]
    if llm and llm.get("summary"):
        s, _ = _truncate(str(llm["summary"]), 500)
        parts.append(f"LLM narrative: {s}")
    return " ".join(parts)


def _exec_summary_text(risk_level: str, risk_score: float, summary: str, flags_n: int) -> str:
    return (
        f"Ad-hoc text analysis: {risk_level} risk (score {risk_score:.0%}). "
        f"{flags_n} indicator(s). {summary}"
    )


def build_osint_pdf(payload: Dict[str, Any]) -> bytes:
    """
    Build PDF bytes from a normalized payload dict (from Pydantic .model_dump()).
    report_type: 'collection_item' | 'text_analysis'
    """
    report_type = (payload.get("report_type") or "text_analysis").lower()
    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=letter,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.85 * inch,
        bottomMargin=0.75 * inch,
        title="OSINT Assessment Report",
    )
    _, h1, h2, body, mono, small = _styles()
    story: List[Any] = []

    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    report_id = payload.get("report_id") or f"RPT-{int(datetime.now(timezone.utc).timestamp())}"

    # Banner
    story.append(Paragraph(_p(CLASSIFICATION), small))
    story.append(Spacer(1, 6))
    if report_type == "collection_digest":
        default_title = "Master collection intelligence digest"
    elif report_type == "collection_item":
        default_title = "Collection artifact assessment"
    else:
        default_title = "Text analysis assessment"
    title = payload.get("report_title") or default_title
    story.append(Paragraph(_p(title), h1))
    story.append(Paragraph(_p(f"Report ID: {report_id}  |  Generated: {now_utc}"), small))
    story.append(Spacer(1, 12))

    if report_type == "collection_item":
        _build_collection_story(payload, story, h2, body, mono, small, report_id, now_utc)
    elif report_type == "collection_digest":
        _build_digest_story(payload, story, h2, body, mono, small, report_id, now_utc)
    else:
        _build_text_analysis_story(payload, story, h2, body, mono, small, report_id, now_utc)

    doc.build(story, onFirstPage=_footer_canvas, onLaterPages=_footer_canvas)
    pdf = buf.getvalue()
    buf.close()
    return pdf


def _build_collection_story(
    payload: Dict[str, Any],
    story: List[Any],
    h2: ParagraphStyle,
    body: ParagraphStyle,
    mono: ParagraphStyle,
    small: ParagraphStyle,
    report_id: str,
    now_utc: str,
) -> None:
    ra = payload.get("risk_analysis") or {}
    llm = payload.get("llm_analysis")
    img = payload.get("image_analysis")

    platform = (payload.get("platform") or "?").upper()
    record_id = payload.get("record_id") or payload.get("id") or "—"
    author = payload.get("author_hash") or "—"
    collected = payload.get("collected_at") or "—"
    source_url = payload.get("source_url") or payload.get("url") or ""
    channel = payload.get("channel") or ""
    sub = payload.get("subreddit") or ""
    loc = f"r/{sub}" if sub else (channel or "—")

    content_raw = payload.get("content") or ""
    content, _trunc = _truncate(content_raw, MAX_BODY_CHARS)

    meta_rows = [
        ["Platform", platform],
        ["Source locator", _truncate(loc, 200)[0]],
        ["Record ID", _truncate(str(record_id), 200)[0]],
        ["Author hash", _truncate(str(author), 200)[0]],
        ["Collected (UTC/local as provided)", _truncate(collected, 200)[0]],
        ["Source URL", ""],
    ]
    story.append(Paragraph("<b>Source profile</b>", h2))
    story.append(_table_kv(meta_rows, [1.35 * inch, 4.9 * inch]))
    if source_url:
        url_t, _ = _truncate(source_url, MAX_FIELD_CHARS)
        story.append(Spacer(1, 4))
        story.append(Paragraph(_p(url_t), mono))

    story.append(Spacer(1, 10))
    story.append(Paragraph("<b>Executive summary</b>", h2))
    summary_text = _exec_summary_collection(ra, llm)
    story.append(Paragraph(_p(summary_text), body))

    story.append(Spacer(1, 10))
    story.append(Paragraph("<b>Subject title</b>", h2))
    title_t, _ = _truncate(payload.get("title") or "(no title)", 500)
    story.append(Paragraph(_p(title_t), body))

    story.append(Spacer(1, 8))
    story.append(Paragraph("<b>Source content (excerpt)</b>", h2))
    story.append(Paragraph(_p(content), mono))
    if _trunc:
        story.append(Paragraph(_p("[Body truncated for report length]"), small))

    _append_findings(story, ra, h2, body, mono, small)

    if llm:
        story.append(Paragraph("<b>Automated LLM assessment</b>", h2))
        rows = [
            ["Weapon-related", str(llm.get("is_weapon_related"))],
            ["Trade-related", str(llm.get("is_trade_related"))],
            ["Potentially illegal", str(llm.get("is_potentially_illegal"))],
            ["Risk assessment", str(llm.get("risk_assessment") or "—")],
            ["Recommendation", str(llm.get("recommendation") or "—")],
            ["Confidence", f"{float(llm.get('confidence') or 0):.0%}"],
        ]
        story.append(_table_kv(rows, [1.6 * inch, 4.65 * inch]))
        if llm.get("illegality_reason"):
            story.append(Spacer(1, 6))
            ir, _ = _truncate(str(llm["illegality_reason"]), 1500)
            story.append(Paragraph(f"<b>Illegality reason:</b> {_p(ir)}", body))
        if llm.get("summary"):
            sm, _ = _truncate(str(llm["summary"]), 2000)
            story.append(Spacer(1, 6))
            story.append(Paragraph(f"<b>Summary:</b> {_p(sm)}", body))
        wt = llm.get("weapon_types_mentioned") or []
        ti = llm.get("trade_indicators") or []
        if wt:
            story.append(Spacer(1, 6))
            story.append(Paragraph("<b>Weapon types mentioned</b>", body))
            for line in _clip_list(wt, "items")[0][:25]:
                story.append(Paragraph(f"• {_p(line)}", body))
        if ti:
            story.append(Spacer(1, 6))
            story.append(Paragraph("<b>Trade indicators</b>", body))
            for line in _clip_list(ti, "items")[0][:25]:
                story.append(Paragraph(f"• {_p(line)}", body))

    if img:
        story.append(Paragraph("<b>Visual intelligence (textual)</b>", h2))
        notes = img.get("analysis_notes") or ""
        irisk = str(img.get("overall_risk") or "—")
        wc = img.get("weapon_count")
        cw = img.get("contains_weapons")
        img_rows = [
            ["Contains weapons (model)", str(cw)],
            ["Weapon count", str(wc if wc is not None else "—")],
            ["Overall risk", irisk],
        ]
        story.append(_table_kv(img_rows, [2 * inch, 4.25 * inch]))
        if notes:
            n, _ = _truncate(str(notes), 2000)
            story.append(Spacer(1, 6))
            story.append(Paragraph(_p(n), body))
        story.append(Paragraph(_p("Annotated imagery not embedded in this report format."), small))


def _build_text_analysis_story(
    payload: Dict[str, Any],
    story: List[Any],
    h2: ParagraphStyle,
    body: ParagraphStyle,
    mono: ParagraphStyle,
    small: ParagraphStyle,
    report_id: str,
    now_utc: str,
) -> None:
    source_text = payload.get("source_text") or ""
    text, _trunc = _truncate(source_text, MAX_BODY_CHARS)
    ctx = payload.get("context_title") or "Ad-hoc text sample"

    story.append(Paragraph("<b>Context</b>", h2))
    story.append(Paragraph(_p(ctx), body))
    story.append(Spacer(1, 8))
    story.append(Paragraph("<b>Submitted text (excerpt)</b>", h2))
    story.append(Paragraph(_p(text), mono))
    if _trunc:
        story.append(Paragraph(_p("[Text truncated for report length]"), small))

    ra = {
        "risk_score": float(payload.get("risk_score") or 0),
        "risk_level": payload.get("risk_level") or "LOW",
        "confidence": float(payload.get("confidence") or 0),
        "flags": payload.get("flags") or [],
        "detected_keywords": payload.get("detected_keywords") or [],
        "detected_patterns": payload.get("detected_patterns") or [],
    }
    story.append(Spacer(1, 10))
    story.append(Paragraph("<b>Executive summary</b>", h2))
    es = _exec_summary_text(
        str(ra["risk_level"]),
        float(ra["risk_score"]),
        str(payload.get("summary") or ""),
        len(ra["flags"]),
    )
    story.append(Paragraph(_p(es), body))
    story.append(Spacer(1, 6))
    story.append(Paragraph(_p(f"Analysis ID: {payload.get('analysis_id') or '—'}"), small))

    _append_findings(story, ra, h2, body, mono, small)


def _append_findings(
    story: List[Any],
    ra: Dict[str, Any],
    h2: ParagraphStyle,
    body: ParagraphStyle,
    mono: ParagraphStyle,
    small: ParagraphStyle,
) -> None:
    story.append(Paragraph("<b>Technical findings</b>", h2))
    level = str(ra.get("risk_level") or "LOW")
    score = float(ra.get("risk_score") or 0)
    conf = float(ra.get("confidence") or 0)
    color = _risk_color(level)
    findings_rows = [
        ["Risk level", level],
        ["Risk score", f"{score:.0%}"],
        ["Confidence", f"{conf:.0%}"],
    ]
    t = _table_kv(findings_rows, [1.35 * inch, 4.9 * inch])
    t.setStyle(
        TableStyle(
            [
                ("TEXTCOLOR", (1, 0), (1, 0), color),
            ]
        )
    )
    story.append(t)

    for label, key in [
        ("Indicators / flags", "flags"),
        ("Detected keywords", "detected_keywords"),
        ("Detected patterns", "detected_patterns"),
    ]:
        items = ra.get(key) or []
        if not items:
            continue
        story.append(Spacer(1, 8))
        story.append(Paragraph(f"<b>{_p(label)}</b>", body))
        clipped, _ = _clip_list(list(items), label.lower())
        for line in clipped:
            story.append(Paragraph(f"• {_p(line)}", mono))


def _digest_post_table_data(posts: List[Dict[str, Any]]) -> List[List[str]]:
    rows: List[List[str]] = [["Record", "Title", "Plt", "Risk", "%", "Ill", "URL"]]
    for p in posts:
        ra = p.get("risk_analysis") or {}
        level = str(ra.get("risk_level") or "—")[:8]
        score = ra.get("risk_score")
        try:
            pct = f"{float(score) * 100:.0f}" if score is not None else "—"
        except (TypeError, ValueError):
            pct = "—"
        llm = p.get("llm_analysis") or {}
        ill = "Y" if llm.get("is_potentially_illegal") else ""
        pid = str(p.get("id") or "")[:12]
        title, _ = _truncate(str(p.get("title") or "(no title)"), 64)
        plat = str(p.get("platform") or "")[:4].upper()
        url, _ = _truncate(str(p.get("url") or ""), 42)
        rows.append([pid, title, plat, level, pct, ill, url])
    return rows


def _append_post_grid(
    story: List[Any],
    posts: List[Dict[str, Any]],
    mono: ParagraphStyle,
) -> None:
    if not posts:
        return
    data = _digest_post_table_data(posts)
    col_w = [0.72 * inch, 2.05 * inch, 0.38 * inch, 0.52 * inch, 0.38 * inch, 0.32 * inch, 2.28 * inch]
    t = Table(data, colWidths=col_w, repeatRows=1)
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), COLOR_HEADER),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 7),
                ("FONTSIZE", (0, 1), (-1, -1), 6),
                ("FONTNAME", (0, 1), (-1, -1), "Courier"),
                ("GRID", (0, 0), (-1, -1), 0.2, COLOR_BORDER),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 3),
                ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, COLOR_SHADE]),
            ]
        )
    )
    story.append(t)


def _build_digest_story(
    payload: Dict[str, Any],
    story: List[Any],
    h2: ParagraphStyle,
    body: ParagraphStyle,
    mono: ParagraphStyle,
    small: ParagraphStyle,
    report_id: str,
    now_utc: str,
) -> None:
    stats = payload.get("aggregate_stats") or {}
    sessions = payload.get("sessions") or []
    standalone = payload.get("standalone_posts") or []
    job_summary = payload.get("job_summary") or {}
    job_meta = payload.get("job_meta") or {}

    story.append(Paragraph("<b>Scope</b>", h2))
    story.append(
        Paragraph(
            _p(
                "Consolidated digest of recorded collection sessions and detections retained in the "
                "application workspace (academic research context)."
            ),
            body,
        )
    )
    story.append(Spacer(1, 8))

    story.append(Paragraph("<b>Workspace statistics</b>", h2))
    stat_rows = [
        ["Posts analyzed (cached)", str(stats.get("totalAnalyzed", stats.get("total_analyzed", "—")))],
        ["High risk count", str(stats.get("highRiskCount", stats.get("high_risk_count", "—")))],
        ["Medium risk count", str(stats.get("mediumRiskCount", stats.get("medium_risk_count", "—")))],
        ["Low risk count", str(stats.get("lowRiskCount", stats.get("low_risk_count", "—")))],
        ["Platforms monitored", str(stats.get("platformsMonitored", stats.get("platforms_monitored", "—")))],
    ]
    story.append(_table_kv(stat_rows, [1.85 * inch, 4.4 * inch]))

    if job_summary or job_meta:
        story.append(Spacer(1, 10))
        story.append(Paragraph("<b>Latest background collection run</b>", h2))
        if job_meta:
            meta_rows = [
                ["Job ID", str(job_meta.get("id") or "—")],
                ["Platform", str(job_meta.get("platform") or "—").upper()],
                ["Status", str(job_meta.get("status") or "—")],
                ["Sources", _truncate(", ".join(job_meta.get("sources") or []), 200)[0]],
            ]
            story.append(_table_kv(meta_rows, [1.1 * inch, 5.15 * inch]))
        if job_summary:
            jr = [
                ["Total scanned / collected", str(job_summary.get("total_scanned") or job_summary.get("total_collected") or "—")],
                ["High risk", str(job_summary.get("high_risk_count", "—"))],
                ["Medium risk", str(job_summary.get("medium_risk_count", "—"))],
                ["Low risk", str(job_summary.get("low_risk_count", "—"))],
                ["Filtered", str(job_summary.get("filtered_out", "—"))],
            ]
            story.append(Spacer(1, 6))
            story.append(_table_kv(jr, [1.85 * inch, 4.4 * inch]))
            hint = job_summary.get("hint")
            if hint:
                story.append(Spacer(1, 6))
                story.append(Paragraph(_p(str(hint)), small))

    total_sessions = len(sessions)
    total_posts_all = sum(len(s.get("posts") or []) for s in sessions) + len(standalone)
    story.append(Spacer(1, 10))
    story.append(Paragraph("<b>Inventory</b>", h2))
    story.append(
        Paragraph(
            _p(
                f"Sessions in this export: {total_sessions}. "
                f"Post rows (all sources): {total_posts_all}. "
                f"Table rows capped at {MAX_DIGEST_POST_ROWS_TOTAL}; remainder omitted if exceeded."
            ),
            small,
        )
    )

    remaining = MAX_DIGEST_POST_ROWS_TOTAL
    truncated_any = False

    for si, session in enumerate(sessions):
        if remaining <= 0:
            truncated_any = True
            break
        posts = list(session.get("posts") or [])
        if not posts and not (session.get("sources") or session.get("timestamp")):
            continue
        story.append(Spacer(1, 12))
        story.append(Paragraph(_p(f"Session {si + 1}: {str(session.get('platform', '?')).upper()}"), h2))
        sess_rows = [
            ["Session ID", str(session.get("id") or "—")[:40]],
            ["Timestamp", str(session.get("timestamp") or "—")],
            ["Sources", _truncate(", ".join(session.get("sources") or []), 220)[0]],
            ["Totals H/M/L", f"{session.get('high_risk', '?')}/{session.get('medium_risk', '?')}/{session.get('low_risk', '?')}"],
            ["Posts in session", str(len(posts))],
        ]
        story.append(_table_kv(sess_rows, [1.15 * inch, 5.1 * inch]))
        if posts:
            chunk = posts[:remaining]
            _append_post_grid(story, chunk, mono)
            if len(posts) > len(chunk):
                truncated_any = True
            remaining -= len(chunk)

    if standalone and remaining > 0:
        story.append(Spacer(1, 14))
        story.append(Paragraph("<b>Detections not tied to a saved session</b>", h2))
        story.append(
            Paragraph(
                _p(
                    "These items exist in the live workspace (e.g. current dashboard pipeline) but were not "
                    "matched to a session snapshot by record ID."
                ),
                small,
            )
        )
        story.append(Spacer(1, 6))
        chunk = standalone[:remaining]
        _append_post_grid(story, chunk, mono)
        if len(standalone) > len(chunk):
            truncated_any = True
        remaining -= len(chunk)

    if truncated_any or (total_posts_all > MAX_DIGEST_POST_ROWS_TOTAL):
        story.append(Spacer(1, 10))
        story.append(
            Paragraph(
                _p(
                    "[Row cap applied: increase resolution by exporting individual artifacts, "
                    "or filter collections before export.]"
                ),
                small,
            )
        )
