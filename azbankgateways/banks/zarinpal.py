import logging
import requests

from azbankgateways.banks import BaseBank
from azbankgateways.exceptions import SettingDoesNotExist
from azbankgateways.exceptions.exceptions import (
    BankGatewayConnectionError,
    BankGatewayRejectPayment,
)
from azbankgateways.models import BankType, CurrencyEnum, PaymentStatus
from azbankgateways.utils import get_json


class Zarinpal(BaseBank):
    def __init__(self, **kwargs):
        kwargs.setdefault("SANDBOX", 0)
        super().__init__(**kwargs)
        self._merchant_code = kwargs.get("MERCHANT_CODE")
        self._sandbox = kwargs.get("SANDBOX", 0)
        self.set_gateway_currency(CurrencyEnum.IRT)

        payment_type = "sandbox" if self._sandbox else "payment"
        self._payment_url = f"https://{payment_type}.zarinpal.com/pg/v4/payment/request.json"
        self._startpay_url = f"https://{payment_type}.zarinpal.com/pg/StartPay/"
        self._verify_url = f"https://{payment_type}.zarinpal.com/pg/v4/payment/verify.json"

    def get_bank_type(self):
        return BankType.ZARINPAL

    def set_default_settings(self):
        for key in ["MERCHANT_CODE", "SANDBOX"]:
            if key not in self.default_setting_kwargs:
                raise SettingDoesNotExist(f"{key} does not exist in default_setting_kwargs")
            setattr(self, f"_{key.lower()}", self.default_setting_kwargs[key])

    @classmethod
    def get_minimum_amount(cls):
        return 1000

    def _get_gateway_payment_url_parameter(self):
        return f"{self._startpay_url}{self.get_reference_number()}"

    def _get_gateway_payment_parameter(self):
        return {}

    def _get_gateway_payment_method_parameter(self):
        return "GET"

    def get_pay_data(self):
        description = f"\u062e\u0631\u06cc\u062f \u0628\u0627 \u0634\u0645\u0627\u0631\u0647 \u067e\u06cc\u06af\u06cc\u0631\u06cc - {self.get_tracking_code()}"
        metadata = {"mobile": self.get_mobile_number()} if self.get_mobile_number() else {}

        pay_data = {
            "description": description,
            "merchant_id": self._merchant_code,
            "amount": self.get_gateway_amount(),
            "currency": self._currency,
            "metadata": metadata,
            "callback_url": self._get_gateway_callback_url(),
        }
        pay_data.update(self.get_custom_data())
        return pay_data

    def prepare_pay(self):
        super().prepare_pay()

    def pay(self):
        super().pay()
        data = self.get_pay_data()
        result = self._send_data(self._payment_url, data)
        if result.get("data"):
            self._set_reference_number(result["data"].get("authority"))
        else:
            logging.critical("Zarinpal gateway rejected the payment.")
            raise BankGatewayRejectPayment(self.get_transaction_status_text())

    def prepare_verify_from_gateway(self):
        super().prepare_verify_from_gateway()
        authority = self.get_request().GET.get("Authority")
        self._set_reference_number(authority)
        self._set_bank_record()

    def verify_from_gateway(self, request):
        super().verify_from_gateway(request)

    def get_verify_data(self):
        super().get_verify_data()
        return {
            "merchant_id": self._merchant_code,
            "authority": self.get_reference_number(),
            "amount": self.get_gateway_amount(),
        }

    def prepare_verify(self, tracking_code):
        super().prepare_verify(tracking_code)

    def verify(self, transaction_code):
        super().verify(transaction_code)
        result = self._send_data(self._verify_url, self.get_verify_data())
        data = result.get("data")
        if data and data.get("code") in [100, 101]:
            self._set_payment_status(PaymentStatus.COMPLETE)
        else:
            self._set_payment_status(PaymentStatus.CANCEL_BY_USER)
            logging.debug("Zarinpal gateway did not approve the payment.")

    def _send_data(self, api, data):
        try:
            response = requests.post(api, json=data, timeout=10)
            response.raise_for_status()
        except (requests.RequestException, requests.HTTPError) as error:
            logging.exception(f"ZARINPAL gateway error: {error}, data: {data}")
            raise BankGatewayConnectionError()

        json_data = get_json(response)
        self._set_transaction_status_text(
            json_data.get("data", {}).get("message") or
            json_data.get("errors", {}).get("message", "Unknown error")
        )
        return json_data

    # Utility Methods

    def cancel_payment(self):
        self._set_payment_status(PaymentStatus.CANCEL_BY_USER)
        self._set_transaction_status_text("Payment manually cancelled by user.")
        logging.info(f"Payment manually cancelled: {self.get_reference_number()}")

    def is_payment_successful(self):
        return self.get_payment_status() == PaymentStatus.COMPLETE

    def get_payment_summary(self):
        return {
            "reference_number": self.get_reference_number(),
            "tracking_code": self.get_tracking_code(),
            "status": self.get_payment_status(),
            "amount": self.get_gateway_amount(),
            "currency": self._currency,
            "description": self.get_transaction_status_text(),
        }

    def get_payment_url(self):
        return self._get_gateway_payment_url_parameter()

    def retry_payment(self):
        logging.info(f"Retrying payment: {self.get_reference_number()}")
        return self.pay()

    def has_mobile_number(self):
        return bool(self.get_mobile_number())
 
