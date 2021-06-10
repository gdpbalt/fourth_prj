from flask import render_template, flash, url_for
from flask_security import roles_accepted
from sqlalchemy import exc, func
from werkzeug.utils import redirect

from control import app, db
from control.forms.forms import ShowcaseForm, ShowcaseUpdateForm
from control.models import Showcase, Tour
from control.utils.reorder import move_record_in_table, reorder_record_in_table


@app.route("/superuser/showcases")
@app.route("/showcases/<int:index>")
@roles_accepted('superuser')
def showcases(index=None):
    data = Showcase.query.order_by(Showcase.order_index).all()
    return render_template("superuser/showcases.html", showcases=data, index=index)


@app.route("/superuser/showcase/<int:index>/<string:cmd>")
@roles_accepted('superuser')
def showcase_move(index, cmd):
    app.logger.debug(f"Move element id={index} '{cmd}'")
    move_record_in_table(dbase=db, table=Showcase, index=index, cmd=cmd)
    return redirect(url_for("showcases", index=index))


@app.route("/superuser/showcase/<int:index>/del")
@roles_accepted('superuser')
def showcase_del(index):
    data = Showcase.query.get_or_404(index)
    app.logger.debug(f"Delete element id={index}")

    tours = Tour.query.filter_by(showcase_id=index).first()
    if tours is not None:
        msg = f"Витрина id={index} содержит туры. Сперва надо их удалить"
        app.logger.warning(msg)
        flash(msg, "error")
        return redirect(url_for("showcase_update", index=index))

    try:
        db.session.delete(data)
        db.session.commit()
        msg = f"Витрина id={data.id} успешно удалена"
        app.logger.info(msg)
        flash(msg, "info")
    except exc.SQLAlchemyError as e:
        msg = f"При удалении витрины {data.id} произошла ошибка"
        app.logger.warning(f"{msg}. {e}")
        flash(msg, "error")
    reorder_record_in_table(dbase=db, table=Showcase)
    return redirect(url_for("showcases"))


@app.route("/superuser/showcase_add", methods=["POST", "GET"])
@roles_accepted('superuser')
def showcase_add():
    form = ShowcaseForm()
    if form.validate_on_submit():
        data = Showcase()
        data.name = form.name.data
        app.logger.debug(f"Add element {data.name}")

        max_order_index = db.session.query(func.max(Showcase.order_index)).scalar()
        if max_order_index is None:
            data.order_index = 1
        else:
            data.order_index = max_order_index + 1
        try:
            db.session.add(data)
            db.session.commit()
            msg = f"Добавлена новая витрина '{data.name}'"
            app.logger.info(msg)
            flash(msg, "info")
            return redirect(url_for("showcases", index=data.id) + f"#{data.id}")
        except exc.SQLAlchemyError as e:
            msg = f"При добавлении витрины произошла ошибка"
            app.logger.warning(f"{msg}. {e}")
            flash(msg, "error")

    return render_template("superuser/showcase_add.html", form=form)


@app.route("/superuser/showcase/<int:index>/update", methods=["POST", "GET"])
@app.route("/superuser/showcase/<int:index>/update/<int:tour_id>", methods=["POST", "GET"])
@roles_accepted('superuser')
def showcase_update(index, tour_id=None):
    data = Showcase.query.get_or_404(index)
    tour = Tour.query.filter_by(showcase_id=index).order_by(Tour.order_index).all()
    form = ShowcaseUpdateForm()

    if form.validate_on_submit():
        data.name = form.name.data
        app.logger.debug(f"Chg element {index} {data.name}")
        try:
            db.session.commit()
            msg = f"Данные о витрине id={data.id} успешно обновлены"
            app.logger.info(msg)
            flash(msg, "info")
            return redirect(url_for("showcases", index=data.id) + f"#{data.id}")
        except exc.SQLAlchemyError as e:
            msg = f"При изменении витрины id={data.id} произошла ошибка"
            app.logger.warning(f"{msg}. {e}")
            flash(msg, "error")
    else:
        form.index.data = data.id
        form.name.data = data.name

    return render_template("superuser/showcase_update.html", showcase=data, form=form, tours=tour, tour_id=tour_id)
