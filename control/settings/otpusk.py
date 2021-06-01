from .root import TOKEN, LANGS

API_URL_PRIMARY = 'https://api.otpusk.com/api/2.4/tours'

API = {
    'image_host': 'https://newimg.otpusk.com',

    'token_name': 'access_token',
    'token_value': TOKEN,

    'lang_name': 'lang',
    'lang_value': LANGS[0],

    'people_name': 'people',
    'people_value': 2,

    'method_search': 'search',
    'method_suggests': 'suggests',
    # 'method_static': 'static',
    # 'method_countries': 'countries',
    # 'method_cities': 'cities',
    # 'method_from_cities': 'fromCities',
    # 'method_operators': 'operators',
}
