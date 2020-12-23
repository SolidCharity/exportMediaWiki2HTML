Export MediaWiki to HTML
========================

The task is to export a MediaWiki to HTML.

There is the extension DumpHTML, but it is unmaintained: https://www.mediawiki.org/wiki/Extension%3aDumpHTML

This Python script supports the following features:

* links between the pages
* links to anchors
* links to non-existing pages
* directly embedded images
* thumbnails
* supports authentication for dumping a protected wiki
* export all (currently up to 500) pages, or export a single page

Usage
=====

Please pass the url of the wiki

    ./exportMediaWiki2Html.py https://mywiki.example.org

Optionally pass the page id of the page you want to download, eg. for debugging:

    ./exportMediaWiki2Html.py https://mywiki.example.org 180

Optionally pass the username and password:

    ./exportMediaWiki2Html.py https://mywiki.example.org myuser mypwd [pageid]

Contribute
==========

Feel free to file any issues, and Pull Requests are welcome as well!
