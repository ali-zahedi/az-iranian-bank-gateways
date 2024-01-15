import json
import logging

import requests

from azbankgateways.banks import BaseBank
from azbankgateways.exceptions import BankGatewayConnectionError, SettingDoesNotExist
from azbankgateways.exceptions.exceptions import BankGatewayRejectPayment
from azbankgateways.models import BankType, CurrencyEnum, PaymentStatus
from azbankgateways.utils import get_json


class Jibit(BaseBank):
    _api_key = None
    _secret_key = None

    def __init__(self, **kwargs):
        super(Jibit, self).__init__(**kwargs)
        self.set_gateway_currency(CurrencyEnum.IRR)
        self._token_api_url = "https://napi.jibit.ir/ppg/v3/purchases"
        self._jwt_token_api_url = "https://napi.jibit.ir/ppg/v3/tokens"
        self._payment_url = "https://napi.jibit.ir/ppg/v3/purchases/{}/payments"
        self._verify_api_url = "https://napi.jibit.ir/ppg/v3/purchases/{}/verify"

    def get_bank_type(self):
        return BankType.JIBIT

    def set_default_settings(self):
        for item in ["API_KEY", "SECRET_KEY"]:
            if item not in self.default_setting_kwargs:
                raise SettingDoesNotExist()
            setattr(self, f"_{item.lower()}", self.default_setting_kwargs[item])

    """
    gateway
    """

    def _get_gateway_payment_url_parameter(self):
        return self._payment_url.format(self.get_reference_number())

    def _get_gateway_payment_parameter(self):
        params = {}
        return params

    def _get_gateway_payment_method_parameter(self):
        return "GET"

    """
    pay
    """

    def get_pay_data(self):
        description = "خرید با شماره پیگیری - {}".format(self.get_tracking_code())
        data = {
            'additionalData': {},
            'amount': self.get_gateway_amount(),
            'callbackUrl': self._get_gateway_callback_url(),
            'checkPayerNationalCode': False,
            'userIdentifier': self.get_mobile_number(),
            'clientReferenceNumber': self.get_tracking_code(),
            'currency': 'IRR',
            'description': description,
            'payerMobileNumber': self.get_mobile_number(),
            'wage': 0,
        }

        return data

    def prepare_pay(self):
        super(Jibit, self).prepare_pay()

    def pay(self):
        super(Jibit, self).pay()
        data = self.get_pay_data()
        response_json = self._send_data(self._token_api_url, data)
        if response_json.get('purchaseId'):
            token = response_json["purchaseId"]
            self._set_reference_number(token)
        else:
            logging.critical("Jibit gateway reject payment")
            raise BankGatewayRejectPayment(self.get_transaction_status_text())

    """
    verify from gateway
    """

    def prepare_verify_from_gateway(self):
        super(Jibit, self).prepare_verify_from_gateway()
        token = self.get_request().POST.get("purchaseId", None)

        self._set_reference_number(token)
        self._set_bank_record()

        extra_information = {
            "payer_ip": self.get_request().POST.get("payerIp", None),
            "psp_reference_number": self.get_request().POST.get("pspReferenceNumber", None),
            "psp_RRN": self.get_request().POST.get("pspRRN", None),
            "payer_masked_card_number": self.get_request().POST.get("payerMaskedCardNumber", None),
            "psp_name": self.get_request().POST.get("pspName", None),
            "psp_hashed_card_number": self.get_request().POST.get("pspHashedCardNumber", None),
            "fail_reason": self.get_request().POST.get("failReason", None),
        }

        self._bank.extra_information = extra_information
        self._bank.save()

    def verify_from_gateway(self, request):
        super(Jibit, self).verify_from_gateway(request)

    """
    verify
    """

    def get_verify_data(self):
        super(Jibit, self).get_verify_data()
        return self.get_reference_number()

    def prepare_verify(self, tracking_code):
        super(Jibit, self).prepare_verify(tracking_code)

    def verify(self, transaction_code):
        super(Jibit, self).verify(transaction_code)
        data = self.get_verify_data()
        response_json = self._send_data(self._verify_api_url.format(data), data)
        if response_json["status"] == "SUCCESSFUL":
            self._set_payment_status(PaymentStatus.COMPLETE)
            self._bank.save()
        else:
            self._set_payment_status(PaymentStatus.CANCEL_BY_USER)
            logging.debug("Jibit gateway unapprove payment")

    def __generate_token(self):
        url = self._jwt_token_api_url

        payload = json.dumps({
            "apiKey": self._api_key,
            "secretKey": self._secret_key
        })
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }
        response = requests.post(url=url, headers=headers, data=payload)
        if response.status_code == 200:
            return response.json()['accessToken']
        else:
            self._set_payment_status(PaymentStatus.ERROR)
            logging.critical("Can not get JWT token from Jibit")
            raise BankGatewayRejectPayment(self.get_transaction_status_text())

    def _send_data(self, api, data):

        access_token = self.__generate_token()
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer {}'.format(access_token)
        }
        try:
            response = requests.post(api, headers=headers, json=data, timeout=5)
        except requests.Timeout:
            logging.exception("Jibit time out gateway {}".format(data))
            raise BankGatewayConnectionError()
        except requests.ConnectionError:
            logging.exception("Jibit time out gateway {}".format(data))
            raise BankGatewayConnectionError()
        print(response.content)
        response_json = get_json(response)

        if response.status_code != 200:
            self._set_transaction_status_text(response_json["errors"][0]['code'])
        return response_json
