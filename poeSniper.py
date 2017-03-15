import requests
import json
import time

CURRENT_LEAGUE = "Legacy"
API_BASE_URL = "http://api.pathofexile.com/public-stash-tabs"
STARTING_PAGE = "49919976-52967025-49502222-57596848-53578103" # empty string for first page
TOTAL_PAGES = 1
    
class FRAME_TYPES:
    Normal, Magic, Rare, Unique, Gem, Currency, Card, Quest, Prophecy, Relic = range(10)
    
def getDivinationPrices():
    params = {'league': CURRENT_LEAGUE, 'time': time.strftime("%Y-%m-%d")}
    url_div = "http://api.poe.ninja/api/Data/GetDivinationCardsOverview"
    response = requests.get(url_div, params = params)
    div_prices = response.json().get('lines')
    return dict( [div.get('name'), div.get('chaosValue')] for div in div_prices )
    
def getApiPage(page_id=""):
    target = API_BASE_URL
    if (page_id != ""):
        target = target + "?id=" + str(page_id)
       
    request = requests.get(target)
    page = str(request._content)
    return json.loads(page)

def loadApiPageFromFile(file_name):
    file = open(file_name, 'r', encoding='utf-8')
    text = file.read()
    file.close()
    return json.loads(text)

def getItemCount(stashes):
    count = 0
    for i in range(len(stashes)):
        len(stashes[i]["items"])
    return count
    
def hasPrice(item):
    return "note" in item.keys()
    
def hasBoPrice(item):
    return "note" in item.keys() and item["note"].startswith("~b/o")

def getItemBoPrice(item):
    return item["note"][5:] # if not B/O, will fuck up everything
 
def getItemName(item):
    return item["typeLine"]

def getItemType(item):
    return item["frameType"]
    
def getItemLeague(item):
    return item["league"]

def isEmpty(stash):
    return stash["items"] == []
    
div_prices = getDivinationPrices()

dump_file = open('dump.txt', 'w')
next_page = STARTING_PAGE

for p in range(TOTAL_PAGES):
    print("---- Page " +  str(p+1) + " ----")

    #jPage = getApiPage(next_page)
    jPage = loadApiPageFromFile('response.txt')
    
    stashes = jPage["stashes"]
    stashes_count = len(stashes)
    
    empty_stashes_count = 0
    total_items_count = 0
    card_count = 0
    
    for s in range(stashes_count):
        items = stashes[s]["items"]
        if ( isEmpty(stashes[s]) ):
            empty_stashes_count += 1
        else:
            items = stashes[s]["items"]
            total_items_count += len(items)
            for i in range(len(items)):
                if (getItemType(items[i]) == FRAME_TYPES.Card and getItemLeague(items[i]) == CURRENT_LEAGUE):
                    card_count += 1
                    item_name = getItemName(items[i])
                    
                    if hasBoPrice(items[i]):
                        print("{}: {} ({} chaos)".format(item_name, getItemBoPrice(items[i]), div_prices[item_name]))                    
                        player_info = stashes[s]
                        player_info["items"] = []
                        dump_file.write("{} {}\n".format(player_info, items[i]))
    
    print("----")
    print("This page has {} items on {} stashes and {} empty stashes".format(total_items_count, stashes_count-empty_stashes_count, empty_stashes_count))
    print("{} divination cards on legacy league".format(card_count))
    
    next_page = jPage["next_change_id"]
    print("Next page: {}".format(next_page))

dump_file.close()

print("Done!")
