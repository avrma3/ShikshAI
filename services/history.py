"""
SQLite-backed session history for ShikshAI.
Records every teacher action so the Dashboard can show analytics.
"""
import sqlite3
import json
import os
from datetime import datetime

_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "shiksha_sessions.db")
_db_ready = False


def _conn() -> sqlite3.Connection:
    c = sqlite3.connect(_DB)
    c.row_factory = sqlite3.Row
    return c


def init_db() -> None:
    global _db_ready
    if _db_ready:
        return
    with _conn() as db:
        db.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            ts         TEXT    NOT NULL,
            feature    TEXT    NOT NULL,
            topic      TEXT,
            grade      TEXT,
            subject    TEXT,
            data_json  TEXT,
            score_pct  REAL
        )""")
        db.commit()
    _db_ready = True


def save(feature: str, topic: str = "", grade: str = "", subject: str = "",
         data: dict = None, score_pct: float = None) -> None:
    init_db()
    with _conn() as db:
        db.execute(
            "INSERT INTO sessions (ts,feature,topic,grade,subject,data_json,score_pct) "
            "VALUES (?,?,?,?,?,?,?)",
            (
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                feature, topic, grade, subject,
                json.dumps(data or {}),
                score_pct,
            ),
        )
        db.commit()


def recent(limit: int = 25) -> list:
    init_db()
    with _conn() as db:
        rows = db.execute(
            "SELECT id,ts,feature,topic,grade,subject,score_pct "
            "FROM sessions ORDER BY ts DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [dict(r) for r in rows]


def stats() -> dict:
    init_db()
    with _conn() as db:
        total = db.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]

        by_feature = {
            row[0]: row[1]
            for row in db.execute(
                "SELECT feature, COUNT(*) FROM sessions GROUP BY feature"
            ).fetchall()
        }

        avg_score = db.execute(
            "SELECT AVG(score_pct) FROM sessions "
            "WHERE feature='quiz' AND score_pct IS NOT NULL"
        ).fetchone()[0]

        top_topics = db.execute(
            "SELECT topic, COUNT(*) cnt FROM sessions "
            "WHERE topic IS NOT NULL AND topic != '' "
            "GROUP BY topic ORDER BY cnt DESC LIMIT 6"
        ).fetchall()

        # Quiz score distribution (for sparkline)
        scores = db.execute(
            "SELECT score_pct FROM sessions WHERE feature='quiz' AND score_pct IS NOT NULL "
            "ORDER BY ts DESC LIMIT 10"
        ).fetchall()

    return {
        "total": total,
        "by_feature": by_feature,
        "avg_quiz_score": round(avg_score or 0, 1),
        "top_topics": [(r[0], r[1]) for r in top_topics],
        "recent_scores": [r[0] for r in scores],
    }


def clear_all() -> None:
    init_db()
    with _conn() as db:
        db.execute("DELETE FROM sessions")
        db.commit()
