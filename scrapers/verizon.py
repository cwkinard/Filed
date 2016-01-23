from bs4 import BeautifulSoup
import requests
import re
import logging
import filerpath
from datetime import datetime
import os


LOGIN_PAGE = 'https://www.verizonwireless.com'


class Scraper:

    def __init__(self, username, password, qa):
	self.s = requests.session()
	
	self._logger = logging.getLogger(__name__)
	self._logger.setLevel(logging.DEBUG)
	log_path = os.path.join(filerpath.TMP_PATH, 'verizon.log')
	handler = logging.FileHandler(log_path)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self._logger.addHandler(handler)	

	self.username = username
	self.password = password
	self.qa = qa

	self._login()

    def _login(self):

	headers = {
	  'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'
	}
	
	# Pull login page for cookies
	self.res = self.s.get(LOGIN_PAGE, headers=headers)
	
	# Post login
	data = {
	   'realm':'vzw', 'gx_charset':'UTF-8', 'rememberUserNameCheckBoxExists':'Y',
	   'IDToken1':self.username, 'userNameOnly':'true' 
	}
	lg_page = 'https://login.verizonwireless.com/amserver/UI/Login'
        self.res = self.s.post(LOGIN_PAGE, data=data, headers=headers)

	self._logger.debug(self.res.text)

	data = {
           'realm':'vzw', 'goto':'', 'gotoOnFail':'', 'displayLoginStart':'true',
           'IDToken1':self.username, 'mode':'', 'IDToken2':self.password 
        }
        self.res = self.s.post(LOGIN_PAGE, data=data, headers=headers)

	self._logger.info("Logged In")
    
    def _get_statement_table(self):

	# View statement history
        statement_url = 'https://ebillpay.verizonwireless.com/vzw/accountholder/digitalocker/MessageCenter.action'
        
	headers = {
          'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'
        }	

	self.res = self.s.get(statement_url, headers=headers)
	#self._logger.debug(self.res.text)
        statement_page = BeautifulSoup(self.res.text, 'html.parser')
        table = statement_page.find('table', id='myDocsData')
        return table

    def scrape(self, account, drive_date):
	
	self._logger.info("Starting scrape for account '%s' ", account)

	table = self._get_statement_table()
	table_body = table.find('tbody')

	rows = table_body.find_all('tr')
	for row in rows:	
	    cols = row.find_all('td')
            link = cols[2].find('a').get('href')
            date_raw = cols[2].text
	    statement_date = datetime.strptime(date_raw, "%m/%d/%Y").date()
	
	    self._logger.debug("Statement Date: '%s', Drive Date: '%s' ", statement_date, drive_date)

	    # Break when dates match
	    if statement_date <= drive_date:
		break
	    	
	    # Download statement
	    #statement_url = 'https://ebillpay.verizonwireless.com/'
	    #statement_url += link
	    
	    headers = {
              'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'
            }
	
	    file = self.s.post(statement_url, data=data, headers=headers) 	

	    # Create directory structure
	    file_name = str(statement_date) + '.pdf'
	    file_path = os.path.join(filerpath.TMP_PATH, file_name)

	    self._logger.info("Downloaded statement '%s' ", file_name)

	    # Save statement
	    with open(file_path, "wb") as code:
    		code.write(file.content)

	    self._logger.debug("Statement saved to '%s' ", file_path)
	
	return
	    

    def hasNew(self, account, date):
	
	table = self._get_statement_table()
        table_body = table.find('tbody')

	# No statement table if new year
        if table_body is None:
            return False

        rows = table_body.find_all('tr')
        cols = rows[0].find_all('td')
        date_raw = cols[2].text
        latest_date = datetime.strptime(date_raw, "%m/%d/%Y").date()

	if latest_date > date:
	    self._logger.info("New statement(s) found")
	    return True
	else:
	    self._logger.info("No new statement(s) found")
	    return False



   
