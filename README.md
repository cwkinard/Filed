Filed
=====

Modular scraping framework for retrieving statements online and saving to cloud storage provider (Google Drive).

# Setup

1. Download any/all dependencies. 
2. Edit 'accounts.json' file with your accounts
3. Turn on Google Drive API as instructed here (and add created 'client_secret.json' to project root):
   https://developers.google.com/drive/v3/web/quickstart/python
4. Create 'logs', 'tmp', and '.credentials' directories

# Run

```
python Filed.py --logging_level DEBUG --noauth_local_webserver
```

'--noauth_local_webserver' needs to only be run the first time for Google Drive setup
'--logging_level' supports multiple modes (INFO, WARN, etc.)

# Notes

* Most scrapers do not have paging logic to pull full account history. Assumes that most accounts have recent statements in Google Drive (the ADP scraper currently does support full account history)
* Google Drive folder id's can be found by right clicking on the folder and selecting 'Get Link' (copy from end of hyperlink)
* See working scrapers list below. Websites that require javascript can be tackled using a web automation library instead of python requests (modularity allows separate techniques for each scraper)

# To-Do

* Create parent scraper class to remove repeated logic (like saving statement to disc)
* Refactor account json file and loop logic for cleanliness
* Complete scheduling functionality
* Add complete statement history pull to scraper logic
* Abstract Google Drive from single source cloud provider 
* Finish LastPass vault integration
* Clean up and reorganize logging

# Working Scrapers
* TD Bank
* ADP
* Benefit Wallet
* Pepco

## Very Close
* Barclay
* Vanguard

## Blocked by Javascript
* Fidelity
* Verizon
* Chase
