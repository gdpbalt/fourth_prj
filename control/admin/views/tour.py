# -*- coding: utf-8 -*-
import json

from flask import flash, url_for, render_template, jsonify, request
from flask_security import roles_accepted
from sqlalchemy import func, exc
from werkzeug.utils import redirect

from control import app, db
from control import Tour, TourSearch, TourError
from control.classes.api_otpusk_search import MethodSearch
from control.classes.mk_link import MakeSearchLink
from control.forms.forms import TourForm
from control.utils.reorder import move_record_in_table, reorder_record_in_table
from control.utils.request import get_method_link_append


@app.route("/admin/tour_add/<int:showcase_id>")
@roles_accepted('admin')
def tour_add(showcase_id):
    app.logger.debug(f"Add element showcase={showcase_id}")
    data = Tour()
    data.showcase_id = showcase_id
    max_order_index = db.session.query(func.max(Tour.order_index)).filter(Tour.showcase_id == showcase_id).scalar()
    if max_order_index is None:
        data.order_index = 1
    else:
        data.order_index = max_order_index + 1
    try:
        db.session.add(data)
        db.session.commit()

        db.session.refresh(data)
        msg = f"Добавлен новый тур id={data.id} в витрину id={showcase_id}"
        app.logger.info(msg)
        flash(msg, "info")
        return redirect(url_for("showcase_update", index=showcase_id))
    except exc.SQLAlchemyError as e:
        msg = f"При добавлении тура в витрину id={showcase_id} произошла ошибка"
        app.logger.warning(f"{msg}. {e}")
        flash(msg, "error")

    return render_template("admin/showcase_add.html")


@app.route("/admin/tour/<int:index>/<string:cmd>")
@roles_accepted('admin')
def tour_move(index, cmd):
    app.logger.debug(f"Move element id={index} '{cmd}'")
    data_current = Tour.query.get_or_404(index)
    showcase_id = data_current.showcase_id
    move_record_in_table(dbase=db, table=Tour, index=index, cmd=cmd)
    return redirect(url_for("showcase_update", index=showcase_id, tour_id=index) + f"#{index}")


@app.route("/admin/tour/<int:index>/del")
@roles_accepted('admin')
def tour_del(index):
    data = Tour.query.get_or_404(index)
    app.logger.debug(f"Delete element id={index}")

    tour_search_data = TourSearch.query.filter_by(tour_id=index).all()
    for record in tour_search_data:
        try:
            db.session.delete(record)
            db.session.commit()
        except exc.SQLAlchemyError as e:
            msg = f"При работе с базой произошла ошибка"
            app.logger.warning(f"{msg} {e}")
            flash(msg, "error")

    tour_error_data = TourError.query.filter_by(tour_id=index).all()
    for record in tour_error_data:
        try:
            db.session.delete(record)
            db.session.commit()
        except exc.SQLAlchemyError as e:
            msg = f"При работе с базой произошла ошибка"
            app.logger.warning(f"{msg} {e}")
            flash(msg, "error")

    try:
        db.session.delete(data)
        db.session.commit()
        msg = f"Тур id={data.id} успешно удален"
        app.logger.info(msg)
        flash(msg, "info")
    except exc.SQLAlchemyError as e:
        msg = f"При удалении тура {data.id} произошла ошибка"
        app.logger.warning(f"{msg}. {e}")
        flash(msg, "error")

    reorder_record_in_table(dbase=db, table=Tour)
    return redirect(url_for("showcase_update", index=data.showcase_id))


@app.route("/admin/tour/<int:index>/update", methods=["POST", "GET"])
@roles_accepted('admin')
def tour_update(index):
    data: Tour = Tour.query.get_or_404(index)
    app.logger.debug(f"Chg element id={index}")
    form = TourForm()

    if request.method != 'POST':
        form.destination.data = data.destination if data.destination is not None else form.destination.default
        form.active.data = data.active
        form.category.data = data.category_id if data.category_id is not None else form.category.default
        form.city.data = data.from_id if data.from_id is not None else form.city.default
        form.transport.data = data.transport_id if data.transport_id is not None else form.transport.default
        form.food.data = data.food_id if data.food_id is not None else form.food.default
        form.length.data = data.length_id if data.length_id is not None else form.length.default
        form.date_start.data = data.date_start if data.date_start is not None else form.date_start.default
        form.date_stop.data = data.date_stop

    elif form.validate_on_submit():
        data.destination = form.destination.data
        data.active = form.active.data
        data.category_id = form.category.data
        data.from_id = form.city.data
        data.transport_id = form.transport.data
        data.food_id = form.food.data
        data.length_id = form.length.data

        data.date_start = form.date_start.data
        data.date_stop = form.date_stop.data

        data_link = MakeSearchLink(index=index)
        data_link.run()
        data.link = data_link.link

        tour_search_data = TourSearch.query.filter_by(tour_id=index).all()
        for record in tour_search_data:
            try:
                db.session.delete(record)
                db.session.commit()
            except exc.SQLAlchemyError as e:
                msg = f"При работе с базой произошла ошибка"
                app.logger.warning(f"{msg}. {e}")
                flash(msg, "error")

        try:
            db.session.commit()
            msg = f"Данные о туре id={index} успешно обновлены"
            app.logger.info(msg)
            flash(msg, "info")
            return redirect(url_for("tour_update", index=index))
        except exc.SQLAlchemyError as e:
            msg = f"При изменении тура id={index} произошла ошибка"
            app.logger.warning(f"{msg}. {e}")
            flash(msg, "error")

    tour_search_data = TourSearch.query.filter_by(tour_id=index, lang=1).first()
    return render_template("admin/tour_update.html", showcase_id=data.showcase_id, tour_id=index, form=form,
                           tour=tour_search_data, link=data.link, token=get_method_link_append(), tour_info=data)


@app.route("/admin/tour/<int:index>/src")
@roles_accepted('admin')
def tour_search_scr(index):
    tour_search_data = TourSearch.query.filter_by(tour_id=index).first()
    data_str = json.loads(tour_search_data.src_json)
    return jsonify(data_str)


@app.route("/admin/tour/<int:index>/search")
@roles_accepted('admin')
def tour_search(index):
    data_tour: Tour = Tour.query.get(index)
    data = MethodSearch(index=index, url_link=data_tour.link)
    try:
        result = data.run()
    except Exception as e:
        flash("Ошибка получения данных от сервера", 'error')
        app.logger.info(f"Error get data. {e}")
    else:
        if result is None:
            flash("Ошибка получения данных от сервера", 'error')
    return redirect(url_for("tour_update", index=index))
