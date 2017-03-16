import requests
import json
import time

CURRENT_LEAGUE = "Legacy"
API_BASE_URL = "http://api.pathofexile.com/public-stash-tabs"
STARTING_PAGE = "49919976-52967025-49502222-57596848-53578103" # empty string for first page
TOTAL_PAGES = 50
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
       
    response = requests.get(target)
    
    if response.status_code == 200:
        data = response.json()
        with open('lastresponse.txt', 'w') as outfile:
            json.dump(data, outfile)
            outfile.close()
        return data
    else:
        raise ConnectionError('API request returned status code {}: {}!'.format(response.status_code, response.reason))

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
    return "note" in item.keys() and item['note'].startswith("~b/o")

def getItemSellingOffer(item):
    return item['note'].split()

def offer2chaos(offer):
    if "chaos" in offer[2]:
        return eval(offer[1])
        #return float(offer[1])
    
    if "fus" in offer[2]:
        return  float(eval(offer[1]))*MARKET_PRICES[ITEM_TYPES.Currency]["Orb of Fusing"]
    
    for k,v in MARKET_PRICES[ITEM_TYPES.Currency].items():
        if offer[2].lower() in k.lower():
            return float(eval(offer[1])*v)

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
        if getItemName(item) in MARKET_PRICES[ITEM_TYPES.Card]:
            return MARKET_PRICES[ITEM_TYPES.Card][getItemName(item)]
        else:
            print('Item not in price List! ' + getItemName(item))
            return 9999.0

                
def getTradeInGameMessage(stash, item):
    characterName = getCharacterName(stash)
    itemName = getItemName(item)
    price = getItemSellingOffer(item)[1]
    currency = getItemSellingOffer(item)[2]
    league = getItemLeague(item)
    stashName = getStashName(stash)
    w = item.get('w')
    h = item.get('h')
    return '@{} Hi, I would like to buy your {} listed for {} {} in {} (stash tab "{}"; position: left {}, top {})'.format(characterName, itemName, price, currency, league, stashName, w, h)

def getTradeInfoMessage(profit, item):
	investment = getItemSellingPrice(item)
	roi = profit/float(investment)
	return '[Item Found! Investment: {} / Profit: {} / ROI: {}] '.format(investment, profit, str(roi))

def findDivDeals(stashes):
    for s in stashes:
        items = s['items']
        for i in items:
            if getItemLeague(i) == CURRENT_LEAGUE and getItemType(i) == ITEM_TYPES.Card and isSellingBuyout(i):
                #print(getItemName(i))
                profit =  getProfitMargin(i)
                if profit > 3.0:
                    outputText = getTradeInfoMessage(profit, i) + getTradeInGameMessage(s, i)
                    print(outputText)
                


def createStashDumpFile(npages, starting_page=STARTING_PAGE):
    nextPageID = starting_page
    StashDump = open('StashDump.txt', 'w')
    for _ in range(npages):
        data = getApiPage(nextPageID)
        StashDump.write(data)
        nextPageID = data['next_change_id']
    StashDump.close()

def getNinjaNextPageId():
    response = requests.get("http://api.poe.ninja/api/Data/GetStats")
    return response.json().get('nextChangeId')

def getProfitMargin(item):
    return getItemMarketPrice(item) - getItemSellingPrice(item)


MARKET_PRICES[ITEM_TYPES.Card].update(getNinjaPrices(CARD_PRICES_URL))
MARKET_PRICES[ITEM_TYPES.Prophecy].update(getNinjaPrices(PROPHECY_PRICES_URL))
MARKET_PRICES[ITEM_TYPES.Unique].update(getNinjaPrices(UNIQUE_FLASK_PRICES_URL))
MARKET_PRICES[ITEM_TYPES.Currency].update(getNinjaCurrency(CURRENCY_PRICES_URL))

#data = loadApiPageFromFile('response.txt')

for k,v in MARKET_PRICES[ITEM_TYPES.Card].items():
	print(str(k) + ': ' + str(v))


#createStashDumpFile(TOTAL_PAGES, getNinjaNextPageId())
print('Starting sniper')
next_change_id = getNinjaNextPageId()
for k in range(9999):
	data = getApiPage(next_change_id)
	stashes = data['stashes']
	findDivDeals(stashes)
	next_change_id = data['next_change_id']
	time.sleep(1)
	print('Page #' + str(k+1))

print("Done!")
