import urllib.request

base_site = "http://api.pathofexile.com/public-stash-tabs"

urllib.request.urlopen(base_site).read()