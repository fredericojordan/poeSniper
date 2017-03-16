import requests
import json
import time
import re
import winsound
import base64

PLAY_SOUNDS = True
MIN_PROFIT = -100.0
MIN_ROI = 0.000000001

CURRENT_LEAGUE = "Legacy"

API_BASE_URL = "http://api.pathofexile.com/public-stash-tabs"
UNIQUE_FLASK_PRICES_URL = "http://cdn.poe.ninja/api/Data/GetUniqueFlaskOverview"
CARD_PRICES_URL = "http://api.poe.ninja/api/Data/GetDivinationCardsOverview"
PROPHECY_PRICES_URL = "http://api.poe.ninja/api/Data/GetProphecyOverview"
CURRENCY_PRICES_URL = "http://cdn.poe.ninja/api/Data/GetCurrencyOverview"

MARKET_PRICES = [{} for _ in range(10)]

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
        dumpToFile(data, 'lastresponse.txt')
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

def isOfferValid(item):
    hasNote = "note" in item.keys() and item['note'].startswith('~')
    if hasNote:
        offer = getItemSellingOffer(item)
        hasPrice = offer[0].startswith("~b/o") or offer[0].startswith("~price")
        priceIsNotNull = eval(offer[1]) > 0.0
    
    conditions = hasNote and hasPrice and priceIsNotNull
    return conditions

def getItemSellingOffer(item):
    print(item['note'])
    o = re.split(r'(\~*\s*)(\d+(?:\.\d+)?(?:\/\d+)?)(\W*)', item['note'])
    return [o[0], o[2], o[4]]

def offer2chaos(offer):
    quantity = float(eval(offer[1]))
    
    if "chaos" in offer[2]:
        return quantity
    
    if "fus" in offer[2]:
        return  quantity*MARKET_PRICES[ITEM_TYPES.Currency]["Orb of Fusing"]
    
    if "gcp" in offer[2]:
        return  quantity*MARKET_PRICES[ITEM_TYPES.Currency]["Gemcutter's Prism"]
    
    for currency,value in MARKET_PRICES[ITEM_TYPES.Currency].items():
        if offer[2].lower() in currency.lower():
            return quantity*value

def getItemSellingPrice(item):
    return offer2chaos(getItemSellingOffer(item))
 

def getItemTypeLine(item):
    return item["typeLine"]

def getItemName(item):
    name = re.sub(r'<<.*>>', '', item['name'])
    return name

def getItemType(item):
    return item["frameType"]
    
def getItemLeague(item):
    return item["league"]

def isFlask(item):
    return 'Flask' in getItemTypeLine(item)

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
        if getItemTypeLine(item) in MARKET_PRICES[ITEM_TYPES.Card]:
            return MARKET_PRICES[ITEM_TYPES.Card][getItemTypeLine(item)]
            
    if getItemType(item) == ITEM_TYPES.Unique and isFlask(item):
        if getItemName(item) in MARKET_PRICES[ITEM_TYPES.Unique]:
            return MARKET_PRICES[ITEM_TYPES.Unique][getItemName(item)]
        else:
            print('Item not in price list! ' + getItemName(item))
            return 9999.0
                
def getTradeInGameMessage(stash, item):
    characterName = getCharacterName(stash)
    itemName = getItemName(item)
    if itemName:
        itemName += ' '
    itemTypeLine = getItemTypeLine(item)
    price = getItemSellingOffer(item)[1]
    currency = getItemSellingOffer(item)[2]
    league = getItemLeague(item)
    stashName = getStashName(stash)
    w = item.get('w')
    h = item.get('h')
    return '@{} Hi, I would like to buy your {}{} listed for {} {} in {} (stash tab "{}"; position: left {}, top {})'.format(characterName, itemName, itemTypeLine, price, currency, league, stashName, w, h)

def getTradeInfoMessage(item):
    investment = getItemSellingPrice(item)
    profit = getProfitMargin(item)
    roi = getROI(item)
    return '[Item Found! Investment: {:.1f}c / Profit: {:.1f}c / ROI: {:.2%}]'.format(investment, profit, roi)

