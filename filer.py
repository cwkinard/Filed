import logging
import pkgutil
import filerpath
import json
import os
import drive
from scraperbase import ScraperBase
from lastpass import (
    Vault,
    LastPassIncorrectGoogleAuthenticatorCodeError
)


def _CreateArgumentParser():
    try:
        import argparse
    except ImportError:
        return None
    parser = argparse.ArgumentParser(parents=[drive.argparser], add_help=False)
    return parser

argparser = _CreateArgumentParser()

class Filer(object):

    def __init__(self):
	"""        
	Instantiates a new Filer object, which scrapes each website
	defined as a scraper for new documents and files them 
	appropriately in the location defined.

	"""

	self._logger = logging.getLogger(__name__)
	self.scrapers = self.get_scrapers()
	#self.vault = self.get_vault()
        self.drive = drive.Drive()
	
	self._logger.info("Initiating Filer")
	self._logger.info("Loading Accounts from %s", filerpath.ACCOUNTS_PATH)
		
	# Open Accounts JSON config
        with open(filerpath.ACCOUNTS_PATH) as data_file:
            self.accounts = json.load(data_file)

	self._logger.info("Accounts loaded")
	

    @classmethod
    def get_scrapers(cls):

        """
        Dynamically loads all the scrapers in the 'scrapers' folder
	that contain 'Scraper' class inheriting from 'ScraperBase'.
        """

        logger = logging.getLogger(__name__)
	log_path = os.path.join(filerpath.LOG_PATH, 'Filed.log')
	handler = logging.FileHandler(log_path)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

	locations = [filerpath.SCRAPER_PATH]
        logger.info("Loading scrapers from: %s",
                     ', '.join(["'%s'" % location for location in locations]))
        scrapers = []
        for finder, name, ispkg in pkgutil.walk_packages(locations):
            try:
                loader = finder.find_module(name)
                scraper = loader.load_module(name)
            except:
                logger.warning("Skipped scraper '%s' due to an error.", name,
                               exc_info=True)
            else:
                if hasattr(scraper, 'Scraper') and issubclass(scraper.Scraper, ScraperBase):
                    logger.debug("Found scraper '%s'", name)
                    scrapers.append(scraper)
                else:
                    logger.warning("Skipped scraper '%s' because it misses " +
                                   "the 'Scraper' class or it does not inherit " +
				   "the 'ScraperBase' parent class", name)
	logger.info("Scrapers loaded")
        return scrapers
    
    @classmethod
    def get_vault(cls):
	
	"""
	Retrieves LastPass vault
	"""

	logger = logging.getLogger(__name__)
	log_path = os.path.join(filerpath.LOG_PATH, 'Filed.log')
        handler = logging.FileHandler(log_path)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

	try:
    	    # First try without a multifactor password
    	    vault = Vault.open_remote(username, password)
	except LastPassIncorrectGoogleAuthenticatorCodeError as e:
    	    # Get the code
    	    multifactor_password = input('Enter Google Authenticator code:')

    	    # And now retry with the code
    	    vault = Vault.open_remote(username, password, multifactor_password)
	return vault

    def file(self):

        self._logger.info("\nStarting Filer: Filer.file()")
	
	# Site Loop (ex. 'PNC Bank')
	for site in self.accounts:
	    if (self.accounts[site]['disabled'] == 'true'):
                    self._logger.info("Site '%s' disabled.", site)
                    continue
	    
	    self._logger.debug("Scraping '%s'", site)
	    # Find appropriate scraper for the account
	    scraper = next(x for x in self.scrapers if x.__name__.split('.')[0] == site)	

	    # Login Loop (ex. 'bankuser')
	    for login in self.accounts[site].keys():
		if (login == 'disabled'):
                    continue		

		self._logger.debug("Executing scraper '%s' for login '%s'",
                                   scraper.__name__, login)
		# Instantiate scraper for this login (and logs in)
                s = scraper.Scraper(login, self.accounts[site][login]['password'],
                                    self.accounts[site][login]['qa'])
		
		# Account Loop (ex. 'checking')
		for account in self.accounts[site][login]["accounts"]:
		    self._logger.debug("Account '%s' - ", account)
		    date = self.drive.get_latest_from_folder(
					self.accounts[site][login]["accounts"][account]['drive_id'])
		    self._logger.debug("Last Drive statement date: %s", str(date))

		    # Check if this account has new documents
		    if s.hasNew(self.accounts[site][login]["accounts"][account], date):
			try:
			    self._logger.debug("New statement(s) found. Downloading...")
			    s.scrape(self.accounts[site][login]["accounts"][account], date)
			except:
			    self._logger.error('Failed to execute scraper',
                                               exc_info=True)
			else:
			    self._logger.debug("Scrape by scraper '%s' completed",
                                       scraper.__name__)
                    	    self._logger.info("Found %d new statements to file", len([name for \
				name in os.listdir(filerpath.TMP_PATH) if os.path.isfile(name)]))
                    	    
			    # Add files to drive
			    for file in os.listdir(filerpath.TMP_PATH):
			    	self.drive.add_file_to_folder(file, os.path.join(filerpath.TMP_PATH, 
										 file), 
					self.accounts[site][login]["accounts"][account]['drive_id'])
			        self._logger.debug("File '%s' saved to Drive", file)
		    	    #delete files from tmp
			    for the_file in os.listdir(filerpath.TMP_PATH):
    				file_path = os.path.join(filerpath.TMP_PATH, the_file)
    				try:
        			    if os.path.isfile(file_path):
            				os.unlink(file_path)
					self._logger.debug("File '%s' deleted from tmp", the_file)
    				except Exception, e:
        			    self._logger.warning(e)
		    else:
			self._logger.info("No new statements for '%s' ",
                                   account)
        

    
