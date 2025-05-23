from scraper_water import water_scraper
from db.models import insert_outage
from db.schema import init_db
from notifications import notify_users
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "komubot_database.db")

def main():
    init_db()
    data = water_scraper(DB_PATH)
    outage_id = insert_outage(DB_PATH, "water", data)

    # for now just collect outages
    # if outage_id:
    # if True:     # TEST
    #     notify_users(DB_PATH, outage_id)
    #     notify_users(DB_PATH, 3)    # TEST
    # else:
    #     print("[INFO] No new outage info to notify.")



if __name__ == "__main__":
    main()