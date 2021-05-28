import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
dotenv_path = os.path.join(basedir, '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'cii4theetoo7ChieweeH'

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SECURITY_REGISTERABLE = True
    SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT') or 'om8foh9uoDeechiexe7k'
    SECURITY_SEND_REGISTER_EMAIL = True
    SECURITY_RECOVERABLE = True
    SECURITY_CHANGEABLE = True
    SECURITY_TRACKABLE = True
    # TODO
    # SECURITY_POST_LOGIN_VIEW - default /

    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'localhost'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'test@localhost'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or 'a secrete password'
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or 'test@localhost'
    MAIL_PORT = os.environ.get('MAIL_PORT') or 25
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
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
