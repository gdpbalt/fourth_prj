# -*- coding: utf-8 -*-
import sentry_sdk
from flask import Flask
from flask_caching import Cache
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sentry_sdk.integrations.flask import FlaskIntegration

from control.settings import *
from control.utils.utils_logger import logger_init

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["ROPAGATE_EXCEPTIONS"] = True
app.config['JSON_SORT_KEYS'] = False

if USE_LOG_SENTRY:
    sentry_sdk.init(dsn=SENTRY_URL,
                    integrations=[FlaskIntegration()],
                    ignore_errors=SENTRY_IGNORE_ERRORS,
                    traces_sample_rate=SENTRY_RATE)

db = SQLAlchemy(app)
manager = LoginManager(app)
migrate = Migrate(app, db)
app.config.from_mapping(cache_config)
cache = Cache(app)
logger_init(app)

from control import models

from control.routers.routes import *
from control.routers.routers_api import *
from control.routers.routers_auth import *
from control.routers.routers_error import *
from control.routers.routers_setting import *
from control.routers.routers_show import *
from control.routers.routers_showcase import *
from control.routers.routers_tour import *
from control.routers.routers_users import *
