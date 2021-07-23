from unittest import TestCase

from pydantic import ValidationError

from control.models.api_pay_before_data import PayBeforeData


class TestAPIPayBeforeData(TestCase):
    arr = dict()
    arr['first_default_request'] = {
        "advert": "",
        "withoutDiscount": True,
        "manager": "",
        "contest1": "No",
        "passports": {},
        "client": {
            "name": "TEST TESTIKOV",
            "adress": {
                "region": "",
                "city": "",
                "street": "",
                "house": "",
                "appartment": "", "zip": ""
            },
            "email": "",
            "phone": "+0503266374"
        },
        "payment": {},
        "offer": {
            "id": "1352142510841417",
            "url": "https://antonivtours.com/palayuchi-putivki/hot/tour/turkey/rios_beach_hotel/8018/1352142510841417"}
    }
    arr['full_fill_form'] = {
        "advert": "",
        "withoutDiscount": False,
        "manager": "",
        "passports": {
            "adults": [{
                "sex": "male",
                "number": "123123",  # необязательно
                "name": "TEST",
                "phone": "+380503266688",
                "country": "Україна",
                "series": "AA",  # необязательно
                "issue": "1234",  # необязательно
                "ended": "10.01.2029",  # необязательно
                "surName": "TESTIKOV",
                "birthday": "06.03.1975"
            }, {
                "sex": "male",
                "number": "222555",  # необязательно
                "name": "OKSANA",
                "phone": "+380503266699",  # необязательно
                "country": "Україна",
                "series": "BA",  # необязательно
                "issue": "6632",  # необязательно
                "ended": "20.12.2022",  # необязательно
                "surName": "YURTSAN",
                "birthday": "10.10.1976"
            }],
            "child": []
        },
        "contest1": "Yes",
        "client": {
            "name": "TEST TESTIKOV",
            "adress": {
                "region": "Киевская",
                "city": "Киев",
                "street": "Княжий Затон",
                "house": "1",
                "appartment": "25",
                "zip": "83016"
            },
            "email": "GDP@TEST.COM.UA",  # необязательно
            "phone": "+380503266688"
        },
        "payment": {},
        "offer": {
            "id": "1352142510841417",
            "url": "https://antonivtours.com/palayuchi-putivki/hot/tour/turkey/rios_beach_hotel/8018/1352142510841417"
        }
    }
    arr['partly_fill_form'] = {
        "advert": "",
        "withoutDiscount": True,
        "manager": "",
        "passports": {
            "adults": [{
                "sex": "male",
                "number": "",
                "name": "YURTSAN",
                "phone": "+380503266666",
                "country": "Україна",
                "series": "",
                "issue": "",
                "ended": "",
                "surName": "KHRYSTYNA",
                "birthday": "15.05.1990"
            }, {
                "sex": "male",
                "number": "",
                "name": "MARIA",
                "phone": "",
                "country": "Україна",
                "series": "",
                "issue": "",
                "ended": "",
                "surName": "YURTSAN",
                "birthday": "08.06.1990"
            }],
            "child": []
        },
        "contest1": "No",
        "client": {
            "name": "DMITRO TESTIKOV",
            "adress": {
                "region": "Киевская",
                "city": "г.Киев",
                "street": "Княжий Затон",
                "house": "",
                "appartment": "",
                "zip": "83016"
            },
            "email": "",
            "phone": "+380503266699"
        },
        "payment": {},
        "offer": {
            "id": "1352142510841417",
            "url": "https://antonivtours.com/palayuchi-putivki/hot/tour/turkey/rios_beach_hotel/8018/1352142510841417"
        }
    }
    arr['form_with_pay'] = {
        "advert": "",
        "withoutDiscount": True,
        "manager": "",
        "passports": {},
        "contest1": "No",
        "client": {
            "name": "TEST5 TESTIKOV",
            "adress": {
                "region": "",
                "city": "",
                "street": "",
                "house": "",
                "appartment": "",
                "zip": ""
            },
            "email": "",
            "phone": "+380633266374"
        },
        "payment": {
            "type": "partial_custom",
            "amount": 10,
            "currency": "UAH",
            "createdDate": 1626797658,
            "transactionStatus": "Approved",
            "reason": "Ok"},
        "offer": {
            "id": "2642012700808438",
            "url": "https://antonivtours.com/tour/turkey/pineta_club_hotel/7920/2642012700808438"
        }
    }

    empty_form = {}

    def test_data_parse_ok(self):
        number = 0
        for value in self.arr.values():
            try:
                data = PayBeforeData(**value)
            except ValidationError as error_msg:
                self.fail('Parse errors {}'.format(error_msg))
            else:
                number += 1
        self.assertEqual(number, len(self.arr.keys()))

    def test_data_parse_failed(self):
        with self.assertRaises(Exception) as context:
            data = PayBeforeData(**self.empty_form)
        self.assertIsInstance(context.exception, ValidationError)
