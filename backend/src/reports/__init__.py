"""PDF helpers — ReportLab is imported only when PDF export runs (app can start without it)."""

from __future__ import annotations

from typing import Any, Dict


def build_osint_pdf(payload: Dict[str, Any]) -> bytes:
    from .osint_pdf import build_osint_pdf as _build

    return _build(payload)


__all__ = ["build_osint_pdf"]
