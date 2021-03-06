import abc
import requests
import logging
import filerpath
import os
import re
from oauth2client import tools



class ScraperBase(object):
    __metaclass__ = abc.ABCMeta    

    def __init__(self, username, password, qa, flags):
        self.s = requests.session()

	regex = re.compile('(?<=\')(.*)(?=\.)', re.MULTILINE)
        log_name = re.search(regex, str(type(self))).group()
        self._logger = logging.getLogger(log_name)
        self._logger.setLevel(getattr(logging, flags.logging_level))
	if not self._logger.handlers:
            log_path = os.path.join(filerpath.LOG_PATH, 'Filed.log')
            handler = logging.FileHandler(log_path)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self._logger.addHandler(handler)

        self.username = username
        self.password = password
        self.qa = qa
	self.flags = flags
	
        self._login()

    @abc.abstractmethod
    def _login(self):
	return	
    
    def _save(self, file, statement_date):
	# Create directory structure
        file_name = str(statement_date) + '.pdf'
        file_path = os.path.join(filerpath.TMP_PATH, file_name)

        self._logger.info("Downloaded statement '%s' ", file_name)

        # Save statement
        with open(file_path, "wb") as code:
            code.write(file.content)

        self._logger.info("Statement saved to '%s' ", file_path)

    @abc.abstractmethod
    def scrape(self, account, drive_date):
	return

    @abc.abstractmethod
    def hasNew(self, account, date):
	return 


