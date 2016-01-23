import os

# Filer main directory
APP_PATH = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), os.pardir))

LIB_PATH = os.path.join(APP_PATH, "Filed")
SCRAPER_PATH = os.path.join(LIB_PATH, "scrapers")

ACCOUNTS_PATH = os.path.join(LIB_PATH, "accounts.json")

TMP_PATH = os.path.join(LIB_PATH, "tmp")

LOG_PATH = os.path.join(LIB_PATH, "logs")

CRED_PATH = os.path.join(LIB_PATH, ".credentials")
