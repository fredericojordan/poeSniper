import re
import requests
import json
import time

API_BASE_URL = "http://api.pathofexile.com/public-stash-tabs"


def dumpToFile(data, filename):
    with open(filename, 'w') as outfile:
        json.dump(data, outfile)
        outfile.close()

def getNinjaNextPageId():
    response = requests.get("http://api.poe.ninja/api/Data/GetStats")
    return response.json().get('nextChangeId')

def loadApiPageFromFile(file_name):
    file = open(file_name, 'r', encoding='utf-8')
    text = file.read()
    file.close()
    return json.loads(text)
    
def getApiPage(page_id=""):
    target = API_BASE_URL
    if (page_id != ""):
        target = target + "?id=" + str(page_id)
       
    response = requests.get(target)
    
    if response.status_code == 200:
        data = response.json()
        dumpToFile(data, 'lastOffers.txt')
        return data
    else:
        raise ConnectionError('API request returned status code {}: {}!'.format(response.status_code, response.reason))

def evaluateOffers(stashes):
	for s in stashes:
		items = s['items']
		for i in items:
			print(isOfferValid(i))
	
def getItemSellingOffer(item):
    o = re.split(r'(\~*\s*)(\d+(?:\.\d+)?(?:\/\d+)?)(\W*)', item['note'])
    return [o[0], o[2], o[4]]
	
def isOfferValid(item):
    conditions = False
    hasNote = "note" in item.keys() and item['note'].startswith('~')
    
    if hasNote:
        try:
            offer = getItemSellingOffer(item)
            hasPrice = offer[0].startswith("~b/o") or offer[0].startswith("~price")
            if '/0' not in offer[1]:
                priceIsNotNull = eval(offer[1]) > 0.0
            else:
                priceIsNotNull = False
                
            conditions = hasNote and hasPrice and priceIsNotNull
        except:
            dumpToFile(item,'problemitem.txt')
            print(item['id'])
            conditions = False
            raise
    return conditions


# TEST
notes = ['~','~b/o 2 chaos','~price 1mirr','~b/o 25.3 alt','~b/o 3/5 chaos','~price 5/0 chaos','~price .13 chrom','~b/o .015 chaos']
for s in notes:
	print(s)
	hasNote = True
	if hasNote:
		offer = re.split(r'(\~*\s*)(\d+(?:\.\d+)?(?:\/\d+)?)(\W*)', s)
	print(offer)

'''
# LOCAL
pagefile = 'lastOffers.txt'
print('Loading page from file ' + pagefile)
data = loadApiPageFromFile(pagefile)
stashes = data['stashes']
evaluateOffers(stashes)
print('Done!')



# ONLINE
next_change_id = getNinjaNextPageId()
while(True):
    print('Fetching page #{}...'.format(next_change_id))
    data = getApiPage(next_change_id)
    stashes = data['stashes']
    evaluateOffers(stashes)
    next_change_id = data['next_change_id']
    time.sleep(1)
'''
