import imp
import os
import logging
import pkgutil
import schedule
import time
import sys
import filer
import filerpath

def _CreateArgumentParser():
    try:
        import argparse
    except ImportError:
        return None
    parser = argparse.ArgumentParser(description='Filed - Get Organized', parents=[filer.argparser])
    parser.add_argument('--daemon', action='store_true',
                    help='Run Filed as a service')
    return parser

# argparser is an ArgumentParser that contains command-line options
argparser = _CreateArgumentParser()
flags = argparser.parse_args()


class Filed(object):
    def __init__(self):
        self._logger = logging.getLogger(__name__)
	self._logger.setLevel(getattr(logging, flags.logging_level))
	log_path = os.path.join(filerpath.LOG_PATH, 'Filed.log')
        # Create file handler to log to file
        fh = logging.FileHandler(log_path)
        fh.setLevel(getattr(logging, flags.logging_level))
        # Create console handler for stdout
        ch = logging.StreamHandler()
        ch.setLevel(getattr(logging, flags.logging_level))
        # Create formatter and add it to the handlers
	formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
	fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        # Add handlers to logger
	self._logger.addHandler(fh)
        self._logger.addHandler(ch)

	self.f = filer.Filer()

    def run(self):
        self.f.file()

if __name__ == "__main__":

    print("*******************************************************")
    print("*                 FILED - Get Organized               *")
    print("*                   2015 Will Kinard                  *")
    print("*******************************************************")

    logging.basicConfig()
    logger = logging.getLogger()

    logger.setLevel(getattr(logging, flags.logging_level))

    try:
        app = Filed()
	#schedule.every().day.at("22:30").do(app.run())
    except Exception:
        logger.error("Error occured!", exc_info=True)
        sys.exit(1)

    if flags.daemon:	
        while 1:
            schedule.run_pending()
            time.sleep(1)
    else:
        app.run()

