import sqlite3

def init_db(db_path="komubot_database.db"):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS outages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source TEXT NOT NULL,
        json TEXT NOT NULL,
        json_hash TEXT NOT NULL UNIQUE,
        inserted_at TEXT DEFAULT CURRENT_TIMESTAMP,
        processed INT DEFAULT 0
    )""")

    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        phone TEXT,
        keywords TEXT,  -- comma-separated or JSON list like '["Borča", "Звездара"]'
        inserted_at TEXT DEFAULT CURRENT_TIMESTAMP
    )""")

    c.execute("""
        CREATE TABLE IF NOT EXISTS emails_queue (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        outage_id INTEGER,
        email_addr TEXT,
        phone TEXT,
        email_subject TEXT,
        email_body TEXT,
        status TEXT,    -- pending/sent/retry/failed/etc
        inserted_at TEXT DEFAULT CURRENT_TIMESTAMP,
        att_count INT DEFAULT 0,
        processed_at DATETIME,
        sent_at DATETIME,
        UNIQUE(user_id, outage_id)  -- ensures 1 notification per user per outage
    )""")

    conn.commit()
    conn.close()
