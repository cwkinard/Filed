from bs4 import BeautifulSoup
import requests
import re
import logging
import filerpath
from datetime import datetime
import os
import urllib
from scraperbase import ScraperBase


LOGIN_PAGE = 'https://www.barclaycardus.com'


class Scraper(ScraperBase):

    def __init__(self, username, password, qa):
	ScraperBase.__init__(self, username, password, qa)

    def _login(self):

	self.res = self.s.get(LOGIN_PAGE)

	login_page = BeautifulSoup(self.res.text, 'html.parser')

	pm_fp = login_page.find('input', attrs={'id':'pm_fp', 'type':'hidden'}).get('value')
	sp = login_page.find('input', attrs={'name':'_sourcePage', 'type':'hidden'}).get('value')
	fp = login_page.find('input', attrs={'name':'__fp', 'type':'hidden'}).get('value')
	self._logger.debug(self.res.text)
	self._logger.debug("'%s' '%s' '%s'", pm_fp, sp, fp)
        # Post Login Data
        data = { 'username':self.username, 'redirectAction':'', 'login':'Log in', 'INTNAV':
		 'Homepage_CustomerLoginBtn', 'loginButtonAction':'true', 'pm_fp': pm_fp,
		 'redirectAction':'', '_sourcePage':sp, '__fp':fp  }
	data = urllib.urlencode(data)
	self._logger.debug(data)
	login_url = 'https://www.barclaycardus.com/servicing/login'
        self.res = self.s.post(login_url, data=data)

	pass_page = BeautifulSoup(self.res.text, 'html.parser')
	username = pass_page.find('input', attrs={'name':'username', 'type':'hidden'}).get('value')

	pm_fp = login_page.find('input', attrs={'id':'pm_fp', 'type':'hidden'}).get('value')
        sp = login_page.find('input', attrs={'name':'_sourcePage', 'type':'hidden'}).get('value')
        fp = login_page.find('input', attrs={'name':'__fp', 'type':'hidden'}).get('value')
	
	data = { 'password':self.password, 'submitPassword':'Log in', 'loginButton-button':'Log in',
		 'username':username, 'rememberUserName':'false', 'redirectAction':'', 
		 'INTNAV':'Homepage_CustomerLoginBtn', 'loginButtonAction':'true', 'pm_fp': pm_fp,
                 '_sourcePage':sp, '__fp':fp  }
	data = urllib.urlencode(data)

	self.res = self.s.post(pass_page, data=data)	

	self._logger.info("Logged In")
    
    def _get_statement_dropdown(self):

	statement_url = 'https://www.barclaycardus.com/servicing/activity'
	self.res = self.s.get(statement_url)

	statement_page = BeautifulSoup(self.res.text, 'html.parser')
	statement_url = statement_page.find('nav', id='subNavMenu').findAll('a')[1].get('href')

	self.res = self.s.get(statement_url)

	# View statement history
        statement_page = BeautifulSoup(self.res.text, 'html.parser')
        dropdown = statement_page.find('select', id='statementsSelect')
        return dropdown

    def scrape(self, account, drive_date):
	
	self._logger.info("Starting scrape for account '%s' ", account)

	dropdown = self._get_statement_dropdown()

	rows = dropdown.find_all('option')
	for row in rows:	
            date_raw = row.text

	    if 'Annual Summary' not in date_raw:
	        statement_date = datetime.strptime(date_raw, "%m/%d/%Y").date()
	
	        self._logger.debug("Statement Date: '%s', Drive Date: '%s' ", 
				    statement_date, drive_date)

	        # Break when dates match
	        if statement_date <= drive_date:
		    break
	    
		doc_id = row.get('value')

	        # Download statement
	        statement_url = 'https://www.barclaycardus.com/servicing/mystatements?getStatement=DownloadPDF&documentId=' + str(doc_id)
	    
	        file = self.s.get(statement_url)
	        #self._logger.debug(self.res.text)

		# Save statment
		self._save(file, statement_date)

	return
	    

    def hasNew(self, account, date):

        dropdown = self._get_statement_dropdown()

        rows = dropdown.find_all('option')
	for row in rows:
	    date_raw = rows[0].text

	    if 'Annual Summary' not in date_raw:
                latest_date = datetime.strptime(date_raw, "%m/%d/%Y").date()

	        if latest_date > date:
	            self._logger.info("New statement(s) found")
	            return True
	        else:
	            self._logger.info("No new statement(s) found")
	            return False



   
