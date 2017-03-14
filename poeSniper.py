import requests
import json
import gzip
import io
import time

CURRENT_LEAGUE = "Legacy"
BASE_SITE = "http://api.pathofexile.com/public-stash-tabs"
#FIRST_PAGE = ""
FIRST_PAGE = "49919976-52967025-49502222-57596848-53578103"
TOTAL_PAGES = 0
    
class FRAME_TYPES:
    Normal, Magic, Rare, Unique, Gem, Currency, Card, Quest, Prophecy, Relic = range(10)
    
def getPrices():
    params = {'league': CURRENT_LEAGUE, 'time': time.strftime("%Y-%m-%d")}
    url_div = "http://api.poe.ninja/api/Data/GetDivinationCardsOverview"
    r = requests.get(url_div, params = params)
    div_prices = r.json().get('lines')
    return dict( [div.get('name'), div.get('chaosValue')] for div in div_prices )
    
def getStashes(id=""):
    target = BASE_SITE
    if (id != ""):
        target = target + "?id=" + str(id)
       
    request = requests.get(target)
    page = str(request._content)
    
    page = page[2:-1]
    page = page.replace("\\'", "'")
    page = page.replace("\\\\", "\\")
    return page
    

div_prices = getPrices()
for k,v in div_prices.items():
    print(str(k) + ": " + str(v))

dump_file = open('dump.txt', 'w')
next_page = FIRST_PAGE

for x in range(TOTAL_PAGES):
    print("---- Page " +  str(x+1) + " ----")

    data = getStashes(next_page)
    
    jPage = json.loads(data)
    stashes = jPage["stashes"]
    stashes_number = len(stashes)
    
    empty_stashes = 0
    total_items_number = 0
    cards = 0
    for i in range(stashes_number):
        items = stashes[i]["items"]
        if (items == []):
            empty_stashes += 1
        else:
            total_items_number += len(items)
            for t in range(len(items)):
                if (items[t]["frameType"] == FRAME_TYPES.Card and items[t]["league"] == CURRENT_LEAGUE):
                    cards += 1
                    player_info = stashes[i]
                    player_info["items"] = []
                    dump_file.write(str(player_info))
                    dump_file.write(str(items[t]))
                    dump_file.write("\n")
    
    print(str(total_items_number) + " items on " + str(stashes_number-empty_stashes) + " stashes")
    print(str(cards) + " divination cards on legacy league")
    
    next_page = jPage["next_change_id"]
    print("Next page: " + next_page)   

dump_file.close()

print("Done!")
