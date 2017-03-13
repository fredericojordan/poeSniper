import urllib.request
import json
import gzip
import io

BASE_SITE = "http://api.pathofexile.com/public-stash-tabs"
    
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
        buf = io.StringIO(page)
        f = gzip.GzipFile(fileobj=buf)
        data = f.read()
        page = str(data)
    
    page = page[2:-1]
    page = page.replace("\\'", "'")
    page = page.replace("\\\\", "\\")
    return page
    
dump_file = open('dump.txt', 'w')
next_page = ""
for x in range(10):
    data = getStashes(next_page)
    #data = getStashes(next_page, True) # GZIP
    dump_file.write(data)
    dump_file.write("\n")
    jPage = json.loads(data)
    next_page = jPage["next_change_id"]
    print(next_page)    

dump_file.close()
print("Done!")