import datetime

from control import app


def parse_date(date_str: str):
    try:
        mydate = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError as err:
        msg = f"Error input date string. {err}"
        app.logger.error(msg)
        raise ValueError(msg)
    return mydate


def parse_int(int_str: str):
    try:
        mynum = int(int_str)
    except ValueError as err:
        msg = f"Error input int string. {err}"
        app.logger.error(msg)
        raise ValueError(msg)
    return mynum


def parse_float(float_str: str):
    try:
        mynum = float(float_str)
    except ValueError as err:
        msg = f"Error input float string. {err}"
        app.logger.error(msg)
        raise ValueError(msg)
    return mynum


def decimal2str_with_space(num: int):
    return "{:,}".format(num).replace(",", " ")
