#!/usr/bin/python3

# Author: Timotheus Pokorra <timotheus.pokorra@solidcharity.com>
# source hosted at https://github.com/SolidCharity/exportMediaWiki2HTML
# licensed under the MIT license
# Copyright 2020 Timotheus Pokorra

import urllib.request, urllib.parse
import json
import re
from pathlib import Path
import sys

if len(sys.argv) == 1:
  print("Please pass the url of the wiki")
  print("    ./exportMediaWiki2Html.py https://mywiki.example.org")
  print("Optionally pass the page id of the page you want to download, eg. for debugging:")
  print("    ./exportMediaWiki2Html.py https://mywiki.example.org 180")
  exit(-1)

url = sys.argv[1]
if not url.endswith('/'):
  url = url + '/'

pageOnly = -1
if len(sys.argv) == 3:
  pageOnly = int(sys.argv[2])

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

def PageTitleToFilename(title):
    temp = re.sub('[^A-Za-z0-9]+', '_', title);
    return temp.replace("(","_").replace(")","_").replace("__", "_")

for page in data['query']['allpages']:
    if (pageOnly > -1) and (page['pageid'] != pageOnly):
        continue
    print(page)
    quoted_pagename = quote_title(page['title'])
    url_page = url + "index.php?title=" + quoted_pagename + "&action=render"
    response = urllib.request.urlopen(url_page)
    content = response.read().decode()
    pos = 0
    while url + "index.php?title=" in content:
        pos = content.find(url + "index.php?title=")
        posendquote = content.find('"', pos)
        linkedpage = content[pos:posendquote]
        linkedpage = linkedpage[linkedpage.find('=') + 1:]
        linkedpage = linkedpage.replace('%27', '_');
        if linkedpage.startswith('File:') or linkedpage.startswith('Image:'):
          if linkedpage.startswith('File:'):
              linkType = "File:"
          if linkedpage.startswith('Image:'):
              linkType = "Image:"
          origlinkedpage = linkedpage[linkedpage.find(':')+1:]
          linkedpage = urllib.parse.unquote(origlinkedpage)
          imgpos = content.find('src="/images/', posendquote)
          if imgpos > posendquote:
            imgendquote = content.find('"', imgpos+len(linkType))
            imgpath = content[imgpos+len(linkType):imgendquote]
          if not linkedpage in downloadedimages:
            DownloadImage(linkedpage, imgpath)
          if linkedpage in downloadedimages:
            content = content.replace(url+"index.php?title="+linkType+origlinkedpage, "img/"+linkedpage)
            content = content.replace(imgpath, "img/"+linkedpage)
          else:
            print("Error: not an image? " + linkedpage)
            exit(-1)
        elif "&amp;action=edit&amp;redlink=1" in linkedpage:
          content = content[:pos] + "article_not_existing.html\" style='color:red'" + content[posendquote+1:]
        elif "#" in linkedpage:
          linkWithoutAnchor = linkedpage[0:linkedpage.find('#')]
          linkWithoutAnchor = PageTitleToFilename(linkWithoutAnchor)
          content = content[:pos] + linkWithoutAnchor + ".html#" + linkedpage[linkedpage.find('#')+1:] + content[posendquote:]
        else:
          linkedpage = PageTitleToFilename(linkedpage)
          content = content[:pos] + linkedpage + ".html" + content[posendquote:]

    #content = content.replace('<div class="mw-parser-output">'.encode("utf8"), ''.encode("utf8"))
    #content = re.sub("(<!--).*?(-->)".encode("utf8"), ''.encode("utf8"), content, flags=re.MULTILINE)

    f = open("export/" + PageTitleToFilename(page['title']) + ".html", "wb")
    f.write(("<html>\n<head><title>" + page['title'] + "</title></head>\n<body>\n").encode("utf8"))
    f.write(("<h1>" + page['title'] + "</h1>").encode("utf8"))
    f.write(content.encode('utf8'))
    f.write("</body></html>".encode("utf8"))
    f.close()

f = open("export/article_not_existing.html", "wb")
f.write(("<html>\n<head><title>This article does not exist yet</title></head>\n<body>\n").encode("utf8"))
f.write(("<h1>This article does not exist yet</h1>").encode("utf8"))
f.write("</body></html>".encode("utf8"))
f.close()


