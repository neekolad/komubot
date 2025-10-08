import sqlite3
from datetime import datetime


class Matcher:

    def __init__(self, db_path):
        self.db_path = db_path

    def connect(self):
        return sqlite3.connect(self.db_path)
    
    def get_outages(self):
        with self.connect() as conn:
            return conn.execute("SELECT id, description, region FROM outages").fetchall()
        
    def get_user_keywords(self):
        with self.connect() as conn:
            return conn.execute("""
                SELECT users.id, users.email, GROUP_CONCAT(keywords.keyword)
                FROM users
                JOIN keywords ON users.id = keywords.user_id
                GROUP BY users.id
            """).fetchall()
        
    def match(self):
        outages = self.get_outages()
        users = self.get_user_keywords()

        matched = []
        for user_id, email, keywords in users:
            for outage_id, description, region in outages:
                for kw in keywords.split(','):
                    kw_lower = kw.strip().lower()
                    if kw_lower in description.lower() or kw_lower in region.lower():
                        matched.append((user_id, outage_id))
                        self.insert_email(user_id, outage_id, email)
                        break  # avoid duplicates for same outage/user
        return matched
    
    def insert_email(self, user_id, outage_id, email):
        with self.connect() as conn:
            conn.execute("""
                INSERT OR IGNORE INTO email_queue (user_id, outage_id, email, status, created_at)
                VALUES (?, ?, ?, 'pending', ?)
            """, (user_id, outage_id, email, datetime.now().isoformat()))
            conn.commit()