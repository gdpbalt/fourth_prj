from control import MethodSuggests, Tour, TourFrom, TourCategory, TourTransport, TourFood, TourLength
from control import app
from control.classes.api_otpusk import MethodError
from control.settings import API
from control.utils.request import get_method_link_prepend, get_method_link_append


class MakeSearchLink:
    METHOD = API['method_search']

    def __init__(self, index: int):
        self.index = index
        self.link = None
        self.tour = None
        self.params = list()

    def get_data_from_db(self):
        self.tour = Tour.query.get(self.index)
        if self.tour is None:
            msg = f'Tour id={self.index} not found in database'
            app.logger.error(msg)
            raise ValueError(msg)

    def get_method_url(self):
        self.link = get_method_link_prepend(self.METHOD)
        self.get_destination()
        self.get_from()
        self.get_stars()
        self.get_date()
        self.get_length()
        self.params.append('{}={}'.format(API['people_name'], API['people_value']))
        self.get_food()
        self.get_transport()
        self.link += '{}&{}'.format('&'.join(self.params), get_method_link_append(lang=API['lang_value']))

    def get_destination(self):
        destination = self.tour.destination
        values = MethodSuggests(text=destination)
        values.run()

        found_id = None
        for record in values.data:
            if record['name'] == destination:
                found_id = record['id']

        if found_id is not None:
            self.params.append('to={}'.format(found_id))
        else:
            msg = f"Not found '{destination}' in API suggests method"
            app.logger.error(msg)
            raise MethodError(msg)

    def get_from(self):
        data = TourFrom.query.get(self.tour.from_id)
        self.params.append(f'from={data.value}')

    def get_stars(self):
        data = TourCategory.query.get(self.tour.category_id)
        if data.value != 'any':
            self.params.append(f'stars={data.value}')

    def get_date(self):
        start = self.tour.date_start
        self.params.append('checkIn={}'.format(start.strftime('%Y-%m-%d')))

        stop = self.tour.date_stop
        self.params.append('checkTo={}'.format(stop.strftime('%Y-%m-%d')))

    def get_transport(self):
        data = TourTransport.query.get(self.tour.transport_id)
        if data.value != 'any':
            self.params.append(f'transport={data.value}')

    def get_food(self):
        data = TourFood.query.get(self.tour.food_id)
        if data.value != 'any':
            self.params.append(f'food={data.value}')

    def get_length(self):
        data = TourLength.query.get(self.tour.length_id)
        self.params.append('length={}'.format(data.nights_from + 1))

        if data.nights_from != 30:
            self.params.append('lengthTo={}'.format(data.nights_to + 1))

    def run(self):
        self.get_data_from_db()
        self.get_method_url()
