"""
SQLite database manager for GRASP.
Thread-safe connection handling for FastAPI async workers.
"""
import sqlite3
import os
import json
from datetime import datetime
from contextlib import contextmanager
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

DB_PATH = os.getenv('DATABASE_PATH', 'grasp.db')
DB_FULL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), DB_PATH)

def get_connection():
    conn = sqlite3.connect(DB_FULL_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

@contextmanager
def get_db():
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db():
    with get_db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL DEFAULT (datetime('now')),
                source_ip TEXT,
                dest_ip TEXT,
                protocol TEXT,
                bytes_sent REAL DEFAULT 0,
                bytes_recv REAL DEFAULT 0,
                event_type TEXT,
                payload TEXT,
                label TEXT DEFAULT 'benign',
                metadata TEXT DEFAULT '{}'
            );

            CREATE TABLE IF NOT EXISTS anomalies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL DEFAULT (datetime('now')),
                node_id TEXT NOT NULL,
                risk_score REAL NOT NULL,
                attack_type TEXT,
                agent_scores TEXT NOT NULL DEFAULT '{}',
                explanation TEXT,
                resolved INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS agent_scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL DEFAULT (datetime('now')),
                event_id INTEGER,
                node_id TEXT NOT NULL,
                agent_name TEXT NOT NULL,
                score REAL NOT NULL,
                latency_ms REAL DEFAULT 0,
                FOREIGN KEY (event_id) REFERENCES events(id)
            );

            CREATE TABLE IF NOT EXISTS safe_box (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                node_id TEXT NOT NULL UNIQUE,
                quarantined_at TEXT NOT NULL DEFAULT (datetime('now')),
                risk_score REAL NOT NULL,
                reason TEXT,
                agent_scores TEXT DEFAULT '{}',
                status TEXT DEFAULT 'quarantined',
                released_at TEXT
            );

            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL DEFAULT (datetime('now')),
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                metadata TEXT DEFAULT '{}'
            );

            CREATE TABLE IF NOT EXISTS attack_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL DEFAULT (datetime('now')),
                attack_type TEXT NOT NULL,
                target_node TEXT,
                result TEXT DEFAULT '{}',
                agent_scores TEXT DEFAULT '{}',
                risk_score_before REAL,
                risk_score_after REAL
            );

            CREATE INDEX IF NOT EXISTS idx_anomalies_node ON anomalies(node_id);
            CREATE INDEX IF NOT EXISTS idx_agent_scores_node ON agent_scores(node_id);
            CREATE INDEX IF NOT EXISTS idx_safe_box_status ON safe_box(status);
            CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp);
        """)
    print(f"[DB] SQLite database initialized at {DB_FULL_PATH}")

if __name__ == "__main__":
    init_db()
