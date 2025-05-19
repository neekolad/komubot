
import json
import sqlite3
from email.message import EmailMessage
import subprocess
import time
import os
from datetime import datetime
from dotenv import load_dotenv
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
            # if was_already_notified(db_path, user['id'], outage_id):  # TEST, uncomment this block of code for LIVE
            #     print(f"[SKIP] Already notified {user['name']} for outage {outage_id}")
            #     continue

            # Placeholder for actual send
            print(f"[NOTIFY] Would notify {user['name']} via email: {user['email']}")
            message = make_message(json_data, user['keywords'])
            subject = "Nestanak vode"
            email = user['email']
            send_mail(message, subject, email)
            
            # record_notification(db_path, user['id'], outage_id)

def match_keywords(json_data, keywords):
    """
    Returns True if any keyword is found in the outage data.
    """
    haystack = json.dumps(json_data, ensure_ascii=False).lower()
    return any(keyword.lower() in haystack for keyword in keywords)

def make_message(json, keywords):
    today = datetime.now()
    day = today.strftime("%d")
    month = today.strftime("%B")
    year = today.strftime("%Y")
    the_time = today.strftime("%H:%M:%S")

    body = msg_text(json, keywords)

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

def msg_text(json_data, keywords):
    haystack = json.dumps(json_data, ensure_ascii=False).lower()
    # print(haystack)
    # print(type(haystack))
    msg = "Test mail"
    return msg

def send_mail(message, subject, recipient=None):
    # techo(f"RECEPIENTS: {recipients}")
    if recipient is None:
        raise Exception("No recepients were passed to a function!")
    
    load_dotenv()

    sender_name = os.getenv('EMAIL_SENDER_NAME', 'Homeserver')
    sender_address = os.getenv('EMAIL_SENDER_ADDRESS')
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = f'{sender_name} <{sender_address}>'
    msg['To'] = recipient
    msg.add_alternative(f"{message}", subtype='html')

    try:
        # Send message using msmtp
        process = subprocess.Popen(
            ['msmtp', '-a', 'gmail', msg['To']],
            stdin=subprocess.PIPE,
        )
        process.communicate(msg.as_bytes())
    except Exception as e:
        print(f"Failed to send to {recipient}: {e}")
    time.sleep(2)