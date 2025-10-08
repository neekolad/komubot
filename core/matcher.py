import sqlite3
from datetime import datetime
import json
import sys
import io

# Force UTF-8 printing to terminal
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

class Matcher:

    def __init__(self, db_path):
        self.db_path = db_path

    def connect(self):
        return sqlite3.connect(self.db_path)
    
    def get_outages(self):
        with self.connect() as conn:
            return conn.execute("SELECT id, source, json FROM outages").fetchall()
        
    def get_user_keywords(self):
        with self.connect() as conn:
            return conn.execute("SELECT id, name, email, phone, keywords FROM users").fetchall()
    
    def match_keywords(self, json_data, keywords):
        """
        Returns True if any keyword is found in the outage data.
        """
        haystack = json.dumps(json_data, ensure_ascii=False).lower()
        return any(keyword.lower() in haystack for keyword in keywords)
        
    def match(self):
        outages = self.get_outages()
        users = self.get_user_keywords()

        print(f"outages: {json.dumps(outages, indent=4)}")
        print(f"users: {json.dumps(users, indent=4)}")
        matched = []
        for user_id, name, email, phone, keywords in users:
            for outage_id, source, json_data in outages:
                print(f"json_data: {json_data}\nkeywords: {keywords}")
                if self.match_keywords(json_data, keywords):
                    print("WE GOT A MATCH?")


                # for kw in keywords.split(','):
                #     kw_lower = kw.strip().lower()
                #     if kw_lower in data.lower() or kw_lower in region.lower():
                #         matched.append((user_id, outage_id))
                #         # self.insert_email(user_id, outage_id, email)
                #         print(user_id, outage_id)
                #         break  # avoid duplicates for same outage/user
        return matched
    
    def insert_email(self, user_id, outage_id, email):
        with self.connect() as conn:
            conn.execute("""
                INSERT OR IGNORE INTO email_queue (user_id, outage_id, email, status, created_at)
                VALUES (?, ?, ?, 'pending', ?)
            """, (user_id, outage_id, email, datetime.now().isoformat()))
            conn.commit()