Filed
=====

Modular scraping framework for retrieving statements online and saving to cloud storage provider (Google Drive).

## Setup

1. Download dependencies using requirements.txt: ``pip install -r requirements.txt`` 
2. Edit 'accounts.json' file with your accounts
3. Turn on Google Drive API as instructed here (and add created 'client_secret.json' to project root):
   https://developers.google.com/drive/v3/web/quickstart/python
4. Create 'logs', 'tmp', and '.credentials' directories
5. Start Selenium node server (for certain scrapers). See this great tutorial on Dockerized Selenium: https://github.com/SeleniumHQ/docker-selenium

## Run

```
python Filed.py --logging_level DEBUG --noauth_local_webserver
```

'--noauth_local_webserver' needs to only be run the first time for Google Drive setup

'--logging_level' supports multiple modes (INFO, WARN, etc.)

```
python Filed.py -s 12:01
```
Schedules Filed to run every day at 12:01 PM

## Notes

* Most scrapers do not have paging logic to pull full account history. Assumes that most accounts have recent statements in Google Drive (the ADP scraper currently does support full account history)
* Google Drive folder id's can be found by right clicking on the folder and selecting 'Get Link' (copy from end of hyperlink)
* See working scrapers list below. 

## To-Do

* Refactor account json file and loop logic for cleanliness
* Add complete statement history pull to scraper logic
* Abstract Google Drive from single source cloud provider 
* Finish LastPass vault integration
* Clean up and reorganize logging

# Working Scrapers
| Name | URL | Full History |
| ---- | --- | ------------ |
| TD Bank | tdbank.com | no |
| ADP | ipay.adp.com | yes |
| Benefit Wallet | mybenefitwallet.com | no |
| Pepco | pepco.com | no |
| Barclaycard | barclaycardus.com | maybe |
| Vanguard | personal.vanguard.com | yes |
| Verizon | verizonwireless.com | yes |
| Prosper | prosper.com | maybe |

## Working On
* Fidelity - statements use CSS print selectors
* Chase    - javascript generated key
