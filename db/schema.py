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
        inserted_at TEXT DEFAULT CURRENT_TIMESTAMP
    )""")

    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        telegram_id TEXT,
        phone TEXT,
        keywords TEXT,  -- comma-separated or JSON list like '["Borča", "Звездара"]'
        wants_email INTEGER DEFAULT 1,
        wants_telegram INTEGER DEFAULT 0,
        wants_sms INTEGER DEFAULT 0
    )""")

    c.execute("""
        CREATE TABLE IF NOT EXISTS notifications_sent (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        outage_id INTEGER,
        notified_at TEXT DEFAULT CURRENT_TIMESTAMP,
        method TEXT,  -- 'email', 'telegram', etc.
        UNIQUE(user_id, outage_id)  -- ensures 1 notification per user per outage
    )""")

    conn.commit()
    conn.close()
