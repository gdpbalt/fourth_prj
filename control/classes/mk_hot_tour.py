from control.models import TourSearch, Tour
from datetime import timedelta
import copy

HOT_TOUR = {
    "searchedTour": {
        "data_view": {
        },
        "offers": [{}]  # TODO в эту структуру надо добавить другие предложеня
    },
    "api_version": "1",
    "time": 0,
    "updateTime": ""
}

HOT_TOUR_EMPTY = {
    "searchedTour": {
        "data_view": False
    },
    "api_version": "1",
    "time": 0
}


class TourBlock:
    format_date = '%Y-%m-%d'
    format_datetime_sec = f'{format_date} %H:%M:%S'
    format_datetime_min = f'{format_date} %H:%M'

    def __init__(self, index, lang_id):
        self.index = index
        self.lang_id = lang_id
        self.data = None
        self.tour = None
        self.response = None

    def get_data_from_db(self):
        self.tour: Tour = Tour.query.get(self.index)
        self.data: TourSearch = TourSearch.query.filter_by(tour_id=self.index, lang=self.lang_id).first()

    def make_response(self):
        if self.data is None:
            self.response = HOT_TOUR_EMPTY
            return

        self.response = copy.deepcopy(HOT_TOUR)

        self.response["errors"] = self.tour.errors
        self.response["errorLast"] = self.tour.errors_update.strftime(self.format_datetime_sec)

        self.response["updateTime"] = self.data.updated.strftime(self.format_datetime_sec)

        data_view = self.response['searchedTour']['data_view']
        data_view["hotelId"] = self.data.hotelId
        data_view["imgSrc"] = self.data.imgSrc
        data_view["hotelName"] = self.data.hotelName
        data_view["hotelStars"] = self.data.hotelStars
        data_view["fullHotelName"] = self.data.fullHotelName
        data_view["countryId"] = self.data.countryId
        data_view["countryName"] = self.data.countryName

        data_view["cityId"] = self.data.cityId
        data_view["cityName"] = self.data.cityName
        data_view["resortName"] = self.data.resortName
        if self.data.cityPortName is not None:
            data_view["cityPortName"] = self.data.cityPortName
        else:
            data_view["cityPortName"] = self.data.cityName
        data_view["cityPortIata"] = self.data.cityPortIata

        data_view["dateString"] = self.data.dateString.strftime(self.format_date)
        data_view["cityFromId"] = self.data.cityFromId
        data_view["cityFrom"] = self.data.cityFrom
        data_view["locationFromString"] = self.data.locationFromString
        data_view["foodString"] = self.data.foodString
        data_view["dateDurationString"] = self.data.dateDurationString
        data_view["operatorId"] = self.data.operatorId
        data_view["operatorName"] = self.data.operatorName
        data_view["promo"] = self.data.promo
        data_view["price"] = self.data.price
        data_view["currency"] = self.data.currency
        data_view["priceUsd"] = self.data.priceUsd
        data_view["priceEuro"] = self.data.priceEuro
        data_view["priceUah"] = self.data.priceUah
        data_view["priceUahOne"] = self.data.priceUahOne
        data_view["tourLink"] = self.data.tourLink
        data_view["transport"] = self.data.transport
        data_view["food"] = self.data.food
        data_view["length"] = self.data.length
        data_view["offerId"] = self.data.tour_api_id

        if all([x is not None for x in [self.data.locationLat, self.data.locationLng, self.data.locationZoom]]):
            data_view["location"] = dict()
            data_view["location"]['lat'] = self.data.locationLat
            data_view["location"]['lng'] = self.data.locationLng
            data_view["location"]['zoom'] = self.data.locationZoom

        if self.data.deptFrom is not None:
            data_view["deptFrom"] = self.data.deptFrom.strftime(self.format_datetime_min)
        else:
            data_view["deptFrom"] = self.data.dateString.strftime(self.format_datetime_min)

        if self.data.deptTo is not None:
            data_view["deptTo"] = self.data.deptTo.strftime('%Y-%m-%d %H:%M')
        else:
            stop_date = self.data.dateString + timedelta(days=self.data.length) - timedelta(days=1)
            data_view["deptTo"] = stop_date.strftime(self.format_datetime_min)

    def run(self):
        self.get_data_from_db()
        self.make_response()
