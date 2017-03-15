import requests
import json
import time

CURRENT_LEAGUE = "Legacy"
API_BASE_URL = "http://api.pathofexile.com/public-stash-tabs"
STARTING_PAGE = "49919976-52967025-49502222-57596848-53578103" # empty string for first page
TOTAL_PAGES = 1
MARKET_PRICES = {}

UNIQUE_FLASK_PRICES_URL = "http://cdn.poe.ninja/api/Data/GetUniqueFlaskOverview"
CARD_PRICES_URL = "http://api.poe.ninja/api/Data/GetDivinationCardsOverview"
PROPHECY_PRICES_URL = "http://api.poe.ninja/api/Data/GetProphecyOverview"

class ITEM_TYPES:
    Normal, Magic, Rare, Unique, Gem, Currency, Card, Quest, Prophecy, Relic = range(10)

def getNinjaPrices(url):
    params = {'league': CURRENT_LEAGUE, 'time': time.strftime("%Y-%m-%d")}
    response = requests.get(url, params = params)
    prices = response.json().get('lines')
    return dict( [i.get('name'), float(i.get('chaosValue')) ] for i in prices )	
    

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
    
def isSelling(item):
    return "note" in item.keys()
    
def isSellingBuyout(item):
    return "note" in item.keys() and item["note"].startswith("~b/o")

def getItemSellingPrice(item):
    return item["note"].split()
 
def getItemName(item):
    return item["typeLine"]

def getItemType(item):
    return item["frameType"]
    
def getItemLeague(item):
    return item["league"]

def getStashName(stash):
    return stash["stash"]

def getCharacterName(stash):
    return stash["lastCharacterName"]

def getAccountName(stash):
    return stash["accountName"]

def isEmpty(stash):
    return stash["items"] == []

def getItemMarketPrice(item):
    return MARKET_PRICES[getItemName(item)]
                
def getTradeMessage(stash, item):
    characterName = getCharacterName(stash)
    itemName = getItemName(item)
    price = item["note"].split()[1]
    currency = item["note"].split()[2]
    league = getItemLeague(item)
    stashName = getStashName(stash)
    w = item.get('w')
    h = item.get('h')
    return '@{} Hi, I would like to buy your {} listed for {} {} in {} (stash tab "{}"; position: left {}, top {})'.format(characterName, itemName, price, currency, league, stashName, w, h)

def findDivDeals(stashes):
    for s in stashes:
        items = s['items']
        
        for i in items:
            if getItemLeague(i) == CURRENT_LEAGUE and getItemType(i) == ITEM_TYPES.Card:
                price = i.get('note')
                
                # Gets items with price, in chaos, b/o only
                if price and ('~b/o' and 'chaos' in price):
                    
                    price = float(price.split()[1])
                    
                    if (getItemMarketPrice(i) - price) > -5.0:
                        print(getTradeMessage(s, i))




MARKET_PRICES.update(getNinjaPrices(CARD_PRICES_URL))
MARKET_PRICES.update(getNinjaPrices(PROPHECY_PRICES_URL))
MARKET_PRICES.update(getNinjaPrices(UNIQUE_FLASK_PRICES_URL))


# VSZ
data = loadApiPageFromFile('response.txt')
stashes = data['stashes']
findDivDeals(stashes)


# FVJ
dump_file = open('dump.txt', 'w')
next_page = STARTING_PAGE

for p in range(TOTAL_PAGES):
    print("---- Page {} ----".format(p+1))

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
                if (getItemType(items[i]) == ITEM_TYPES.Card and getItemLeague(items[i]) == CURRENT_LEAGUE):
                    card_count += 1
                    item_name = getItemName(items[i])
                    
                    if isSellingBuyout(items[i]):
                        print("{}: {} ({} chaos)".format(item_name, ' '.join(getItemSellingPrice(items[i])[1:]), MARKET_PRICES[item_name]))                    
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
