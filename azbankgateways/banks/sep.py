import logging
import requests
from zeep import Client, Transport

from azbankgateways.banks import BaseBank
from azbankgateways.exceptions import BankGatewayConnectionError, SettingDoesNotExist
from azbankgateways.exceptions.exceptions import BankGatewayRejectPayment
from azbankgateways.models import BankType, CurrencyEnum, PaymentStatus
from azbankgateways.utils import get_json

# IBAN = IR (Iran)

class SEP(BaseBank):
    _merchant_code = None
    _terminal_code = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self._is_strict_origin_policy_enabled():
            raise SettingDoesNotExist(
                "SECURE_REFERRER_POLICY must be 'strict-origin-when-cross-origin' for SEP gateway."
            )

        self.set_gateway_currency(CurrencyEnum.IRR)
        self._token_api_url = "https://sep.shaparak.ir/MobilePG/MobilePayment"
        self._payment_url = "https://sep.shaparak.ir/OnlinePG/OnlinePG"
        self._verify_api_url = "https://verify.sep.ir/Payments/ReferencePayment.asmx?WSDL"

    def get_bank_type(self):
        return BankType.SEP

    def set_default_settings(self):
        for key in ["MERCHANT_CODE", "TERMINAL_CODE"]:
            if key not in self.default_setting_kwargs:
                raise SettingDoesNotExist(f"Missing setting: {key}")
            setattr(self, f"_{key.lower()}", self.default_setting_kwargs[key])

    def get_pay_data(self):
        data = {
            "Action": "Token",
            "Amount": self.get_gateway_amount(),
            "Wage": 0,
            "TerminalId": self._merchant_code,
            "ResNum": self.get_tracking_code(),
            "RedirectURL": self._get_gateway_callback_url(),
            "CellNumber": self.get_mobile_number(),
        }
        data.update(self.get_custom_data())
        return data

    def prepare_pay(self):
        super().prepare_pay()

    def pay(self):
        super().pay()
        response = self._send_data(self._token_api_url, self.get_pay_data())
        if str(response.get("status")) == "1":
            self._set_reference_number(response["token"])
        else:
            logging.critical("SEP gateway rejected payment: %s", response)
            raise BankGatewayRejectPayment(self.get_transaction_status_text())

    def _get_gateway_payment_url_parameter(self):
        return self._payment_url

    def _get_gateway_payment_method_parameter(self):
        return "POST"

    def _get_gateway_payment_parameter(self):
        return {
            "Token": self.get_reference_number(),
            "GetMethod": "true",
        }

    def prepare_verify_from_gateway(self):
        super().prepare_verify_from_gateway()
        request = self.get_request()
        if not self.validate_callback_data():
            raise BankGatewayRejectPayment("Invalid callback data")

        self._set_tracking_code(request.GET.get("ResNum"))
        self._set_bank_record()
        ref_num = request.GET.get("RefNum")
        token = request.GET.get("Token")
        traceno = request.GET.get("TRACENO")

        self._set_reference_number(ref_num)
        self._bank.reference_number = ref_num
        self._bank.extra_information = f"TRACENO={traceno}, RefNum={ref_num}, Token={token}"
        self._bank.save()

    def verify_from_gateway(self, request):
        super().verify_from_gateway(request)

    def get_verify_data(self):
        super().get_verify_data()
        return self.get_reference_number(), self._merchant_code

    def prepare_verify(self, tracking_code):
        super().prepare_verify(tracking_code)

    def verify(self, transaction_code):
        super().verify(transaction_code)
        client = self._get_client(self._verify_api_url)
        result = client.service.verifyTransaction(*self.get_verify_data())
        if result == self.get_gateway_amount():
            self._set_payment_status(PaymentStatus.COMPLETE)
        else:
            self._set_payment_status(PaymentStatus.CANCEL_BY_USER)
            logging.debug("SEP gateway did not approve payment")

    def _send_data(self, url, data):
        try:
            response = requests.post(url, json=data, timeout=5)
            response.raise_for_status()
        except (requests.Timeout, requests.ConnectionError) as e:
            logging.exception("SEP request error: %s", e)
            raise BankGatewayConnectionError()

        json_response = get_json(response)
        self._set_transaction_status_text(json_response.get("errorDesc"))
        return json_response

    @staticmethod
    def _get_client(wsdl_url):
        transport = Transport(timeout=5, operation_timeout=5)
        transport.session.headers.update({
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "User-Agent": "PythonClient/SEP",
        })
        return Client(wsdl_url, transport=transport)

    def is_transaction_successful(self):
        return self._bank and self._bank.payment_status == PaymentStatus.COMPLETE

    def get_transaction_info(self):
        return {
            "tracking_code": self.get_tracking_code(),
            "reference_number": self.get_reference_number(),
            "amount": self.get_gateway_amount(),
            "status": self._bank.payment_status.name if self._bank else "UNKNOWN",
            "extra_information": getattr(self._bank, 'extra_information', None),
        }

    def cancel_transaction(self, reason="User cancelled the payment"):
        self._set_payment_status(PaymentStatus.CANCEL_BY_USER)
        if self._bank:
            self._bank.extra_information = f"Cancelled: {reason}"
            self._bank.save()
        logging.info("Transaction cancelled: %s", reason)

    def log_transaction_summary(self):
        logging.info("SEP Transaction | Amount: %s | Ref#: %s | Status: %s",
                     self.get_gateway_amount(),
                     self.get_reference_number(),
                     self._bank.payment_status.name if self._bank else "UNKNOWN")

    def resend_token_request(self):
        logging.info("Resending token request to SEP")
        return self._send_data(self._token_api_url, self.get_pay_data())

    def validate_callback_data(self):
        request = self.get_request()
        required = ["ResNum", "RefNum", "State", "Token"]
        missing = [p for p in required if not request.GET.get(p)]
        if missing:
            logging.warning("Missing callback data: %s", missing)
            return False
        return True
 
