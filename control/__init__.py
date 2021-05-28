import os

from dotenv import load_dotenv
from flask import Flask, session
from flask_babelex import Babel
from flask_mail import Mail
from flask_security import SQLAlchemyUserDatastore, Security, user_registered
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from config import config

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
config_name = os.getenv('FLASK_CONFIG') or 'default'


app = Flask(__name__)
app.config.from_object(config[config_name])

db = SQLAlchemy(app)
migrate = Migrate(app, db)
babel = Babel(app)
mail = Mail(app)

from control.models import *

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

from control.views import *


@user_registered.connect_via(app)
def user_registered_sighandler(*args, **kwargs):
    # TODO вынести уведомление в лог
    print("Create new user. Args: {}. Kwargs: {}".format(args, kwargs))
    default_role = user_datastore.find_role('guest')
    user_datastore.add_role_to_user(kwargs['user'], default_role)
    db.session.commit()


@babel.localeselector
def get_locale():
    return session.get('lang', 'ru')
