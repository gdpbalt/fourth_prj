import datetime

from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, DateField, BooleanField
from wtforms.validators import DataRequired, Length, ValidationError

from control import db
from control.models import TourCategory, TourFrom, TourTransport, TourFood, TourLength


class ShowcaseForm(FlaskForm):
    MESSAGE_NAME = 'Длина должна быть от 2 до 255 символов'

    name = StringField('Наименование витрины',
                       validators=[Length(min=2, max=255, message=MESSAGE_NAME), DataRequired()],
                       render_kw={"placeholder": "Введите наименование"})


class ShowcaseUpdateForm(FlaskForm):
    index = IntegerField('ID витрины', render_kw={'readonly': True})
    name = StringField('Наименование витрины',
                       validators=[Length(min=2, max=255, message=ShowcaseForm.MESSAGE_NAME), DataRequired()],
                       render_kw={"placeholder": "Введите наименование"})


def compare_date_start_stop(form, field):
    if field.data < form.date_start.data:
        raise ValidationError('Date_stop have to be great than date_start')


class TourForm(FlaskForm):
    index = IntegerField('ID места назначения', validators=[DataRequired()], render_kw={'readonly': True})
    active = BooleanField('Тур участвует в формировании витрины горящих', validators=[], default=True)
    destination = StringField('Страна, курорт или отель',
                              validators=[Length(min=2, max=100), DataRequired()], default='')
    date_start = DateField('Начало тура (от)', validators=[DataRequired()], format='%Y-%m-%d')
    date_stop = DateField('Начало тура (до)', validators=[DataRequired(), compare_date_start_stop], format='%Y-%m-%d')
    category = SelectField("Категория отеля", validators=[DataRequired()], coerce=int)
    city = SelectField("Город вылета", validators=[DataRequired()], coerce=int)
    transport = SelectField("Транспорт", validators=[DataRequired()], coerce=int)
    food = SelectField("Питание", validators=[DataRequired()], coerce=int)
    length = SelectField("Длительность", validators=[DataRequired()], coerce=int)

    def __init__(self, *args, **kwargs):
        super(TourForm, self).__init__(*args, **kwargs)

        self.category.choices = self.get_data_for_select(TourCategory)
        self.category.default = self.get_data_for_select_selected(TourCategory)

        self.city.choices = self.get_data_for_select(TourFrom)
        self.city.default = self.get_data_for_select_selected(TourFrom)

        self.transport.choices = self.get_data_for_select(TourTransport)
        self.transport.default = self.get_data_for_select_selected(TourTransport)

        self.food.choices = self.get_data_for_select(TourFood)
        self.food.default = self.get_data_for_select_selected(TourFood)

        self.length.choices = self.get_data_for_select(TourLength)
        self.length.default = self.get_data_for_select_selected(TourLength)

        self.date_start.default = datetime.datetime.now().date() + datetime.timedelta(days=1)

    @staticmethod
    def get_data_for_select(model):
        return [(c.id, c.name) for c in db.session.query(model).order_by(model.order_index).all()]

    @staticmethod
    def get_data_for_select_selected(model):
        selected = db.session.query(model).filter_by(selected=True).first()
        if selected is not None:
            return selected.id
        else:
            row = db.session.query(model).order_by(model.order_index).first()
            if row is not None:
                return row.id
