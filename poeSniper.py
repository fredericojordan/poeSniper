import urllib.request
import json

BASE_SITE = "http://api.pathofexile.com/public-stash-tabs"

def getStashes(id=""):
    target = BASE_SITE
    
    if (id != ""):
        target = target + "?id=" + str(id)
        
    page = str(urllib.request.urlopen(target).read())[2:-1]
    page = page.replace("\\'", "'")
    page = page.replace("\\\\", "\\")
    return page

dump_file = open('dump.txt', 'w')
next_page = ""
for x in range(10):
    data = getStashes(next_page)
    dump_file.write(data)
    dump_file.write("\n")
    jPage = json.loads(data)
    next_page = jPage["next_change_id"]
    print(next_page)
    
    
dump_file.close()
print("Done!")