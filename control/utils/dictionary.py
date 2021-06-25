from control import app, cache
from control.models import OtpuskCoutries, OtpuskCities, OtpuskFromCities, OtpuskOperators
from control.models.otpusk_data import OtpuskPorts
from control.settings import STATIC_DATA, LANGS


@cache.memoize()
def get_country_name(country_id, lang_id):
    data = OtpuskCoutries.query.filter_by(otpusk_id=country_id, lang=lang_id).first()
    if data is None:
        msg = f'Error found country_id={country_id} in otpusk_countris'
        app.logger.error(msg)
        raise ValueError(msg)
    return data.name


@cache.memoize()
def get_city_name(city_id, lang_id):
    data = OtpuskCities.query.filter_by(otpusk_id=city_id, lang=lang_id).first()
    if data is None:
        msg = f'Error found city_id={city_id} in otpusk_cities'
        app.logger.error(msg)
        raise ValueError(msg)
    return data.name


@cache.memoize()
def get_from_city_name(city_from_id, lang_id):
    data = OtpuskFromCities.query.filter_by(otpusk_id=city_from_id, lang=lang_id).first()
    if data is None:
        msg = f'Error found city_from_id={city_from_id} in otpusk_from_cities'
        app.logger.error(msg)
        raise ValueError(msg)
    return data.rel


@cache.memoize()
def get_operators(operator_id, lang_id):
    data = OtpuskOperators.query.filter_by(otpusk_id=operator_id, lang=lang_id).first()
    if data is None:
        msg = f'Error found operator_id={operator_id} in otpusk_operators'
        app.logger.error(msg)
        raise ValueError(msg)
    return data.name


@cache.memoize()
def get_iata_city(iata_code: str, lang_id: int):
    lang = LANGS[lang_id]
    if lang in STATIC_DATA and 'port' in STATIC_DATA[lang] and iata_code in STATIC_DATA[lang]['port']:
        return STATIC_DATA[lang]['port'][iata_code]

    data = OtpuskPorts.query.filter_by(iata=iata_code, lang=lang_id).first()
    if data is None:
        return
    return data.name
