#!/usr/bin/python3

# Author: Timotheus Pokorra <timotheus.pokorra@solidcharity.com>
# licensed under the MIT license
# Copyright 2020 Timotheus Pokorra

import urllib.request, urllib.parse
import json
import re
from pathlib import Path
import sys

if len(sys.argv) == 1:
  print("Please pass the url of the wiki, eg. https://mywiki.example.org/")
  exit(-1)

url = sys.argv[1]

Path("export/img").mkdir(parents=True, exist_ok=True)

url_allpages = url + "/api.php?action=query&list=allpages&aplimit=500&format=json"
response = urllib.request.urlopen(url_allpages)
data = json.loads(response.read())

def quote_title(title):
  return urllib.parse.quote(page['title'].replace(' ', '_'))

downloadedimages = []
def DownloadImage(filename, urlimg):
  if not filename in downloadedimages:
    if '/thumb/' in urlimg:
      urlimg = urlimg.replace('/thumb/', '/')
      urlimg = urlimg[:urlimg.rindex('/')]
    response = urllib.request.urlopen(url + urlimg)
    content = response.read()
    f = open("export/img/" + filename, "wb")
    f.write(content)
    f.close()
    downloadedimages.append(filename)

filenames = {}
for page in data['query']['allpages']:
    filenames[quote_title(page['title'])] = re.sub('[^A-Za-z0-9]+', '_', page['title']) + ".html"

for page in data['query']['allpages']:
    print(page)
    quoted_pagename = quote_title(page['title'])
    url_page = url + "/index.php?title=" + quoted_pagename + "&action=render"
    response = urllib.request.urlopen(url_page)
    content = response.read().decode()
    pos = 0
    while url + "index.php?title=" in content:
        pos = content.find(url + "index.php?title=")
        posendquote = content.find('"', pos)
        linkedpage = content[pos:posendquote]
        linkedpage = linkedpage[linkedpage.find('=') + 1:]
        if linkedpage.startswith('File:'):
          linkedpage = linkedpage[linkedpage.find(':')+1:]
          imgpos = content.find('src=', posendquote)
          if linkedpage in downloadedimages:
            # probably a thumbnail
            content = content[:pos] + "img/" + linkedpage + content[posendquote:]
          elif imgpos > posendquote:
            imgendquote = content.find('"', imgpos+5)
            imgpath = content[imgpos+5:imgendquote]
            content = content[:imgpos+5] + "img/" + linkedpage + content[imgendquote:]
            DownloadImage(linkedpage, imgpath)
            content = content[:pos] + "img/" + linkedpage + content[posendquote:]
          else:
            print("Error: not an image? " + linkedpage)
            exit(-1)
        elif linkedpage in filenames:
          content = content[:pos] + filenames[linkedpage] + content[posendquote:]
        else:
          content = content[:pos] + linkedpage + content[posendquote:]

    #content = content.replace('<div class="mw-parser-output">'.encode("utf8"), ''.encode("utf8"))
    #content = re.sub("(<!--).*?(-->)".encode("utf8"), ''.encode("utf8"), content, flags=re.MULTILINE)

    f = open("export/" + filenames[quoted_pagename], "wb")
    f.write(("<html>\n<head><title>" + page['title'] + "</title></head>\n<body>\n").encode("utf8"))
    f.write(("<h1>" + page['title'] + "</h1>").encode("utf8"))
    f.write(content.encode('utf8'))
    f.write("</body></html>".encode("utf8"))
    f.close()
    

