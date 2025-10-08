# match_runner.py
from core.matcher import Matcher
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "komubot_database.db")

if __name__ == "__main__":
    matcher = Matcher(DB_PATH)
    matches = matcher.match()
    print(f"{len(matches)} matches inserted into email_queue.")