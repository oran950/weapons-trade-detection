"""
SQLite persistence for background collection jobs (survives server restart and page refresh).
"""
import json
import sqlite3
import threading
from pathlib import Path
from typing import Any, Dict, List, Optional

_DB_LOCK = threading.Lock()
_db_path: Optional[Path] = None


def _backend_root() -> Path:
    return Path(__file__).resolve().parent.parent


def job_db_path() -> Path:
    global _db_path
    if _db_path is None:
        data = _backend_root() / "data"
        data.mkdir(parents=True, exist_ok=True)
        _db_path = data / "jobs.sqlite"
    return _db_path


def init_job_db() -> None:
    with _DB_LOCK:
        conn = sqlite3.connect(job_db_path())
        try:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS collection_jobs (
                    id TEXT PRIMARY KEY,
                    platform TEXT NOT NULL,
                    sources_json TEXT NOT NULL,
                    limit_val INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    progress INTEGER NOT NULL,
                    total INTEGER NOT NULL,
                    phase_message TEXT NOT NULL,
                    summary_json TEXT,
                    error TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS collection_job_posts (
                    job_id TEXT NOT NULL,
                    seq INTEGER NOT NULL,
                    payload_json TEXT NOT NULL,
                    PRIMARY KEY (job_id, seq)
                )
                """
            )
            conn.commit()
        finally:
            conn.close()


def _job_row(job: Any) -> tuple:
    st = job.status
    status_val = st.value if hasattr(st, "value") else str(st)
    return (
        job.id,
        job.platform,
        json.dumps(job.sources, ensure_ascii=False),
        int(job.limit),
        status_val,
        int(job.progress),
        int(job.total),
        job.phase_message or "",
        json.dumps(job.summary, ensure_ascii=False) if job.summary is not None else None,
        job.error,
        job.created_at,
        job.updated_at,
    )


def persist_job_snapshot(job: Any) -> None:
    """Upsert job metadata."""
    init_job_db()
    row = _job_row(job)
    with _DB_LOCK:
        conn = sqlite3.connect(job_db_path())
        try:
            conn.execute(
                """
                INSERT INTO collection_jobs (
                    id, platform, sources_json, limit_val, status, progress, total,
                    phase_message, summary_json, error, created_at, updated_at
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
                ON CONFLICT(id) DO UPDATE SET
                    platform=excluded.platform,
                    sources_json=excluded.sources_json,
                    limit_val=excluded.limit_val,
                    status=excluded.status,
                    progress=excluded.progress,
                    total=excluded.total,
                    phase_message=excluded.phase_message,
                    summary_json=excluded.summary_json,
                    error=excluded.error,
                    updated_at=excluded.updated_at
                """,
                row,
            )
            conn.commit()
        finally:
            conn.close()


def persist_post(job_id: str, seq: int, post: Dict[str, Any]) -> None:
    init_job_db()
    with _DB_LOCK:
        conn = sqlite3.connect(job_db_path())
        try:
            conn.execute(
                """
                INSERT OR REPLACE INTO collection_job_posts (job_id, seq, payload_json)
                VALUES (?,?,?)
                """,
                (job_id, seq, json.dumps(post, ensure_ascii=False)),
            )
            conn.commit()
        finally:
            conn.close()


def load_jobs_into_store(job_store: Any, JobStatus: Any, CollectionJob: Any) -> int:
    """Load all jobs from SQLite into the in-memory store. Returns count loaded."""
    init_job_db()
    path = job_db_path()
    if not path.is_file():
        return 0
    with _DB_LOCK:
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        try:
            rows = conn.execute(
                "SELECT * FROM collection_jobs ORDER BY updated_at DESC"
            ).fetchall()
            posts_by_job: Dict[str, List[Dict]] = {}
            for jid, seq, payload in conn.execute(
                "SELECT job_id, seq, payload_json FROM collection_job_posts ORDER BY job_id, seq"
            ):
                posts_by_job.setdefault(jid, []).append(json.loads(payload))
        finally:
            conn.close()

    loaded = 0
    current_set = False
    for r in rows:
        jid = r["id"]
        posts = posts_by_job.get(jid, [])
        try:
            status = JobStatus(r["status"])
        except ValueError:
            status = JobStatus.FAILED
        summary = json.loads(r["summary_json"]) if r["summary_json"] else None
        job = CollectionJob(
            id=jid,
            platform=r["platform"],
            sources=json.loads(r["sources_json"]),
            limit=int(r["limit_val"]),
            status=status,
            progress=int(r["progress"]),
            total=int(r["total"]),
            phase_message=r["phase_message"] or "",
            posts=posts,
            summary=summary,
            error=r["error"],
            created_at=r["created_at"],
            updated_at=r["updated_at"],
        )
        with job_store._lock:
            job_store._jobs[jid] = job
            if (
                not current_set
                and status
                in (JobStatus.PENDING, JobStatus.COLLECTING, JobStatus.ANALYZING)
            ):
                job_store._current_job_id = jid
                current_set = True
        loaded += 1
    return loaded
