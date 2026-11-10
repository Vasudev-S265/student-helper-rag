import json
import sqlite3
from pathlib import Path

DB_PATH=Path(__file__).resolve().parents[2]/"data"/"feedback.db"

def get_conn():
    conn=sqlite3.connect(DB_PATH)
    conn.row_factory=sqlite3.Row
    return conn

def init_db():
    with get_conn() as conn:
        conn.executescript("""
                CREATE TABLE IF NOT EXISTS interactions(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                sources_json TEXT NOT NULL,
                model TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS feedback(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                interaction_id INTEGER NOT NULL REFERENCES interactions(id),
                rating INTEGER NOT NULL,
                comment TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

                """)


def log_interaction(session_id: str | None, question:str, answer:str, sources:list[dict], model:str)->int:
    with get_conn() as conn:
        cur=conn.execute(
            "INSERT INTO interactions (session_id, question, answer, sources_json, model) VALUES (?, ?, ?, ?, ?)", 
            (session_id, question, answer, json.dumps(sources), model),
        )
    return cur.lastrowid

def log_feedback(interaction_id:int, rating:int , comment:str | None)->bool:
    with get_conn() as conn:
        exists=conn.execute(
            "SELECT 1 FROM interactions WHERE id=?", (interaction_id,)
        ).fetchone()

        if not exists:
            return False

        conn.execute(
            "INSERT INTO feedback (interaction_id, rating, comment ) VALUES(?, ?, ?)", (interaction_id, rating, comment),
        )

    return True