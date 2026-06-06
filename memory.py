import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect("memory.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            role TEXT,
            content TEXT,
            mode TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def save_message(session_id, role, content, mode="general"):
    conn = sqlite3.connect("memory.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO conversations (session_id, role, content, mode) VALUES (?, ?, ?, ?)",
        (session_id, role, content, mode)
    )
    conn.commit()
    conn.close()

def get_history(session_id, limit=10):
    conn = sqlite3.connect("memory.db")
    cursor = conn.cursor()
    cursor.execute(
        """SELECT role, content FROM conversations
           WHERE session_id = ?
           ORDER BY timestamp DESC LIMIT ?""",
        (session_id, limit)
    )
    rows = cursor.fetchall()
    conn.close()
    rows.reverse()
    return [{"role": row[0], "content": row[1]} for row in rows]

def get_full_history(session_id):
    conn = sqlite3.connect("memory.db")
    cursor = conn.cursor()
    cursor.execute(
        """SELECT role, content, mode, timestamp 
           FROM conversations
           WHERE session_id = ?
           ORDER BY timestamp ASC""",
        (session_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [{"role": r[0], "content": r[1], "mode": r[2], "time": r[3]} for r in rows]

def clear_history(session_id):
    conn = sqlite3.connect("memory.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM conversations WHERE session_id = ?", (session_id,))
    conn.commit()
    conn.close()