import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

LANGS = ['rus', 'ukr']

OUR_SITE = 'https://antonivtours.com/tour'

SEARCH_UPDATE_MINUTES = 3 * 60

SEARCH_PAUSE_BETWEEN_REQUEST_SECOND = 1 * 60
SEARCH_SLEEP_WAIT_LASTRESULT_SECOND = 6
SEARCH_STOP_AFTER_SECOND = 15 * 60
SEARCH_STOP_AFTER_ERRORS = 3
SEARCH_TRY_AFTER_ERROR_HOURS = 12
