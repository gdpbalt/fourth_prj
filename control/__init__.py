import os

from dotenv import load_dotenv
from flask import Flask, session
from flask_admin import Admin
from flask_babelex import Babel
from flask_caching import Cache
from flask_mail import Mail
from flask_migrate import Migrate
from flask_security import SQLAlchemyUserDatastore, Security, user_registered, password_reset, user_authenticated
from flask_security.signals import password_changed
from flask_sqlalchemy import SQLAlchemy

import control.settings
from config import config
from control.admin.models import MyAdminIndexView, UserView, RoleView

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
config_name = os.getenv('FLASK_CONFIG') or 'default'


app = Flask(__name__)
app.config.from_object(config[config_name])
config[config_name].init_app(app)


db = SQLAlchemy(app)
migrate = Migrate(app, db)
babel = Babel(app)
mail = Mail(app)
cache = Cache(app)


from control.models import *
from control.forms.users import ExtendedRegisterForm, ExtendedForgotPasswordForm, ExtendedResetPasswordForm, \
    ExtendedLoginForm


admin = Admin(app=app, name='AntonivTours', template_mode='bootstrap4', base_template='admin/admin-base.html',
              index_view=MyAdminIndexView())
admin.add_view(UserView(User, db.session, name='Пользователи'))
admin.add_view(RoleView(Role, db.session, name='Роли'))


user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore,
                    register_form=ExtendedRegisterForm,
                    forgot_password_form=ExtendedForgotPasswordForm,
                    reset_password_form=ExtendedResetPasswordForm,
                    login_form=ExtendedLoginForm)


from control.views import *
from control.superuser.views import *
from control.api.views import *


@user_authenticated.connect_via(app)
def user_authenticated_sighandler(*args, **kwargs):
    user = kwargs['user']
    roles = [role.name for role in current_user.roles]
    app.logger.info("User '{}' logged in ({}). Args: {}. Kwargs: {}".format(user.email, roles, args, kwargs))


@user_registered.connect_via(app)
def user_registered_sighandler(*args, **kwargs):
    user = kwargs['user']
    app.logger.info("New user created '{}'. Args: {}. Kwargs: {}".format(user.email, args, kwargs))

    default_role = user_datastore.find_role('guest')
    user_datastore.add_role_to_user(user, default_role)
    db.session.commit()


@password_reset.connect_via(app)
def user_password_reset_sighandler(*args, **kwargs):
    user = kwargs['user']
    app.logger.info("User '{}' reset password. Args: {}. Kwargs: {}".format(user.email, args, kwargs))


@password_changed.connect_via(app)
def user_password_changed_sighandler(*args, **kwargs):
    user = kwargs['user']
    app.logger.info("User '{}' change password. Args: {}. Kwargs: {}".format(user.email, args, kwargs))


@babel.localeselector
def get_locale():
    return session.get('lang', 'ru')
