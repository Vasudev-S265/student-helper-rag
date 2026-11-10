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


def log_interaction(session_id: str | None, question:str, answer:str, sources:list[dict])->int:
    with get_conn() as conn:
        cur=conn.execute(
            "INSERT INTO interactions (session_id, question, answer, sources_json) VALUES (?, ?, ?, ?)", 
            (session_id, question, answer, json.dumps(sources))
        )
    return cur.lastrowid


if __name__=="__main__":
    init_db()
    new_id=log_interaction("test_session", "test question", "test answer", [{"source": "x.pdf", "page": 1}])
    print(f"Logged interaction with id: {new_id}")