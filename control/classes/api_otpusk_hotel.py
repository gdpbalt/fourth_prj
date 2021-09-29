from control.classes.api_otpusk import MethodOtpusk


class MethodHotel(MethodOtpusk):
    @staticmethod
    def parse_result(input_data: dict) -> dict:
        response = input_data.get('hotel', dict())
        if len(response.keys()) == 0:
            return response

        response = response.get('rb', dict())
        if len(response.keys()) == 0:
            return response

        response = response.get('1', dict())
        if len(response.keys()) == 0:
            return response

        output = dict()
        response = response.get('url')
        if response is not None:
            output['url'] = response
        return output

    def save_data2dbase(self):
        pass
