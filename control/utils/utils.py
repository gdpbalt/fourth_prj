from flask import flash
from sqlalchemy import exc


def move_record_in_table(dbase, table, index, cmd):
    min_order_index = 1
    max_order_index = 255

    data_current = dbase.session.query(table).get(index)
    if data_current is None:
        return

    order_index_old = data_current.order_index
    order_index_new, is_change, text = (None, False, None)
    if cmd == "up":
        if order_index_old > min_order_index:
            is_change = True
            order_index_new = order_index_old - 1
            text = f"Перемистили витрину id={index} вверх"
    else:
        if order_index_old < max_order_index:
            is_change = True
            order_index_new = order_index_old + 1
            text = f"Перемистили витрину id={index} вниз"

    if is_change is False:
        return

    data = dbase.session.query(table).filter_by(order_index=order_index_new).all()
    for el in data:
        el.order_index = order_index_old
        try:
            dbase.session.commit()
        except exc.SQLAlchemyError as e:
            flash(f"При изменении сортировки произошла ошибка ({e})", "error")

    data_current.order_index = order_index_new
    try:
        dbase.session.commit()
        flash(text, "info")
    except exc.SQLAlchemyError as e:
        flash(f"При изменении сортировки произошла ошибка ({e})", "error")


def reorder_record_in_table(dbase, table):
    data = dbase.session.query(table).order_by(table.order_index).all()
    order_index_new = 0
    for el in data:
        order_index_new += 1
        el.order_index = order_index_new
        try:
            dbase.session.commit()
        except exc.SQLAlchemyError as e:
            flash(f"При работе с базой данных произошла ошибка ({e})", "error")
