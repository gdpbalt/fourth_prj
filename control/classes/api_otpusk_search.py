from typing import Optional

from sqlalchemy import exc

from control import app, db, TourError, Tour
from control.classes.api_otpusk_search_get import MethodSearchGet
from control.classes.api_otpusk_search_save import MethodSearchSave


class MethodSearch:
    def __init__(self, url_link, index: int):
        self.link: str = url_link
        self.index: int = index
        self.tour: Optional[Tour] = None
        self.log_prefix: Optional[str] = None
        self.error_name: str = 'Ошибка данных'
        self.obj_search: Optional[MethodSearchGet] = None
        self.obj_save: Optional[MethodSearchSave] = None
        self.hotel_min_offer: Optional[dict] = None

    def get_data_from_table_tour(self):
        self.tour = Tour.query.get(self.index)
        if self.tour is None:
            msg = f'Tour id={self.index} not found in database'
            app.logger.error(msg)
            raise ValueError(msg)
        self.log_prefix = 'Tour {}/{}'.format(self.tour.showcase_id, self.tour.id)

    @staticmethod
    def get_best_offer(hotel_offers):
        offers_list = list()
        for offer_el in hotel_offers.values():
            offers_list.append(offer_el)

        if len(offers_list) > 0:
            offers_list.sort(key=lambda el: el['p'])
            return offers_list[0]
        else:
            return dict()

    def get_best_hotel(self, hotels_record: dict, dept_record: dict):
        hotels_first_record = dict()
        for key, value in hotels_record.items():
            hotels_first_record = value
            break

        hotels_list = list()
        for hotel_id, hotel_detail in hotels_first_record.items():
            offers = hotel_detail.pop('offers', dict())
            hotel_detail['offer'] = self.get_best_offer(offers)
            hotel_detail['hotelId'] = hotel_id
            hotels_list.append(hotel_detail)

        if len(hotels_list) > 0:
            hotels_list.sort(key=lambda el: el['offer']['p'])
            hotels_list[0]['dept'] = dept_record
            return hotels_list[0]
        else:
            return dict()

    def save_error(self, error_text, error_description):
        msg = '{}. {}. {}'.format(error_text, self.log_prefix, error_description[:200])
        app.logger.warning(msg)

        self.tour.errors += 1
        app.logger.warning('{}. Errors: {}'.format(self.log_prefix, self.tour.errors))

        error = TourError()
        error.showcase_id = self.tour.showcase_id
        error.tour_id = self.tour.id
        error.name = error_text
        error.description = error_description[:200]
        error.errors = self.tour.errors

        try:
            db.session.add(error)
            db.session.commit()
        except exc.SQLAlchemyError as e:
            msg = f'Error work with database. {e}'
            app.logger.error(msg)
            raise ConnectionError(msg)

    def get_data_from_api(self):
        self.obj_search = MethodSearchGet(url_link=self.link, log_prefix=self.log_prefix)
        return self.obj_search.run()

    def save_tour_search2db(self, hotel_min_offer: dict):
        self.obj_save = MethodSearchSave(input_data=hotel_min_offer, index=self.index)
        return self.obj_save.run()

    def update_table_tour(self):
        if self.tour.errors == 0:
            return

        self.tour.errors = 0
        try:
            db.session.commit()
        except exc.SQLAlchemyError as e:
            msg = f'Error work with database. {e}'
            app.logger.error(msg)
            raise ConnectionError(msg)

    def run(self) -> bool:
        self.get_data_from_table_tour()

        if self.get_data_from_api() is False:
            self.save_error(error_text=self.obj_search.error_name,
                            error_description=self.obj_search.error_full)
            return False

        dept_record = self.obj_search.result.get('dept')
        if not isinstance(dept_record, dict):
            self.save_error(error_text=self.error_name,
                            error_description='Error get data from response. Dict dept is empty. JSON={}'.format(
                                self.obj_search.result))
            return False

        hotels_record = self.obj_search.result.get('hotels')
        if not isinstance(hotels_record, dict):
            self.save_error(error_text=self.error_name,
                            error_description='Error get data from response. Dict hotels is empty. JSON={}'.format(
                                self.obj_search.result))
            return False

        self.hotel_min_offer = self.get_best_hotel(hotels_record=hotels_record, dept_record=dept_record)
        if bool(self.hotel_min_offer) is False:
            self.save_error(error_text=self.error_name,
                            error_description='Error get data from response. Result is empty. JSON={}'.format(
                                self.obj_search.result))
            return False

        if self.save_tour_search2db(hotel_min_offer=self.hotel_min_offer) is False:
            self.save_error(error_text=self.obj_save.error_name,
                            error_description=self.obj_save.error_full)
            return False

        self.update_table_tour()

        return True
