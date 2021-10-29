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

TRIPADVISER_GET_URL_FROM_OTPUSK_AFTER_DAYS = 30

TRIPADVISER_GET_CONTENT_FROM_SITE_AFTER_MINUTES = 60*3
TRIPADVISER_GET_CONTENT_FROM_SITE_AFTER_NETWORK_ERROR_MINUTES = 5
TRIPADVISER_GET_CONTENT_FROM_SITE_AFTER_PARSE_ERROR_MINUTES = 60 * 24

REQUEST_HEADER = {
    "referer": "https://antonivtours.com/",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) " +
                  "Ubuntu Chromium/71.0.3578.80 Chrome/71.0.3578.80 Safari/537.36"
}
