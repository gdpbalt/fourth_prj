import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

LANGS = ['rus', 'ukr']

OUR_SITE = 'https://antonivtours.com/tour'

SEARCH_UPDATE_MINUTES = 2 * 60

SEARCH_SLEEP_WAIT_LASTRESULT_SECOND = 6
SEARCH_PAUSE_BETWEEN_REQUEST_SECOND = 5
SEARCH_STOP_AFTER_SECOND = 19 * 60

SEARCH_STOP_AFTER_ERRORS = 3
SEARCH_TRY_AFTER_ERROR_HOURS = 6
SEARCH_DISABLE_AFTER_ERRORS = SEARCH_STOP_AFTER_ERRORS * 2 * 2  # Тур с ошибкой держится не больше 2х дней
SEARCH_DISABLE_AFTER_FAILED_UPATE_DAYS = 2

SEARCH_INTERVAL_DAYS = 14

REQUEST_HEADER = {
    "referer": "https://antonivtours.com/",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-GB,en;q=0.9,en-US;q=0.8,ml;q=0.7",
    "cache-control": "max-age=0",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) " +
                  "Ubuntu Chromium/71.0.3578.80 Chrome/71.0.3578.80 Safari/537.36"
}
