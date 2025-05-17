
import json
import sqlite3
from db.models import load_users, was_already_notified, record_notification


def notify_users(db_path, outage_id):
    # Load JSON for this outage
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT json FROM outages WHERE id = ?", (outage_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        print(f"[ERROR] No outage found with ID {outage_id}")
        return

    json_data = json.loads(row[0])
    users = load_users(db_path)

    for user in users:
        if match_keywords(json_data, user['keywords']):
            if was_already_notified(db_path, user['id'], outage_id):
                print(f"[SKIP] Already notified {user['name']} for outage {outage_id}")
                continue

            # Placeholder for actual send
            print(f"[NOTIFY] Would notify {user['name']} via email: {user['email']}")
            
            record_notification(db_path, user['id'], outage_id)

def match_keywords(json_data, keywords):
    """
    Returns True if any keyword is found in the outage data.
    """
    haystack = json.dumps(json_data, ensure_ascii=False).lower()
    return any(keyword.lower() in haystack for keyword in keywords)


