# app/main/db.py
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[2] / "app" / "data" / "aromas.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            tipo TEXT NOT NULL,
            precio REAL NOT NULL CHECK(precio>=0),
            stock INTEGER NOT NULL DEFAULT 0 CHECK(stock>=0)
        )
    """)
    conn.commit()
    conn.close()