import requests
import pprint
from bs4 import BeautifulSoup as bs
import telepot
from dotenv import load_dotenv
import os
import sys
import io
import json

from db.models import insert_outage

# DB_PATH = "komubot_database.db"
DEBUG = True

# Force UTF-8 printing to terminal
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

load_dotenv('.env')

# Teleport telegram information
token = os.getenv("KOMUBOT_TOKEN")
reciever_id = recid = os.getenv("KOMUBOT_RECIEVER_ID")

# Get updates
# 'https://api.telegram.org/bot' + token + '/getUpdates'

def water_scraper(db_path):
    res = requests.get("https://www.bvk.rs/kvarovi-na-mrezi/")
    print(f"Status code:", res.status_code)

    page = bs(res.content, "html.parser")

    with open("water_page.html", "w", encoding="utf-8") as f:
        f.write(page.decode())

    #Selecting div with page content i need
    main = page.select('div[role=tablist]')

    all_data = []

    print("Number of sections in results:", len(main))
    # Looping through sections in main section
    for section in main:

        data = []
        # Defining list items (regions without water)
        outage_date_selector = section.select_one("p")
        if outage_date_selector:
            outage_date = outage_date_selector.text
        else:
            otage_date = '01.01.2000'

        outage_time_selector = section.select_one("h1")
        if outage_time_selector:
            outage_time = outage_time_selector.text
        else:
            outage_time = "00:00"
        
        print(f"Outage date: {outage_date}, Outage time: {outage_time}")

        for li in section.select("ul > li"):
            region = li.select_one("strong").text.replace(":", "").strip()
            address = li.text.replace(region, "").replace(":", "").strip()
            if DEBUG:
                print(f"Region: {region}, address: {address}")

            # push to data list
            data.append({'region' : region, 'address' : [addr for addr in address.split(', ')]})

        all_data.append(
            {
                "date" : outage_date,
                "time" : outage_time,
                "regions" : data
            }
        )
        # outage_id = insert_outage(db_path, "water", all_data)
        return all_data





# Check to see if my region appears
# if "Трстеничка" or "Палилула" in d[date]["region"]:

#     # Start a bot
#     bot = telepot.Bot(token)

#     # Create a message
#     msg = 'ОБАВЕШТЕЊЕ: помињу се улице око тебе, иди на https://www.bvk.rs/kvarovi-na-mrezi/ и провери о чему се ради'

#     # Send a message
#     bot.sendMessage(reciever_id, msg )
    
