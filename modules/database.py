"""
Database Module
Persists resume analysis records and user history locally using SQLite.
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Any


DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "resume_history.db")


def init_db(db_path: str = DB_PATH) -> None:
    """Initializes the SQLite database and ensures the schema is created."""
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analysis_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_name TEXT,
            email TEXT,
            phone TEXT,
            resume_score INTEGER,
            top_job_match TEXT,
            top_match_percent REAL,
            skills_count INTEGER,
            skills_preview TEXT,
            file_name TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()


def save_analysis(
    candidate_name: str,
    email: str,
    phone: str,
    resume_score: int,
    top_job_match: str,
    top_match_percent: float,
    skills_count: int,
    skills_preview: str,
    file_name: str,
    db_path: str = DB_PATH
) -> int:
    """Saves a single analysis record to SQLite."""
    init_db(db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO analysis_history (
            candidate_name, email, phone, resume_score,
            top_job_match, top_match_percent, skills_count,
            skills_preview, file_name, timestamp
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        candidate_name or "Anonymous",
        email or "N/A",
        phone or "N/A",
        resume_score,
        top_job_match or "General",
        round(float(top_match_percent), 1),
        skills_count,
        skills_preview or "",
        file_name or "Uploaded Resume",
        ts
    ))
    record_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return record_id


def get_history(limit: int = 20, db_path: str = DB_PATH) -> List[Dict[str, Any]]:
    """Retrieves previous analysis records ordered by newest first."""
    init_db(db_path)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, candidate_name, email, phone, resume_score,
               top_job_match, top_match_percent, skills_count,
               skills_preview, file_name, timestamp
        FROM analysis_history
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()
    history = [dict(row) for row in rows]
    conn.close()
    return history


def clear_history(db_path: str = DB_PATH) -> None:
    """Clears all records in the analysis history table."""
    init_db(db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM analysis_history")
    conn.commit()
    conn.close()
