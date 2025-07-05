import base64
import datetime
import logging

import requests
from Crypto.Cipher import DES3

from azbankgateways.banks import BaseBank
from azbankgateways.exceptions import BankGatewayConnectionError, SettingDoesNotExist
from azbankgateways.exceptions.exceptions import (
    BankGatewayRejectPayment,
    BankGatewayStateInvalid,
)
from azbankgateways.models import BankType, CurrencyEnum, PaymentStatus
from azbankgateways.utils import get_json


"""
BMI is a payment gateway integration class for Bank Melli Iran (BMI), 
extending BaseBank to handle payment requests, verifications, and transaction management 
using the Sadad API. It includes support for encryption, card number validation.
"""

class BMI(BaseBank):
    _merchant_code = None
    _terminal_code = None
    _secret_key = None
    _iban_country_code = "IR"
    _card_number = None

    def __init__(self, **kwargs):
        super(BMI, self).__init__(**kwargs)
        if not self._is_strict_origin_policy_enabled():
            raise SettingDoesNotExist(
                "SECURE_REFERRER_POLICY is not set to 'strict-origin-when-cross-origin'"
                " in django setting, it's mandatory for BMI gateway"
            )

        self.set_gateway_currency(CurrencyEnum.IRR)
        self._token_api_url = "https://sadad.shaparak.ir/vpg/api/v0/Request/PaymentRequest"
        self._payment_url = "https://sadad.shaparak.ir/VPG/Purchase"
        self._verify_api_url = "https://sadad.shaparak.ir/vpg/api/v0/Advice/Verify"
        self._transaction_result = None

    def get_bank_type(self):
        return BankType.BMI

    def set_default_settings(self):
        for item in ["MERCHANT_CODE", "TERMINAL_CODE", "SECRET_KEY"]:
            if item not in self.default_setting_kwargs:
                raise SettingDoesNotExist()
            setattr(self, f"_{item.lower()}", self.default_setting_kwargs[item])

    def get_pay_data(self):
        time_now = datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S %p")
        data = {
            "TerminalId": self._terminal_code,
            "MerchantId": self._merchant_code,
            "Amount": self.get_gateway_amount(),
            "SignData": self._encrypt_des3(
                "{};{};{}".format(
                    self._terminal_code,
                    self.get_tracking_code(),
                    self.get_gateway_amount(),
                )
            ),
            "ReturnUrl": self._get_gateway_callback_url(),
            "LocalDateTime": time_now,
            "OrderId": self.get_tracking_code(),
            "AdditionalData": "oi:%s-ou:%s" % (self.get_tracking_code(), self.get_mobile_number()),
        }
        data.update(self.get_custom_data())
        return data

    def prepare_pay(self):
        super(BMI, self).prepare_pay()

    def pay(self):
        super(BMI, self).pay()
        data = self.get_pay_data()
        response_json = self._send_data(self._token_api_url, data)
        if str(response_json["ResCode"]) == "0":
            token = response_json["Token"]
            self._set_reference_number(token)
        else:
            logging.critical("BMI gateway reject payment")
            raise BankGatewayRejectPayment(self.get_transaction_status_text())

    def _get_gateway_payment_method_parameter(self):
        return "GET"

    def _get_gateway_payment_url_parameter(self):
        return self._payment_url

    def _get_gateway_payment_parameter(self):
        params = {"Token": self.get_reference_number()}
        return params

    def get_verify_data(self):
        super(BMI, self).get_verify_data()
        data = {
            "Token": self.get_reference_number(),
            "SignData": self._encrypt_des3(self.get_reference_number()),
        }
        return data

    def prepare_verify(self, tracking_code):
        super(BMI, self).prepare_verify(tracking_code)

    def verify(self, transaction_code):
        super(BMI, self).verify(transaction_code)
        data = self.get_verify_data()
        response_json = self._send_data(self._verify_api_url, data)
        if str(response_json["ResCode"]) == "0":
            self._set_payment_status(PaymentStatus.COMPLETE)
            extra_information = (
                f"RetrivalRefNo={response_json['RetrivalRefNo']}"
                ",SystemTraceNo={response_json['SystemTraceNo']}"
            )
            self._bank.extra_information = extra_information
            self._bank.save()
        else:
            self._set_payment_status(PaymentStatus.CANCEL_BY_USER)
            logging.debug("BMI gateway unapprove payment")

    def prepare_verify_from_gateway(self):
        super(BMI, self).prepare_verify_from_gateway()
        request = self.get_request()
        method_data = getattr(request, "POST", {})
        token = None
        for key, value in method_data.items():
            if key.lower() == "token":
                token = value
                break

        if not token:
            raise BankGatewayStateInvalid
        self._set_reference_number(token)
        self._set_bank_record()

    def verify_from_gateway(self, request):
        super(BMI, self).verify_from_gateway(request)

    def get_transaction_result(self):
        return self._transaction_result

    def is_transaction_successful(self):
        return self._transaction_result == PaymentStatus.COMPLETE

    def cancel_transaction(self):
        self._set_payment_status(PaymentStatus.CANCEL_BY_USER)
        self._bank.save()
        logging.info("Transaction was manually cancelled by user")

    def get_iban_country_code(self):
        return self._iban_country_code

    def get_card_number(self):
        return self._card_number

    def set_card_number(self, card_number):
        self._card_number = card_number

    def validate_card_number(self):
        if not self._card_number or len(self._card_number) != 16 or not self._card_number.isdigit():
            raise ValueError("Invalid card number. Must be 16 digits.")
        return True


    @classmethod
    def _pad(cls, text, pad_size=16):
        text_length = len(text)
        last_block_size = text_length % pad_size
        remaining_space = pad_size - last_block_size
        text = text + (remaining_space * chr(remaining_space))
        return text

    def _encrypt_des3(self, text):
        secret_key_bytes = base64.b64decode(self._secret_key)
        text = self._pad(text, 8)
        cipher = DES3.new(secret_key_bytes, DES3.MODE_ECB)
        cipher_text = cipher.encrypt(str.encode(text))
        return base64.b64encode(cipher_text).decode("utf-8")

    def _send_data(self, api, data):
        try:
            response = requests.post(api, json=data, timeout=5)
        except requests.Timeout:
            logging.exception("BMI time out gateway {}".format(data))
            raise BankGatewayConnectionError()
        except requests.ConnectionError:
            logging.exception("BMI time out gateway {}".format(data))
            raise BankGatewayConnectionError()

        response_json = get_json(response)
        self._set_transaction_status_text(response_json["Description"])
        self._transaction_result = response_json.get("ResCode")
        return response_json
 
