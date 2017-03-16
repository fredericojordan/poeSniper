import requests
import json
import time
import re
import winsound
import base64

PLAY_SOUNDS = True
MIN_PROFIT = 3.0
MIN_ROI = 0.05

CURRENT_LEAGUE = "Legacy"

API_BASE_URL = "http://api.pathofexile.com/public-stash-tabs"
UNIQUE_FLASK_PRICES_URL = "http://cdn.poe.ninja/api/Data/GetUniqueFlaskOverview"
CARD_PRICES_URL = "http://api.poe.ninja/api/Data/GetDivinationCardsOverview"
PROPHECY_PRICES_URL = "http://api.poe.ninja/api/Data/GetProphecyOverview"
UNIQUE_ARMOUR_PRICES_URL = "http://cdn.poe.ninja/api/Data/GetUniqueArmourOverview"
UNIQUE_WEAPON_PRICES_URL = "http://cdn.poe.ninja/api/Data/GetUniqueWeaponOverview"
UNIQUE_MAP_PRICES_URL = "http://api.poe.ninja/api/Data/GetMapOverview"
CURRENCY_PRICES_URL = "http://cdn.poe.ninja/api/Data/GetCurrencyOverview"

MARKET_PRICES = [{} for _ in range(10)]

AXE1H_LIST = ['Rusted Hatchet','Jade Hatchet','Boarding Axe','Cleaver','Broad Axe','Arming Axe','Decorative Axe','Spectral Axe','Etched Hatchet','Jasper Axe','Tomahawk','Wrist Chopper','War Axe','Chest Splitter','Ceremonial Axe','Wraith Axe','Engraved Hatchet','Karui Axe','Siege Axe','Reaver Axe','Butcher Axe','Vaal Hatchet','Royal Axe','Infernal Axe','Runic Hatchet']
AXE2H_LIST = ['Stone Axe','Jade Chopper','Woodsplitter','Poleaxe','Double Axe','Gilded Axe','Shadow Axe','Dagger Axe','Jasper Chopper','Timber Axe','Headsman Axe','Labrys','Noble Axe','Abyssal Axe','Karui Chopper','Talon Axe','Sundering Axe','Ezomyte Axe','Vaal Axe','Despot Axe','Void Axe','Fleshripper']
BOW_LIST = ['Crude Bow','Short Bow','Long Bow','Composite Bow','Recurve Bow','Bone Bow','Royal Bow','Death Bow','Grove Bow','Reflex Bow','Decurve Bow','Compound Bow','Sniper Bow','Ivory Bow','Highborn Bow','Decimation Bow','Thicket Bow','Steelwood Bow','Citadel Bow','Ranger Bow','Assassin Bow','Spine Bow','Imperial Bow','Harbinger Bow','Maraketh Bow']
CLAW_LIST = []
DAGGER_LIST = []
MACE1H_LIST = []
MACE2H_LIST = []
SCEPTRE_LIST = []
STAFF_LIST = []
SWORD1H_LIST = []
SWORD2H_LIST = []
SWORDTHRUST_LIST = []
WAND_LIST = []


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

def getItemFrameType(item):
    return item["frameType"]
    
def getItemLeague(item):
    return item["league"]

def isFlask(item):
    return 'Flask' in getItemTypeLine(item)

def isWeapon(item):
    c = is1HAxe(item) or \
        is2HAxe(item) or \
        isBow(item) or \
        isClaw(item) or \
        isDagger(item) or \
        is1HMace(item) or \
        is2HMace(item) or \
        isSceptre(item) or \
        isStaff(item) or \
        is1HSword(item) or \
        is2HSword(item) or \
        isThrustSword(item) or \
        isWand(item)
    return c

def is1HAxe(item):
    return getItemTypeLine(item) in AXE1H_LIST

def is2HAxe(item):
    return getItemTypeLine(item) in AXE2H_LIST
    
def isBow(item):
    return getItemTypeLine(item) in BOW_LIST
    
def isClaw(item):
    return getItemTypeLine(item) in CLAW_LIST

def isDagger(item):
    return getItemTypeLine(item) in DAGGER_LIST

def is1HMace(item):
    return getItemTypeLine(item) in MACE1H_LIST

def is2HMace(item):
    return getItemTypeLine(item) in MACE2H_LIST

def isSceptre(item):
    return getItemTypeLine(item) in SCEPTRE_LIST
    
def isStaff(item):
    return getItemTypeLine(item) in STAFF_LIST
    
def is1HSword(item):
    return getItemTypeLine(item) in SWORD1H_LIST

def is2HSword(item):
    return getItemTypeLine(item) in SWORD2H_LIST

def isThrustSword(item):
    return getItemTypeLine(item) in SWORDTHRUST_LIST

def isWand(item):
    return getItemTypeLine(item) in WAND_LIST

def getStashName(stash):
    return stash["stash"]

def getCharacterName(stash):
    return stash["lastCharacterName"]

def getAccountName(stash):
    return stash["accountName"]

def isEmpty(stash):
    return stash["items"] == []

def getItemMarketPrice(item):
    if getItemFrameType(item) == ITEM_TYPES.Card:
        if getItemTypeLine(item) in MARKET_PRICES[ITEM_TYPES.Card]:
            return MARKET_PRICES[ITEM_TYPES.Card][getItemTypeLine(item)]
            
    if getItemFrameType(item) == ITEM_TYPES.Unique:
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
                if getItemFrameType(i) == ITEM_TYPES.Card:
                    if getProfitMargin(i) >= MIN_PROFIT and getROI(i) >= MIN_ROI:
                        outputText = getTradeInfoMessage(i) + ' ' + getTradeInGameMessage(s, i)
                        print(outputText)
            
                # UniqueFlasks
                if getItemFrameType(i) == ITEM_TYPES.Unique and isFlask(i):
                    if getProfitMargin(i) >= MIN_PROFIT and getROI(i) >= MIN_ROI:
                        outputText = getTradeInfoMessage(i) + getTradeInGameMessage(s, i)
                        print(outputText)
                        
                # Unique Weapons
                if getItemFrameType(i) == ITEM_TYPES.Unique and isWeapon(i):
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
MARKET_PRICES[ITEM_TYPES.Unique].update(getNinjaPrices(UNIQUE_WEAPON_PRICES_URL))
MARKET_PRICES[ITEM_TYPES.Unique].update(getNinjaPrices(UNIQUE_ARMOUR_PRICES_URL))
MARKET_PRICES[ITEM_TYPES.Unique].update(getNinjaPrices(UNIQUE_MAP_PRICES_URL))
MARKET_PRICES[ITEM_TYPES.Currency].update(getNinjaCurrency(CURRENCY_PRICES_URL))

'''
for k,v in MARKET_PRICES[ITEM_TYPES.Currency].items():
    print(str(k) + ': ' + str(v))

for k,v in MARKET_PRICES[ITEM_TYPES.Card].items():
    print(str(k) + ': ' + str(v))
'''

splashScreen()

# LOCAL
pagefile = 'lastresponse.txt'
print('Loading page from file ' + pagefile)
data = loadApiPageFromFile(pagefile)
stashes = data['stashes']
findDeals(stashes)
print("Done!")

'''
#ONLINE
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
