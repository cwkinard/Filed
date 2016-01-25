from bs4 import BeautifulSoup
import requests
import re
import logging
import filerpath
from datetime import datetime
import os


LOGIN_PAGE = 'https://login.fidelity.com/ftgw/Fas/Fidelity/RtlCust/Login/Response/dj.chf.ra?AuthRedUrl=https%3A%2F%2Foltx.fidelity.com%2Fftgw%2Ffbc%2Fofsummary%2FdefaultPage&AuthOrigUrl=llp%2Fhomepage&errorpage=%2Flogin%2FerrorPages%2FaccountErrorPage'


class Scraper:

    def __init__(self, username, password, qa):
	self.s = requests.session()
	
	self._logger = logging.getLogger(__name__)
	self._logger.setLevel(logging.DEBUG)
	handler = logging.FileHandler('fidelity.log')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self._logger.addHandler(handler)	

	self.username = username
	self.password = password
	self.qa = qa

	self._login()

    def _login(self):

	# Post login
	data = { 'DEVICE_PRINT' : 'version=1&amp;pm_fpua=mozilla/5.0 (windows nt 10.0; wow64) applewebkit/537.36 (khtml, like gecko) chrome/47.0.2526.106 safari/537.36|5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36|Win32&amp;pm_fpsc=24|1706|960|900&amp;pm_fpsw=&amp;pm_fptz=-5&amp;pm_fpln=lang=en-US|syslang=|userlang=&amp;pm_fpjv=0&amp;pm_fpco=1', 
	'SSN' : self.username, 'PIN' : self.password }

        self.res = self.s.post(LOGIN_PAGE, data=data)

        lg_page = BeautifulSoup(self.res.text, 'html.parser')

	self._logger.info("Logged In")
    
    def _get_statement_dropdown(self, acctId):

	# View statement history
        statement_url = "https://workplaceservices200.fidelity.com/mybenefits/savings2/navigation/dc/OnlineStatement"
        self.res = self.s.get(statement_url)

        statement_page = BeautifulSoup(self.res.text, 'html.parser')
        dropdown = statement_page.find('select', name='month_req')
        return dropdown

    def scrape(self, account, drive_date):
	
	self._logger.info("Starting scrape for account '%s' ", account)

	dropdown = self._get_statement_dropdown()

	rows = dropdown.find_all('option')
	for row in rows:	
            range = row.get('value')
	    regex = re.compile('(?<=-)(.*)(?=)', re.MULTILINE)
            date_raw = re.search(regex, link).group()
	    statement_date = datetime.strptime(date_raw, "%m/%d/%Y").date()
	
	    self._logger.debug("Statement Date: '%s', Drive Date: '%s' ", statement_date, drive_date)

	    # Break when dates match
	    if statement_date <= drive_date:
		break
	    	
	    # Download statement
	    #statement_url = 'https://onlinebanking.tdbank.com/accts/acct_eStatement_View.asp?'
	    #statement_url += ('viewDate=' + date_raw + '&statementIndex=' + index +
		#	      '&acctID=' + account['web_id'])
	    
	    statement_url = 'https://onlinebanking.tdbank.com/accts/Statement.asp'
	    data = { 'refreshTime' : datetime.now().strftime("%Y/%m/%d %I:%M:%S %p"),
		     'viewDate' : date_raw, 'acctID' : account['web_id'],
		     'statementIndex' : index, 'useCache' : 'N' }

	    file = self.s.post(statement_url, data=data) 	

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

        table_body = self._get_statement_table(account['web_id'])

        rows = table_body.find_all('tr', attrs={'class':'td-table-alt-row'})
        cols = rows[0].find_all('td')
        link = cols[2].find('a').get('href')
        regex = re.compile('(?<=javascript:getStatement\()(.*)(?=,)', re.MULTILINE)
        date_raw = re.search(regex, link).group()
        latest_date = datetime.strptime(date_raw, "%Y%m%d").date()

	if latest_date > date:
	    return True
	else:
	    return False



   
