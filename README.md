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

You need to use a bot password, to make the script work, see [[Special:BotPasswords]] / https://www.mediawiki.org/wiki/Manual:Bot_passwords

Install
=======

    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt

Usage
=====

Please pass the url of the wiki

    python3 exportMediaWiki2Html.py --url https://mywiki.example.org

Optionally pass the page id of the page you want to download, eg. for debugging:

    python3 exportMediaWiki2Html.py --url https://mywiki.example.org --page 180

Optionally pass the username and password:

    python3 exportMediaWiki2Html.py --url https://mywiki.example.org --user myuser --password mypwd [pageid]

You can use `--help` to see all options.

Contribute
==========

Feel free to file any issues, and Pull Requests are welcome as well!
