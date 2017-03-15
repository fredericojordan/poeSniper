import requests
import json
import time

CURRENT_LEAGUE = "Legacy"
API_BASE_URL = "http://api.pathofexile.com/public-stash-tabs"
STARTING_PAGE = "49919976-52967025-49502222-57596848-53578103" # empty string for first page
TOTAL_PAGES = 1
MARKET_PRICES = [{} for _ in range(10)]

UNIQUE_FLASK_PRICES_URL = "http://cdn.poe.ninja/api/Data/GetUniqueFlaskOverview"
CARD_PRICES_URL = "http://api.poe.ninja/api/Data/GetDivinationCardsOverview"
PROPHECY_PRICES_URL = "http://api.poe.ninja/api/Data/GetProphecyOverview"
CURRENCY_PRICES_URL = "http://cdn.poe.ninja/api/Data/GetCurrencyOverview"

class ITEM_TYPES:
    Normal, Magic, Rare, Unique, Gem, Currency, Card, Quest, Prophecy, Relic = range(10)

def getNinjaPrices(url):
    params = {'league': CURRENT_LEAGUE, 'time': time.strftime("%Y-%m-%d")}
    response = requests.get(url, params = params)
    prices = response.json().get('lines')
    return dict( [i.get('name'), float(i.get('chaosValue')) ] for i in prices )	

def getNinjaCurrency(url):
    params = {'league': CURRENT_LEAGUE, 'time': time.strftime("%Y-%m-%d")}
    response = requests.get(url, params = params)
    prices = response.json().get('lines')
    return dict( [i.get('currencyTypeName'), float(i.get('chaosEquivalent')) ] for i in prices )

def getApiPage(page_id=""):
    target = API_BASE_URL
    if (page_id != ""):
        target = target + "?id=" + str(page_id)
       
    request = requests.get(target)
    return request.json()

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

def getItemSellingOffer(item):
    return item["note"].split()

def offer2chaos(offer):
    if "chaos" in offer[2]:
        return float(offer[1])
    
    if "fus" in offer[2]:
        return float(offer[1])*MARKET_PRICES[ITEM_TYPES.Currency]["Orb of Fusing"]
    
    for k,v in MARKET_PRICES[ITEM_TYPES.Currency].items():
        if offer[2].lower() in k.lower():
            return float(float(offer[1])*v)

def getItemSellingPrice(item):
    return offer2chaos(getItemSellingOffer(item))
 
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
    if getItemType(item) == ITEM_TYPES.Card:
        return MARKET_PRICES[ITEM_TYPES.Card][getItemName(item)]
                
def getTradeMessage(stash, item):
    characterName = getCharacterName(stash)
    itemName = getItemName(item)
    price = getItemSellingOffer(item)[1]
    currency = getItemSellingOffer(item)[2]
    league = getItemLeague(item)
    stashName = getStashName(stash)
    w = item.get('w')
    h = item.get('h')
    return '@{} Hi, I would like to buy your {} listed for {} {} in {} (stash tab "{}"; position: left {}, top {})'.format(characterName, itemName, price, currency, league, stashName, w, h)

def findDivDeals(stashes):
    for s in stashes:
        items = s['items']
        
        for i in items:
            if getItemLeague(i) == CURRENT_LEAGUE and getItemType(i) == ITEM_TYPES.Card and isSellingBuyout(i):
                profit = getItemMarketPrice(i) - getItemSellingPrice(i)
                if profit > -5.0:
                    print(getTradeMessage(s, i))


def createStashDumpFile(npages):
	nextPageID = STARTING_PAGE
	StashDump = open('StashDump.txt', 'w')
	for k in range(npages):
		data = getApiPage(nextPageID)
		StashDump.write(data)
		nextPageID = data['next_change_id']
	StashDump.close()
			
			


MARKET_PRICES[ITEM_TYPES.Card].update(getNinjaPrices(CARD_PRICES_URL))
MARKET_PRICES[ITEM_TYPES.Prophecy].update(getNinjaPrices(PROPHECY_PRICES_URL))
MARKET_PRICES[ITEM_TYPES.Unique].update(getNinjaPrices(UNIQUE_FLASK_PRICES_URL))
MARKET_PRICES[ITEM_TYPES.Currency].update(getNinjaCurrency(CURRENCY_PRICES_URL))

# VSZ
data = loadApiPageFromFile('response.txt')
stashes = data['stashes']
findDivDeals(stashes)

# Gets next_page_id from poe.ninja
r = requests.get("http://api.poe.ninja/api/Data/GetStats")
STARTING_PAGE = r.json().get('nextChangeId')

createStashDumpFile(50)

# # FVJ
# dump_file = open('dump.txt', 'w')
# next_page = STARTING_PAGE
#  
# for p in range(TOTAL_PAGES):
#     print("---- Page {} ----".format(p+1))
#  
#     #jPage = getApiPage(next_page)
#     jPage = loadApiPageFromFile('response.txt')
#      
#     stashes = jPage["stashes"]
#     stashes_count = len(stashes)
#      
#     empty_stashes_count = 0
#     total_items_count = 0
#     card_count = 0
#      
#     for s in range(stashes_count):
#         items = stashes[s]["items"]
#         if ( isEmpty(stashes[s]) ):
#             empty_stashes_count += 1
#         else:
#             items = stashes[s]["items"]
#             total_items_count += len(items)
#             for i in range(len(items)):
#                 if (getItemType(items[i]) == ITEM_TYPES.Card and getItemLeague(items[i]) == CURRENT_LEAGUE):
#                     card_count += 1
#                     item_name = getItemName(items[i])
#                      
#                     if isSellingBuyout(items[i]):
#                         #print("{}: {} (~{}c)".format(item_name, ' '.join(getItemSellingOffer(items[i])[1:]), MARKET_PRICES[ITEM_TYPES.Card][item_name]))
#                         print("{}: {} (~{}c)".format(item_name, ' '.join(getItemSellingOffer(items[i])[1:]), offer2chaos(getItemSellingOffer(items[i]))))                    
#                         player_info = stashes[s]
#                         player_info["items"] = []
#                         dump_file.write("{} {}\n".format(player_info, items[i]))
#      
#     print("----")
#     print("This page has {} items on {} stashes and {} empty stashes".format(total_items_count, stashes_count-empty_stashes_count, empty_stashes_count))
#     print("{} divination cards on legacy league".format(card_count))
#      
#     next_page = jPage["next_change_id"]
#     print("Next page: {}".format(next_page))
#  
# dump_file.close()

print("Done!")
