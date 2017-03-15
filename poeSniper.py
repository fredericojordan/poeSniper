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
    
    page = page[2:-1]
    page = page.replace("\\'", "'")
    page = page.replace("\\\\", "\\")
    return json.loads(page)

def loadApiPageFromFile(file):
    file = open(file, 'r', encoding='utf-8')
    text = file.read()
    file.close()
    return json.loads(text)

def getItemCount(stashes):
    count = 0
    for i in range(len(stashes)):
        len(stashes[i]["items"])
    return count

div_prices = getDivinationPrices()
for k,v in div_prices.items():
    print(str(k) + ": " + str(v))

dump_file = open('dump.txt', 'w')
next_page = STARTING_PAGE

for x in range(TOTAL_PAGES):
    print("---- Page " +  str(x+1) + " ----")

    #jPage = getApiPage(next_page)
    jPage = loadApiPageFromFile('response.txt')
    
    stashes = jPage["stashes"]
    stashes_count = len(stashes)
    
    empty_stashes = 0
    total_items_number = 0
    cards = 0
    for i in range(stashes_count):
        items = stashes[i]["items"]
        if (items == []):
            empty_stashes += 1
        else:
            total_items_number += len(items)
            for t in range(len(items)):
                if (items[t]["frameType"] == FRAME_TYPES.Card and items[t]["league"] == CURRENT_LEAGUE):
                    item_name = items[t]["typeLine"]
                    if "note" in items[t].keys() and items[t]["note"].startswith("~b/o"):
                        print("{}: {} ({} chaos)".format(item_name, items[t]["note"][5:], div_prices[item_name]))
                    cards += 1
                    player_info = stashes[i]
                    player_info["items"] = []
                    dump_file.write(str(player_info))
                    dump_file.write(str(items[t]))
                    dump_file.write("\n")
    
    print(str(total_items_number) + " items on " + str(stashes_count-empty_stashes) + " stashes")
    print(str(cards) + " divination cards on legacy league")
    
    next_page = jPage["next_change_id"]
    print("Next page: " + next_page)   

dump_file.close()

print("Done!")
