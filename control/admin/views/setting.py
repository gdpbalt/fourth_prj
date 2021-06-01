from flask import render_template
from flask_security import roles_accepted

from control import app
from control.settings import SEARCH_UPDATE_MINUTES, SEARCH_PAUSE_BETWEEN_REQUEST_SECOND, \
    SEARCH_SLEEP_WAIT_LASTRESULT_SECOND, SEARCH_STOP_AFTER_SECOND, SEARCH_STOP_AFTER_ERRORS, \
    SEARCH_TRY_AFTER_ERROR_HOURS

info = {
    'CRON_RUN': {
        'name': 'CRON_RUN',
        'comment': 'Как часто запускать автоматический поиску тура. '
                   'В первую очередь запрашиваются данные о турах по которым никогда не выполнялся поиск',
        'value': 10,
        'dimension': 'минут',
    },

    'SEARCH_UPDATE_MINUTES': {
        'name': 'SEARCH_UPDATE',
        'comment': 'Как часто обновлять туры в витринах. '
                   'После истечении этого времени будет предпринята попытка обновить тур.',
        'value': SEARCH_UPDATE_MINUTES,
        'dimension': 'минут',
    },

    'SEARCH_PAUSE_BETWEEN_REQUEST_SECOND': {
        'name': 'SEARCH_PAUSE_BETWEEN_REQUEST',
        'comment': 'Какую паузу делать между обращением к API Отпуска при автоматическом обновлении туров',
        'value': SEARCH_PAUSE_BETWEEN_REQUEST_SECOND,
        'dimension': 'секунды',
    },

    'SEARCH_SLEEP_WAIT_LASTRESULT_SECOND': {
        'name': 'SEARCH_SLEEP_WAIT_LASTRESULT',
        'comment': 'Какую паузу делать между обращением к API Отпуска при поиске тура. '
                   'В ходе обновления тура необходимо выполнить несколько запросов к API Отпуска',
        'value': SEARCH_SLEEP_WAIT_LASTRESULT_SECOND,
        'dimension': 'секунды',
    },

    'SEARCH_STOP_AFTER_SECOND': {
        'name': 'SEARCH_STOP_AFTER',
        'comment': 'Прекращать поиск после истечении этого времени',
        'value': SEARCH_STOP_AFTER_SECOND,
        'dimension': 'секунды',
    },

    'SEARCH_STOP_AFTER_ERRORS': {
        'name': 'SEARCH_STOP_AFTER_ERRORS',
        'comment': 'Кол-во ошибок, после которого не выполнять регулярное обновление туров',
        'value': SEARCH_STOP_AFTER_ERRORS,
        'dimension': '',
    },

    'SEARCH_TRY_AFTER_ERROR_HOURS': {
        'name': 'SEARCH_TRY_AFTER_ERROR',
        'comment': 'Повторить попытку поиска тура, после возникновения ошибки, если прошло столько времени. '
                   'Если обновление тура содержит ошибки, то увеличивается интервал авто-обновления',
        'value': SEARCH_TRY_AFTER_ERROR_HOURS,
        'dimension': 'часов',
    },
}


@app.route("/admin/setting")
@roles_accepted('admin')
def setting():
    return render_template("admin/settings.html", info=info)
