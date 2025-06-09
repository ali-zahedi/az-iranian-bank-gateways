import logging
from json import dumps, loads
from time import gmtime, strftime

from zeep import Client, Transport

from azbankgateways.banks import BaseBank
from azbankgateways.exceptions import SettingDoesNotExist
from azbankgateways.exceptions.exceptions import BankGatewayRejectPayment
from azbankgateways.models import BankType, CurrencyEnum, PaymentStatus


class Mellat(BaseBank):
    _terminal_id = None
    _user_name = None
    _user_password = None

    def __init__(self, **kwargs):
        super(Mellat, self).__init__(**kwargs)
        self.set_gateway_currency(CurrencyEnum.IRR)
        self._token_api_url = "https://bpm.shaparak.ir/pgwchannel/services/pgw?wsdl"
        self._payment_url = "https://bpm.shaparak.ir/pgwchannel/startpay.mellat"
        self._verify_api_url = self._token_api_url

    def get_bank_type(self):
        return BankType.MELLAT

    def set_default_settings(self):
        for item in ["TERMINAL_ID", "USER_NAME", "USER_PASSWORD"]:
            if item not in self.default_setting_kwargs:
                raise SettingDoesNotExist()
            setattr(self, f"_{item.lower()}", self.default_setting_kwargs[item])

    def get_pay_data(self):
        data = {
            "terminalId": self._terminal_id,
            "userName": self._user_name,
            "userPassword": self._user_password,
            "orderId": self.get_tracking_code(),
            "amount": self.get_gateway_amount(),
            "localDate": datetime.datetime.now().strftime("%Y%m%d"),
            "localTime": datetime.datetime.now().strftime("%H%M%S"),
            "callBackUrl": self._get_gateway_callback_url(),
            "payerId": 0,
        }
        return data

    def prepare_pay(self):
        super(Mellat, self).prepare_pay()

    def pay(self):
        super(Mellat, self).pay()
        data = self.get_pay_data()
        response = self._send_data(self._token_api_url, "bpPayRequest", data)
        result = response.split(",")
        if result[0] == "0":
            self._set_reference_number(result[1])
        else:
            raise BankGatewayRejectPayment(f"Mellat response code: {result[0]}")

    def _get_gateway_payment_method_parameter(self):
        return "GET"

    def _get_gateway_payment_url_parameter(self):
        return self._payment_url

    def _get_gateway_payment_parameter(self):
        return {"RefId": self.get_reference_number()}

    def get_verify_data(self):
        super(Mellat, self).get_verify_data()
        return {
            "terminalId": self._terminal_id,
            "userName": self._user_name,
            "userPassword": self._user_password,
            "orderId": self.get_tracking_code(),
            "saleOrderId": self.get_tracking_code(),
            "saleReferenceId": self.get_reference_number(),
        }

    def verify(self, transaction_code):
        super(Mellat, self).verify(transaction_code)
        data = self.get_verify_data()
        response = self._send_data(self._verify_api_url, "bpVerifyRequest", data)
        if response == "0":
            self._set_payment_status(PaymentStatus.COMPLETE)
        else:
            self._set_payment_status(PaymentStatus.CANCEL_BY_USER)

    def _send_data(self, url, method, data):
        try:
            client = zeep.Client(wsdl=url)
            return getattr(client.service, method)(**data)
        except Exception as e:
            logging.exception(f"Mellat gateway error during {method}: {e}")
            raise BankGatewayConnectionError()

    def prepare_verify_from_gateway(self):
        super(Mellat, self).prepare_verify_from_gateway()
        request = self.get_request()
        ref_id = request.POST.get("SaleReferenceId")
        if not ref_id:
            raise BankGatewayStateInvalid
        self._set_reference_number(ref_id)
        self._set_bank_record()

    def verify_from_gateway(self, request):
        super(Mellat, self).verify_from_gateway(request)
 
