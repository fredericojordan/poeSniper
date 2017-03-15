import requests
import json
import time

CURRENT_LEAGUE = "Legacy"
API_BASE_URL = "http://api.pathofexile.com/public-stash-tabs"
STARTING_PAGE = "49919976-52967025-49502222-57596848-53578103" # empty string for first page
TOTAL_PAGES = 1
    
class FRAME_TYPES:
    Normal, Magic, Rare, Unique, Gem, Currency, Card, Quest, Prophecy, Relic = range(10)

def getPricesFromNinja(url):
    params = {'league': CURRENT_LEAGUE, 'time': time.strftime("%Y-%m-%d")}
    response = requests.get(url, params = params)
    prices = response.json().get('lines')
    return dict( [i.get('name'), i.get('chaosValue')] for i in prices )	
    

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

def getItemPrice(name, frameType):
	# Other items can be added here...
	# Divination Cards
	if frameType == FRAME_TYPES.Card:
		for k,v in div_prices.items():
			if k == name:
				return float(v)
	# Prophecies

def findDivDeals(stashes):
	for s in stashes:
		accountName = s['accountName']
		lastCharacterName = s['lastCharacterName']
		items = s['items']
		stashName = s.get('stash')
		
		for i in items:
			league = i.get('league')
			frameType = i.get('frameType')
			if league == CURRENT_LEAGUE and frameType == FRAME_TYPES.Card:
				name = i.get('typeLine')
				price = i.get('note')
				w = i.get('w')
				h = i.get('h')
				
				# Gets items with price, in chaos, b/o only
				if price and ('~b/o' and 'chaos' in price):
					
					# convert price
					price = price.replace('~b/o ', '')
					price = price.replace('~price ', '')
					price = price.replace(' chaos', '')
					price = float(price)
					
					if (getItemPrice(name, FRAME_TYPES.Card) - price) > -5.0:
						print('@' + lastCharacterName + ' Hi, I would like to buy your ' + str(name) + ' listed for ' + str(price) + ' chaos in ' + str(league) + ' (stash tab "' + str(stashName) + '"; position: left ' + str(w) + ', top ' + str(h) + ')')

# Divination Cards						
url_div = "http://api.poe.ninja/api/Data/GetDivinationCardsOverview"
div_prices = getPricesFromNinja(url_div)

# Prophecies
url_prophecy = "http://api.poe.ninja/api/Data/GetProphecyOverview"
prophecy_prices = getPricesFromNinja(url_prophecy)

# Flasks
url_flasks = "http://cdn.poe.ninja/api/Data/GetUniqueFlaskOverview"
flask_prices = getPricesFromNinja(url_flasks)


#for k,v in flask_prices.items():
#	print(str(k) + ': ' + str(v))

# VSZ
data = loadApiPageFromFile('response.txt')
stashes = data['stashes']
findDivDeals(stashes)


# FVJ
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
