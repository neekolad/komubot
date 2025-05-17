import sqlite3
import json
from datetime import datetime
import hashlib



def insert_outage(db_path, source, json_data):
    """
    Inserts new outage JSON into DB only if it has changed (based on hash).
    
    Args:
        db_path (str): Path to your SQLite DB
        json_data (list or dict): Parsed outage data
        source (str): Type of outage ('water', etc.)

    Returns:
        int or None: ID of inserted row, or None if duplicate
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Normalize and hash the JSON
        json_string = json.dumps(json_data, ensure_ascii=False, sort_keys=True)
        json_hash = hashlib.sha256(json_string.encode('utf-8')).hexdigest()

        # Check if hash already exists
        cursor.execute("SELECT id FROM outages WHERE json_hash = ?", (json_hash,))
        existing = cursor.fetchone()
        if existing:
            print(f"[SKIPPED] Duplicate data (already in row ID: {existing[0]})")
            return None

        # Insert new row
        cursor.execute("""
            INSERT INTO outages (source, json, json_hash)
            VALUES (?, ?, ?)
        """, (source, json_string, json_hash))
        
        conn.commit()
        return cursor.lastrowid

    except sqlite3.Error as e:
        print(f"[DB ERROR] {e}")
        return None

    finally:
        conn.close()


def load_users(db_path):
    import sqlite3
    import json

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email, telegram_id, phone, keywords FROM users")
    rows = cursor.fetchall()
    conn.close()

    users = []
    for row in rows:
        keywords = row[5]
        try:
            kw_list = json.loads(keywords)
        except:
            kw_list = [kw.strip() for kw in keywords.split(',') if kw.strip()]
        
        users.append({
            'id': row[0],
            'name': row[1],
            'email': row[2],
            'telegram_id': row[3],
            'phone': row[4],
            'keywords': kw_list,
        })
    return users

def was_already_notified(db_path, user_id, outage_id):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 1 FROM notifications_sent
        WHERE user_id = ? AND outage_id = ?
    """, (user_id, outage_id))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def record_notification(db_path, user_id, outage_id, method="email"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR IGNORE INTO notifications_sent (user_id, outage_id, method)
        VALUES (?, ?, ?)
    """, (user_id, outage_id, method))
    conn.commit()
    conn.close()


