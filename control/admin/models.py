import uuid

from flask_admin import expose, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_security import current_user
from flask_security import utils


def check_role():
    if not current_user.is_active or not current_user.is_authenticated:
        return False
    if current_user.has_role('superuser'):
        return True
    return False


class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        return self.render('admin/index.html')

    def is_accessible(self):
        return check_role()


class UserView(ModelView):
    column_list = ('id', 'email', 'active',
                   'current_login_at', 'last_login_at', 'current_login_ip', 'last_login_ip', 'login_count')
    column_sortable_list = column_list
    form_columns = ('roles', 'email', 'password', 'active')
    column_filters = ['email']

    def on_model_change(self, form, model, is_created):
        model.password = utils.hash_password(model.password)
        if is_created:
            model.fs_uniquifier = uuid.uuid4().hex

    def is_accessible(self):
        result = check_role()
        if result:
            self.can_create, self.can_edit, self.can_delete, self.can_export = True, True, True, False
        return result


class RoleView(ModelView):
    column_list = ('id', 'name', 'description')
    column_sortable_list = column_list
    column_default_sort = 'id'

    def is_accessible(self):
        result = check_role()
        if result:
            self.can_create, self.can_edit, self.can_delete, self.can_export = True, True, True, False
        return result


class LangView(ModelView):
    column_list = ('id', 'name')
    column_sortable_list = column_list


class TourCategoryView(ModelView):
    column_list = ('id', 'name', 'order_index', 'selected', 'value')
    column_sortable_list = column_list


class TourTransportView(ModelView):
    column_list = ('id', 'name', 'order_index', 'selected', 'value')
    column_sortable_list = column_list


class TourFoodView(ModelView):
    column_list = ('id', 'name', 'order_index', 'selected', 'value')
    column_sortable_list = column_list


class TourLengthView(ModelView):
    column_list = ('id', 'name', 'order_index', 'selected', 'nights_from', 'nights_to')
    column_sortable_list = column_list


class TourFromView(ModelView):
    column_list = ('id', 'name', 'order_index', 'selected', 'value')
    column_sortable_list = column_list