def findDeals(stashes):
    for s in stashes:
        items = s['items']
        for i in items:
            if getItemLeague(i) == CURRENT_LEAGUE and isOfferValid(i):
                
                # Divination Cards
                if getItemType(i) == ITEM_TYPES.Card:
                    if getProfitMargin(i) >= MIN_PROFIT and getROI(i) >= MIN_ROI:
                        outputText = getTradeInfoMessage(i) + ' ' + getTradeInGameMessage(s, i)
                        print(outputText)
            
                # UniqueFlasks
                if getItemType(i) == ITEM_TYPES.Unique and 'Flask' in getItemTypeLine(i):
                    if getProfitMargin(i) >= MIN_PROFIT and getROI(i) >= MIN_ROI:
                        outputText = getTradeInfoMessage(i) + getTradeInGameMessage(s, i)
                        print(outputText)

def createStashDumpFile(npages, starting_page=""):
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

def getROI(item):
    if getItemSellingPrice(item) == 0:
        return 9999.0
    return getProfitMargin(item)/getItemSellingPrice(item)

def soundAlert():
    if (PLAY_SOUNDS):
        winsound.PlaySound('SystemHand', winsound.SND_ALIAS)

def dumpToFile(data, filename):
    with open(filename, 'w') as outfile:
        json.dump(data, outfile)
        outfile.close()
        
def splashScreen():
    print(base64.b64decode('X19fX19fX19fXyAgICAgX19fX19fX19fX18gICBfX19fX19fX18gICAgICAuX18=').decode("utf-8"))
    print(base64.b64decode('XF9fX19fXyAgIFxfX19fXF8gICBfX19fXy8gIC8gICBfX19fXy8gX19fXyB8X198X19fX18gICBfX19fX19fX19fXw==').decode("utf-8") )
    print(base64.b64decode('IHwgICAgIF9fXy8gIF8gXHwgICAgX18pXyAgIFxfX19fXyAgXCAvICAgIFx8ICBcX19fXyBcXy8gX18gXF8gIF9fIFw=').decode("utf-8") )
    print(base64.b64decode('IHwgICAgfCAgKCAgPF8+ICkgICAgICAgIFwgIC8gICAgICAgIFwgICB8ICBcICB8ICB8Xz4gPiAgX19fL3wgIHwgXC8=').decode("utf-8") )
    print(base64.b64decode('IHxfX19ffCAgIFxfX19fL19fX19fX18gIC8gL19fX19fX18gIC9fX198ICAvX198ICAgX18vIFxfX18gID5fX3w=').decode("utf-8") )
    print(base64.b64decode('ICAgICAgICAgICAgICAgICAgICAgICBcLyAgICAgICAgICBcLyAgICAgXC8gICB8X198ICAgICAgICBcLw==').decode("utf-8") )
    print()

MARKET_PRICES[ITEM_TYPES.Card].update(getNinjaPrices(CARD_PRICES_URL))
MARKET_PRICES[ITEM_TYPES.Prophecy].update(getNinjaPrices(PROPHECY_PRICES_URL))
MARKET_PRICES[ITEM_TYPES.Unique].update(getNinjaPrices(UNIQUE_FLASK_PRICES_URL))
MARKET_PRICES[ITEM_TYPES.Currency].update(getNinjaCurrency(CURRENCY_PRICES_URL))

'''
for k,v in MARKET_PRICES[ITEM_TYPES.Currency].items():
    print(str(k) + ': ' + str(v))

for k,v in MARKET_PRICES[ITEM_TYPES.Card].items():
    print(str(k) + ': ' + str(v))
'''

# LOCAL
data = loadApiPageFromFile('response.txt')
splashScreen()
stashes = data['stashes']
findDeals(stashes)

'''
#ONLINE
splashScreen()
next_change_id = getNinjaNextPageId()
while(True):
    print('Fetching page #{}...'.format(next_change_id))
    data = getApiPage(next_change_id)
    stashes = data['stashes']
    findDivDeals(stashes)
    findUniqueFlaskDeals(stashes)
    next_change_id = data['next_change_id']
    time.sleep(1)
    
'''
