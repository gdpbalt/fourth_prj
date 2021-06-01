import logging
import os
from logging.handlers import RotatingFileHandler, SysLogHandler

from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
dotenv_path = os.path.join(basedir, '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s - %(filename)s:%(lineno)d - %(process)d"
DATE_FORMAT = '%Y-%m-%d %H:%M'


class Config:
    WTF_CSRF_ENABLED = True

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'cii4theetoo7ChieweeH'

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SECURITY_REGISTERABLE = True
    SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT') or 'om8foh9uoDeechiexe7k'
    SECURITY_RECOVERABLE = True
    SECURITY_CHANGEABLE = True
    SECURITY_TRACKABLE = True
    SECURITY_SEND_REGISTER_EMAIL = True
    SECURITY_SEND_PASSWORD_CHANGE_EMAIL = True
    SECURITY_SEND_PASSWORD_RESET_EMAIL = True

    RECAPTCHA_USE_SSL = False
    RECAPTCHA_PUBLIC_KEY = '6LfSPfwaAAAAAG3XabESGyF0pEow0rlQfgpOpX9v'
    RECAPTCHA_PRIVATE_KEY = '6LfSPfwaAAAAANufTxsA1ENwyVIBPCArUXQPXqV8'
    RECAPTCHA_OPTIONS = {'theme': 'black'}

    MAIL_DEBUG = False
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'localhost'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'test@localhost'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or 'a secrete password'
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or 'test@localhost'
    MAIL_PORT = os.environ.get('MAIL_PORT') or 25
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False

    LOG_LEVEL = logging.DEBUG
    LOG_SCREAM_USE = True
    LOG_SCREAM_LEVEL = LOG_LEVEL
    LOG_FILE_ROTATE_USE = True
    LOG_FILE_ROTATE_LEVEL = LOG_LEVEL
    LOG_FILE_ROTATE_NAME = 'proj_name.log'
    LOG_FILE_ROTATE_SIZE = int(os.environ.get('LOG_FILE_SIZE')) or 1000000
    LOG_FILE_ROTATE_COUNT = int(os.environ.get('LOG_FILE_COUNT')) or 10
    LOG_SYSLOG_USE = False
    LOG_SYSLOG_LEVEL = LOG_LEVEL
    LOG_SYSLOG_ADDR = os.environ.get('SYSLOG_LOG_ADDR') or '127.0.0.1'
    LOG_SYSLOG_PORT = os.environ.get('SYSLOG_LOG_PORT') or 514

    LOG_SENTRY_USE = False
    LOG_SENTRY_RATE = 1.0
    LOG_SENTRY_URL = "https://9742568ba7824d3aa5723e71171eaab5@o620982.ingest.sentry.io/5751742"
    LOG_SENTRY_IGNORE_ERRORS = [KeyboardInterrupt]

    ROPAGATE_EXCEPTIONS = True
    JSON_SORT_KEYS = False

    CACHE_TYPE = 'SimpleCache'
    CACHE_DEFAULT_TIMEOUT = 5

    @classmethod
    def init_app(cls, app):
        while app.logger.hasHandlers():
            app.logger.removeHandler(app.logger.handlers[0])
        app.logger.setLevel(cls.LOG_LEVEL)

        if cls.LOG_SCREAM_USE:
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(logging.Formatter("%(levelname)s - %(message)s"))
            stream_handler.setLevel(cls.LOG_SCREAM_LEVEL)
            app.logger.addHandler(stream_handler)

        if cls.LOG_FILE_ROTATE_USE:
            file_handle = RotatingFileHandler(filename=cls.LOG_FILE_ROTATE_NAME,
                                              maxBytes=cls.LOG_FILE_ROTATE_SIZE,
                                              backupCount=cls.LOG_FILE_ROTATE_COUNT,
                                              encoding='utf-8')
            file_handle.setLevel(cls.LOG_FILE_ROTATE_LEVEL)
            file_handle.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))
            app.logger.addHandler(file_handle)

        if cls.LOG_SYSLOG_USE:
            syslog_handler = SysLogHandler(address=(cls.LOG_SYSLOG_ADDR, cls.LOG_SYSLOG_PORT))
            syslog_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))
            syslog_handler.setLevel(cls.LOG_SYSLOG_LEVEL)
            app.logger.addHandler(syslog_handler)


class DevelopmentConfig(Config):
    DEBUG = True
    LOG_LEVEL = logging.DEBUG
    LOG_SCREAM_USE = True
    LOG_FILE_ROTATE_USE = True
    LOG_FILE_ROTATE_NAME = os.path.join(basedir, 'logs', os.environ.get('LOG_FILE_NAME') or 'proj_name.log')

    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')


class ProductionConfig(Config):
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}
