import urllib.request
import json
import gzip
import io

BASE_SITE = "http://api.pathofexile.com/public-stash-tabs"
FIRST_PAGE = ""
#FIRST_PAGE = "49843657-52888415-49427506-57511230-53495186"
TOTAL_PAGES = 20

def decodeGzip(data): # FIXME
    buf = io.StringIO(data)
    f = gzip.GzipFile(fileobj=buf)
    return f.read()
    
def getStashes(id="", encodeGzip=False):
    target = BASE_SITE
    if (id != ""):
        target = target + "?id=" + str(id)
        
    request = urllib.request.Request(target)
    if (encodeGzip):
        request.add_header('Accept-encoding', 'gzip')
    response = urllib.request.urlopen(request)
    page = str(response.read())
    
    if response.info().get('Content-Encoding') == 'gzip':
        page = decodeGzip(page)
    
    page = page[2:-1]
    page = page.replace("\\'", "'")
    page = page.replace("\\\\", "\\")
    return page

dump_file = open('dump.txt', 'w')
next_page = FIRST_PAGE

for x in range(TOTAL_PAGES):
    print("---- Page " +  str(x+1) + " ----")
    
    data = getStashes(next_page)
    #data = getStashes(next_page, True) # GZIP
    
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
                if (items[t]["frameType"] == 6 and items[t]["league"] == "Legacy"):
                    cards += 1
                    dump_file.write(str(items[t]))
                    dump_file.write("\n")
    
    print(str(total_items_number) + " items on " + str(stashes_number-empty_stashes) + " stashes")
    print(str(cards) + " divination cards on legacy league")
    
    next_page = jPage["next_change_id"]
    print("Next page: " + next_page)   

dump_file.close()
print("Done!")