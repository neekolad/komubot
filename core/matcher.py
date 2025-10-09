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
            return conn.execute("SELECT id, source, json FROM outages WHERE processed=0").fetchall()
        
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
        for outage_id, source, json_data in outages:
            for user_id, name, email, phone, keywords in users:
                # print(f"json_data: {json_data}\nkeywords: {keywords}")    #debug
                if self.match_keywords(json_data, keywords):
                    # print("WE GOT A MATCH")     # debug

                    # gather information needed, insert email into emails_queue, set outage processed 1
                    # user_id, outage_id, email, phone, email_subject, email_body, status (pending)
                    email_subject = "Komubot obavestenje"   # in the future maybe set APP_NAME + notification
                    email_body = self.make_message(json_data, keywords.split(","))
                    # data = [user_id, outage_id, email, phone, email_subject, email_body, "pending"]
                    # print(json.dumps(data, indent=4))   # debug

                    # insert into emails_queue
                    email_queue = self.insert_email(user_id, outage_id, email, phone, email_subject, email_body, status="pending")
                    if email_queue:
                        print(f"Inserted mail for user_id {user_id} outage_id {outage_id}")
                        matched.append((user_id, outage_id))

            # set outage processed
            outage_processed = self.set_outage_processed(outage_id)
            if outage_processed:
                print(f"Succesfully set processed=1 user_id for outage_id {outage_id}")
        return matched
    

    def insert_email(self, user_id, outage_id, email, phone, email_subject, email_body, status):
        try:
            with self.connect() as conn:
                conn.execute("""
                    INSERT INTO emails_queue (user_id, outage_id, email_addr, phone, email_subject, email_body, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (user_id, outage_id, email, phone, email_subject, email_body, status))
                conn.commit()
            return True
        except Exception as e:
            print(f"Failed to insert record into emails_queue (user_id {user_id}, outage_id {outage_id}): {e}")
            return False
        

    def set_outage_processed(self, outage_id):
        print("OUTAGE ID:", outage_id)
        try:
            with self.connect() as conn:
                conn.execute("""
                    UPDATE outages SET processed=1 WHERE id=?
                """, (outage_id,))
            return True
        except Exception as e:
            print(f"Failed to set outage processed=1 for outage_id {outage_id}: {e}")
            return False


    def make_message(self, json, keywords):
        today = datetime.now()
        day = today.strftime("%d")
        month = today.strftime("%B")
        year = today.strftime("%Y")
        the_time = today.strftime("%H:%M:%S")

        body = self.msg_text(json, keywords)

        message = f"""
            <html>
            <body>
                <h1 style="color:gray;">{body}</h1>
                <br>
                <hr>
                <p style="font-size:14px; color:gray;">Poslato: {day}. {month} {year} - {the_time}</p>
            </body>
            </html>
            """
        return message
    
    
    def msg_text(self, json_data, keywords):
        haystack = json.dumps(json_data, ensure_ascii=False).lower()
        # print(json_data)
        print(keywords)
        outage_regions = []
        for lst in json.loads(json_data):
            for item in lst['regions']:
                dt = lst['date']
                tm = lst['time']
                # print(item['region'])
                for kw in keywords:
                    # print(f"now checking {item['region'].lower()} with {kw.lower()}")     # debug
                    if item['region'].lower() == kw.lower().strip():
                        print(item['region'], 'found keyword', kw)
                        outage_regions.append(f"{item['region']} - {', '.join([i for i in item['address']])}")
        msg = f"Hey, there will be a water outage in your region on {dt} ({tm}) :\n{', '.join(outage_regions)}"
        # print(msg)    # debug
        return msg
    
