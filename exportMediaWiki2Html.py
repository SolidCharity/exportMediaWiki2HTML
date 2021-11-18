#!/usr/bin/python3

# Author: Timotheus Pokorra <timotheus.pokorra@solidcharity.com>
# source hosted at https://github.com/SolidCharity/exportMediaWiki2HTML
# licensed under the MIT license
# Copyright 2020-2021 Timotheus Pokorra

from urllib import parse
import requests
import json
import re
from pathlib import Path
import argparse

description = """
Export MediaWiki pages to HTML
Call like this:
   ./exportMediaWiki2Html.py --url=https://mywiki.example.org

   Optionally pass the page id of the page you want to download, eg. for debugging:
   ./exportMediaWiki2Html.py --url=https://mywiki.example.org --page=180

   Optionally pass the category id, all pages with that category will be exported:
   ./exportMediaWiki2Html.py --url=https://mywiki.example.org --category=22

   Optionally pass the username and password:
   ./exportMediaWiki2Html.py --url=https://mywiki.example.org --username=myuser --password=topsecret
"""
parser = argparse.ArgumentParser(description=description, formatter_class=argparse.RawDescriptionHelpFormatter)

parser.add_argument('-l','--url', help='The url of the wiki',required=True)
parser.add_argument('-u','--username', help='Your user name',required=False)
parser.add_argument('-p','--password', help='Your password',required=False)
parser.add_argument('-c','--category', help='The category to export',required=False)
parser.add_argument('-g','--page', help='The page to export',required=False)
args = parser.parse_args()

url = args.url
if not url.endswith('/'):
  url = url + '/'

pageOnly = -1
categoryOnly = -1
if args.category is not None:
  categoryOnly = int(args.category)
if args.page is not None:
  pageOnly = int(args.page)

Path("export/img").mkdir(parents=True, exist_ok=True)

S = requests.Session()

if args.username is not None and args.password is not None:
  LgUser = args.username
  LgPassword = args.password

  # Retrieve login token first
  PARAMS_0 = {
      'action':"query",
      'meta':"tokens",
      'type':"login",
      'format':"json"
  }
  R = S.get(url=url + "/api.php", params=PARAMS_0)
  DATA = R.json()
  LOGIN_TOKEN = DATA['query']['tokens']['logintoken']

  # Main-account login via "action=login" is deprecated and may stop working without warning. To continue login with "action=login", see [[Special:BotPasswords]]
  PARAMS_1 = {
      'action':"login",
      'lgname':LgUser,
      'lgpassword':LgPassword,
      'lgtoken':LOGIN_TOKEN,
      'format':"json"
  }

  R = S.post(url + "/api.php", data=PARAMS_1)
  DATA = R.json()
  if "error" in DATA:
    print(DATA)
    exit(-1)

if categoryOnly != -1:
  url_allpages = url + "/api.php?action=query&list=categorymembers&format=json&cmpageid=" + str(categoryOnly)
else:
  url_allpages = url + "/api.php?action=query&list=allpages&aplimit=500&format=json"
response = S.get(url_allpages)
data = response.json()
if "error" in data:
  print(data)
  if data['error']['code'] == "readapidenied":
    print()
    print("get login token here: " + url + "/api.php?action=query&meta=tokens&type=login")
    print("and then call this script with parameters: myuser topsecret mytoken")
    exit(-1)
if categoryOnly != -1:
  pages = data['query']['categorymembers']
else:
  pages = data['query']['allpages']

def quote_title(title):
  return parse.quote(page['title'].replace(' ', '_'))

downloadedimages = []
def DownloadImage(filename, urlimg):
  if not filename in downloadedimages:
    if '/thumb/' in urlimg:
      urlimg = urlimg.replace('/thumb/', '/')
      urlimg = urlimg[:urlimg.rindex('/')]
    response = S.get(url + urlimg)
    content = response.content
    f = open("export/img/" + filename, "wb")
    f.write(content)
    f.close()
    downloadedimages.append(filename)

def PageTitleToFilename(title):
    temp = re.sub('[^A-Za-z0-9\u0400-\u0500]+', '_', title);
    return temp.replace("(","_").replace(")","_").replace("__", "_")

for page in pages:
    if (pageOnly > -1) and (page['pageid'] != pageOnly):
        continue
    print(page)
    quoted_pagename = quote_title(page['title'])
    url_page = url + "index.php?title=" + quoted_pagename + "&action=render"
    response = S.get(url_page)
    content = response.text
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
          linkedpage = parse.unquote(origlinkedpage)
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
    content = re.sub("(<!--).*?(-->)", '', content, flags=re.DOTALL)

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


