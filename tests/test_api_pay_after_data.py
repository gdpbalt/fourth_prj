from unittest import TestCase


class TestAPIPayBeforeData(TestCase):
    pay_response = {
        "id": "2642012700808438",
        "date": "Tue Jul 20 2021 19:15:34 GMT+0300 (Восточная Европа, летнее время)",
        "wayforpayPayment": {
            "merchantAccount": "antonivtour_com1",
            "merchantSignature": "99a5ac241e3b5ce06527065ada02bba3",
            "orderReference": "1626797657106",
            "amount": 10,  # ***
            "currency": "UAH",  # ***
            "authCode": "967406",
            "email": "gdp@odev.io",
            "phone": "380503266374",
            "createdDate": 1626797658,  # ***
            "processingDate": 1626797734,
            "cardPan": "53****2440",
            "cardType": "MasterCard",
            "issuerBankCountry": "Ukraine",
            "issuerBankName": "ПУМБ",
            "transactionStatus": "Approved",  # ***
            "reason": "Ok",  # ***
            "reasonCode": 1100,
            "fee": 0.22,
            "paymentSystem": "card",
            "clientStartTime": "1626797657107"
        }
    }

    def test_data_parse_ok(self):
        pass
