from flask import render_template
from flask_security import roles_accepted

from control import app
from control import Showcase
from control.classes.api_my import GetHotBlock, GetHotTour
from control.settings import LANGS


@app.route("/admin/show")
@app.route("/admin/show/<int:index_in>/<string:lang_in>")
@roles_accepted('admin')
def show(index_in=None, lang_in=None):
    lang = 'rus'
    if lang_in is not None and lang_in in LANGS:
        lang = lang_in
    lang_id = LANGS.index(lang)

    showcases = Showcase.query.order_by(Showcase.order_index).all()
    index, name = 0, ''
    if index_in is None:
        if len(showcases) > 0:
            index = showcases[0].id
            name = showcases[0].name
    else:
        index = index_in
        for showcase in showcases:
            if showcase.id == index:
                name = showcase.name

    tours_list = GetHotBlock(index=index, lang_id=lang_id)
    tours_list.run()
    tours = list()
    for tour_id in tours_list.data:
        tour = GetHotTour(index=tour_id, lang_id=lang_id)
        tour.run()
        if tour.data is not None:
            tours.append(tour.data)

    number, tours_left, tours_right = 0, list(), list()
    for tour in tours:
        tour['number'] = number + 1
        if (number % 2) == 0:
            tours_left.append(tour)
        else:
            tours_right.append(tour)
        number += 1

    return render_template("admin/showroom.html",
                           showcases=showcases, tours_left=tours_left, tours_right=tours_right, langs=LANGS, lang=lang,
                           index=index, description=name)
