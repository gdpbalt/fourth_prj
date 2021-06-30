import datetime

from sqlalchemy import exc

from control import app, db, OtpuskCoutries, OtpuskFromCities, OtpuskOperators, OtpuskCities
from control.models.otpusk_data import OtpuskPorts
from control.utils.convert import parse_int
from control.utils.request import get_data_from_request


class MethodError(Exception):
    pass


class MethodOtpusk:
    def __init__(self, link, lang_id):
        self.link = link
        self.lang_id = lang_id
        self.data = None

    @staticmethod
    def parse_result(input_data: dict):
        return input_data

    def save_data2dbase(self):
        pass

    def run(self):
        reuslt = get_data_from_request(self.link)
        self.data = self.parse_result(input_data=reuslt)
        self.save_data2dbase()


class MethodCountries(MethodOtpusk):
    @staticmethod
    def parse_result(input_data: dict):
        output_list = list()
        response = input_data.get('countries', dict())
        for record in response:
            output = dict()
            output['id'] = record['id']
            output['name'] = record['name']
            output_list.append(output)
        return output_list

    def save_data2dbase(self):
        number = 0
        for record in self.data:
            index, name = record['id'], record['name']
            number += 1

            result: OtpuskCoutries = OtpuskCoutries.query.filter_by(otpusk_id=index, lang=self.lang_id).first()
            if result is None:
                result = OtpuskCoutries(otpusk_id=index, lang=self.lang_id, name=name)
                db.session.add(result)
                app.logger.debug(f"[{number}] Add to otpusk_countris: {index} - {name}")
            else:
                result.name = name
                app.logger.debug(f"[{number}] Update otpusk_countris: {index} - {name}")

            try:
                db.session.commit()
            except exc.SQLAlchemyError as e:
                msg = f'Error work with database. {e}'
                app.logger.error(msg)
                raise ConnectionError(msg)


class MethodFromCities(MethodOtpusk):
    @staticmethod
    def parse_result(input_data: dict):
        output_list = list()
        response = input_data.get('fromCities', dict())
        for record in response:
            output = dict()
            output['id'] = record['id']
            output['name'] = record['name']
            output['rel'] = record['rel']
            output_list.append(output)
        return output_list

    def save_data2dbase(self):
        number = 0
        for record in self.data:
            index, name, rel = record['id'], record['name'], record['rel']
            number += 1

            result: OtpuskFromCities = OtpuskFromCities.query.filter_by(otpusk_id=index, lang=self.lang_id).first()
            if result is None:
                result = OtpuskFromCities(otpusk_id=index, lang=self.lang_id, name=name, rel=rel)
                db.session.add(result)
                app.logger.debug(f"[{number}] Add to otpusk_from_cities: {index} - {name}")
            else:
                result.name = name
                app.logger.debug(f"[{number}] Update otpusk_from_cities: {index} - {name}")

            try:
                db.session.commit()
            except exc.SQLAlchemyError as e:
                msg = f'Error work with database. {e}'
                app.logger.error(msg)
                raise ConnectionError(msg)


class MethodOperators(MethodOtpusk):
    @staticmethod
    def parse_result(input_data: dict):
        output_list = list()
        response = input_data.get('operators', dict())
        for record in response.values():
            output = dict()
            output['id'] = parse_int(int_str=record['id'])
            output['name'] = record['name']
            output_list.append(output)
        return output_list

    def save_data2dbase(self):
        number = 0
        for record in self.data:
            index, name = record['id'], record['name']
            number += 1

            result: OtpuskOperators = OtpuskOperators.query.filter_by(otpusk_id=index, lang=self.lang_id).first()
            if result is None:
                result = OtpuskOperators(otpusk_id=index, lang=self.lang_id, name=name)
                db.session.add(result)
                app.logger.debug(f"[{number}] Add to otpusk_operators: {index} - {name}")
            else:
                result.name = name
                app.logger.debug(f"[{number}] Update otpusk_operators: {index} - {name}")

            try:
                db.session.commit()
            except exc.SQLAlchemyError as e:
                msg = f'Error work with database. {e}'
                app.logger.error(msg)
                raise ConnectionError(msg)


class MethodCities(MethodOtpusk):
    def __init__(self, link, lang_id, country):
        super().__init__(link=link, lang_id=lang_id)
        self.country = country

    @staticmethod
    def parse_result(input_data: dict):
        output_list = list()
        response = input_data.get('cities', dict())
        for record in response:
            output = dict()
            output['id'] = record['id']
            output['name'] = record['name']
            output_list.append(output)
        return output_list

    def save_data2dbase(self):
        number = 0
        for record in self.data:
            index, name = record['id'], record['name']
            number += 1

            result: OtpuskCities = OtpuskCities.query.filter_by(otpusk_id=index, lang=self.lang_id).first()
            if result is None:
                result = OtpuskCities(otpusk_id=index, lang=self.lang_id, name=name, country=self.country)
                db.session.add(result)
                app.logger.debug(f"[{number}] Add to otpusk_cities: {index} - {name}")
            else:
                result.name = name
                result.update = datetime.datetime.now()
                app.logger.debug(f"[{number}] Update otpusk_cities: {index} - {name}")

            try:
                db.session.commit()
            except exc.SQLAlchemyError as e:
                msg = f'Error work with database. {e}'
                app.logger.error(msg)
                raise ConnectionError(msg)


class MethodPorts(MethodOtpusk):
    def __init__(self, link, lang_id, country):
        super().__init__(link=link, lang_id=lang_id)
        self.country = country

    def parse_result(self, input_data: dict):
        output_list = list()
        response = input_data.get('ports', dict())
        if isinstance(response, dict):
            for key, record in response.items():
                if len(iata := record['iata']) == 3:
                    output = dict()
                    output['id'] = record['airportId']
                    output['iata'] = iata.upper()
                    output['name'] = record['name']
                    output_list.append(output)
                else:
                    app.logger.warn("Error length. Country: {}, IATA: {}".format(self.country, iata))
        return output_list

    def save_data2dbase(self):
        number = 0
        for record in self.data:
            index, name, iata = record['id'], record['name'], record['iata']
            number += 1

            result: OtpuskCities = OtpuskPorts.query.filter_by(otpusk_id=index, lang=self.lang_id).first()
            if result is None:
                result = OtpuskPorts(otpusk_id=index, lang=self.lang_id, name=name, country=self.country, iata=iata)
                db.session.add(result)
                app.logger.debug(f"[{number}] Add to otpusk_ports: {index} - {iata} - {name}")
            else:
                result.name = name
                result.iata = iata
                app.logger.debug(f"[{number}] Update otpusk_ports: {index} - {iata} - {name}")

            try:
                db.session.commit()
            except exc.SQLAlchemyError as e:
                msg = f'Error work with database. {e}'
                app.logger.error(msg)
                raise ConnectionError(msg)
