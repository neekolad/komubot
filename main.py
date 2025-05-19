from scraper_water import water_scraper
from db.models import insert_outage
from notifications import notify_users


DB_PATH = "komubot_database.db"

def main():
    data = water_scraper(DB_PATH)
    outage_id = insert_outage(DB_PATH, "water", data)

    # if outage_id:
    if True:     # TEST
        # notify_users(DB_PATH, outage_id)
        notify_users(DB_PATH, 3)    # TEST
    else:
        print("[INFO] No new outage info to notify.")



if __name__ == "__main__":
    main()