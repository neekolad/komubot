import requests
import pprint
from bs4 import BeautifulSoup
import telepot
from dotenv import load_dotenv
import os

load_dotenv('token.env')

# Teleport telegram information
token = os.getenv("KOMUBOT_TOKEN")
reciever_id = recid = os.getenv("KOMUBOT_RECIEVER_ID")

# Get updates
# 'https://api.telegram.org/bot' + token + '/getUpdates'

page = requests.get("https://www.bvk.rs/kvarovi-na-mrezi/")
print(page)

soup = BeautifulSoup(page.content, "html.parser")

#Selecting div with page content i need
main = soup.find_all('div', class_='togglecontainer')

# Defining empty dictionary
d={}

# Looping through items in main
for i in main:

    # Defining list items (regions without water)
    list_item = i.find('ul').get_text().strip().replace('\n', ', ')

    # Creating paragraph list where first element is DATE and 
    # second is TIME of water shortage
    par = i.find_all('p')
    date = par[0].get_text()
    d[date] = {}

    # Defining keys in dictionary and pushing data
    d[date]["time"], d[date]["region"] = par[1].get_text(), list_item

    print(d)



# Check to see if my region appears
if "Трстеничка" or "Палилула" in d[date]["region"]:

    # Start a bot
    bot = telepot.Bot(token)

    # Create a message
    msg = 'ОБАВЕШТЕЊЕ: помињу се улице око тебе, иди на https://www.bvk.rs/kvarovi-na-mrezi/ и провери о чему се ради'

    # Send a message
    bot.sendMessage(reciever_id, msg )
    
