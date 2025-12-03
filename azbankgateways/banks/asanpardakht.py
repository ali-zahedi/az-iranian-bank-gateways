import json
import logging

import requests

from azbankgateways.banks import BaseBank
from azbankgateways.exceptions import (
    AZBankGatewaysException,
    BankGatewayConnectionError,
    BankGatewayRejectPayment,
    SettingDoesNotExist,
)
from azbankgateways.models import BankType, CurrencyEnum, PaymentStatus


class AsanPardakht(BaseBank):
    _merchant_configuration_id = None
    _username = None
    _password = None

    def __init__(self, **kwargs):
        super(AsanPardakht, self).__init__(**kwargs)

        self.set_gateway_currency(CurrencyEnum.IRR)
        self._token_api_url = "https://ipgrest.asanpardakht.ir/v1/Token"
        self._payment_url = "https://asan.shaparak.ir"
        self._verify_api_url = "https://ipgrest.asanpardakht.ir/v1/Verify"
        self._local_date_api_url = "https://ipgrest.asanpardakht.ir/v1/Time"
        self._transaction_result_api_url = "https://ipgrest.asanpardakht.ir/v1/TranResult"
        self._settlement_api_url = "https://ipgrest.asanpardakht.ir/v1/Settlement"

    def get_bank_type(self):
        return BankType.ASANPARDAKHT

    def set_default_settings(self):
        required_settings = ["MERCHANT_CONFIGURATION_ID", "USERNAME", "PASSWORD"]
        for item in required_settings:
            if item not in self.default_setting_kwargs:
                raise SettingDoesNotExist(f"{item} is not set in settings.")

            setattr(self, f"_{item.lower()}", self.default_setting_kwargs[item])

    def get_pay_data(self):
        data = {
            "serviceTypeId": 1,  # Service type code. For making a purchase, send code 1.
            "merchantConfigurationId": self._merchant_configuration_id,
            "localInvoiceId": self.get_tracking_code(),
            "amountInRials": self.get_gateway_amount(),
            "localDate": self._get_local_date(),
            "callbackURL": self._get_gateway_callback_url() + f'&localInvoiceId={self.get_tracking_code()}',
            "paymentId": self.get_tracking_code(),
            **self.get_custom_data(),
        }
        return data

    def prepare_pay(self):
        super(AsanPardakht, self).prepare_pay()

    def pay(self):
        super(AsanPardakht, self).pay()
        data = self.get_pay_data()
        token = self._send_request(self._token_api_url, data)
        if token:
            self._set_reference_number(token)
        else:
            status_text = "Failed to retrieve token from Asan Pardakht"
            self._set_transaction_status_text(status_text)
            logging.critical(status_text)
            raise BankGatewayRejectPayment(self.get_transaction_status_text())

    def _get_gateway_payment_url_parameter(self):
        return self._payment_url

    def _get_gateway_payment_method_parameter(self):
        return "POST"

    def _get_gateway_payment_parameter(self):
        params = {
            "RefId": self.get_reference_number(),
        }
        return params

    def prepare_verify_from_gateway(self):
        super(AsanPardakht, self).prepare_verify_from_gateway()
        request = self.get_request()
        tracking_code = request.GET.get("localInvoiceId")
        self._set_tracking_code(tracking_code)
        self._set_bank_record()
        self._check_transaction_data()

    def verify_from_gateway(self, request):
        super(AsanPardakht, self).verify_from_gateway(request)

    def get_verify_data(self):
        data = {
            "merchantConfigurationId": self._merchant_configuration_id,
            "payGateTranId": self._get_pay_gate_tran_id(),
        }
        return data

    def prepare_verify(self, tracking_code):
        super(AsanPardakht, self).prepare_verify(tracking_code)

    def verify(self, transaction_code):
        super(AsanPardakht, self).verify(transaction_code)
        data = self.get_verify_data()
        self._send_request(self._verify_api_url, data, is_json=False)
        self._set_payment_status(PaymentStatus.COMPLETE)
        self._settle_transaction()

    def _send_request(self, api_url, data, method='POST', is_json=True):
        headers = {
            "usr": self._username,
            "pwd": self._password,
        }
        try:
            response = requests.request(
                method, api_url, json=data, headers=headers, timeout=self.get_timeout()
            )
            response.raise_for_status()
        except requests.Timeout:
            logging.exception(f"Asan Pardakht gateway timeout: {data}")
            raise BankGatewayConnectionError()
        except requests.ConnectionError:
            logging.exception(f"Asan Pardakht gateway connection error: {data}")
            raise BankGatewayConnectionError()
        except requests.HTTPError as e:
            logging.exception(f"HTTP error occurred: {e}")
            raise BankGatewayConnectionError()
        if is_json:
            return response.json()
        return response.text

    def _get_local_date(self):
        return self._send_request(self._local_date_api_url, {}, method='GET')

    def _get_transaction_data(self):
        data = {
            'merchantConfigurationId': self._merchant_configuration_id,
            'localInvoiceId': self.get_tracking_code(),
        }
        return self._send_request(self._transaction_result_api_url, data, method='GET')

    def _check_transaction_data(self):
        transaction_data = self._get_transaction_data()
        is_valid = (
            transaction_data
            and self._bank.reference_number == transaction_data.get('refID')
            and transaction_data.get('amount') is not None
            and int(self._bank.amount) == transaction_data.get('amount')
        )
        if not is_valid:
            error_message = (
                "Transaction data validation failed. The reference number or the amount "
                "received from the gateway does not match the internal bank record."
            )
            raise AZBankGatewaysException(error_message)
        self._set_pay_gate_tran_id(transaction_data)

    def _settle_transaction(self):
        try:
            data = {
                "merchantConfigurationId": self._merchant_configuration_id,
                "payGateTranId": self._get_pay_gate_tran_id(),
            }
            self._send_request(self._settlement_api_url, data=data, is_json=False)
        except Exception:
            logging.debug("AsanPardakht gateway did not settle the payment")

    def _set_pay_gate_tran_id(self, transaction_data):
        self._bank.extra_information = json.dumps({'payGateTranID': transaction_data.get('payGateTranID')})
        self._bank.save(update_fields={'extra_information'})

    def _get_pay_gate_tran_id(self):
        return json.loads(self._bank.extra_information)['payGateTranID']
