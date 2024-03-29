import itertools

from flask import render_template
from flask_security import roles_accepted

from control import app
from control.classes.api_my import GetHotBlock, GetHotTour
from control.models import Showcase
from control.settings import LANGS


@app.route("/superuser/show")
@app.route("/superuser/show/<int:index_in>/<string:lang_in>")
@roles_accepted('superuser')
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
    number, tours_left, tours_right = 0, list(), list()
    for tour_id in tours_list.data:
        tour = GetHotTour(index=tour_id, lang_id=lang_id)
        tour.run()
        if tour.data is None:
            continue
        tour.data['number'] = number + 1

        if (number % 2) == 0:
            tours_left.append(tour.data)
        else:
            tours_right.append(tour.data)
        number += 1

    tours = list(itertools.zip_longest(tours_left, tours_right, fillvalue=False))
    return render_template("superuser/showroom.html",
                           showcases=showcases, langs=LANGS, lang=lang, index=index, description=name, tours=tours)
