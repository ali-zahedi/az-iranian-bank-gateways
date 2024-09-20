import logging
import requests
from azbankgateways.banks import BaseBank
from azbankgateways.exceptions import (
    BankGatewayConnectionError,
    BankGatewayRejectPayment,
    SettingDoesNotExist,
)
from azbankgateways.models import BankType, CurrencyEnum, PaymentStatus
from azbankgateways.utils import get_json


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

    def get_bank_type(self):
        return BankType.ASANPARDAKHT

    def set_default_settings(self):
        required_settings = ["MERCHANT_CONFIGURATION_ID", "USERNAME", "PASSWORD"]
        for item in required_settings:
            if item not in self.default_setting_kwargs:
                raise SettingDoesNotExist(f"{item} is not set in settings.")
            
            setattr(self, f"_{item.lower()}", self.default_setting_kwargs[item])
            print('___________________________________<',self._username)

    def get_pay_data(self):
        data = {
            "serviceTypeId": 1,
            "merchantConfigurationId": self._merchant_configuration_id,
            "localInvoiceId": self.get_tracking_code(),
            "amountInRials": self.get_gateway_amount(),
            "localDate": self._get_local_date(),
            "callbackURL": self._get_gateway_callback_url(),
            "paymentId": self.get_tracking_code(), 
        }
        return data

    def prepare_pay(self):
        super(AsanPardakht, self).prepare_pay()

    def pay(self):
        super(AsanPardakht, self).pay()
        data = self.get_pay_data()
        headers = {

            "usr": self._username,
            "pwd": self._password,
        }
        
        token = self._send_request(self._token_api_url, data, headers, as_json=False)
        print('||||||||||||||||||||||||||||||||||||||||',token)
        if token:
            self._set_reference_number(token)
        else:
            status_text = "Failed to retrieve token from Asan Pardakht"
            self._set_transaction_status_text(status_text)
            logging.critical(status_text)
            raise BankGatewayRejectPayment(self.get_transaction_status_text())

    def _get_status_text(self, status):
        status_codes = {
            "0": "Transaction successful",
            "1": "Issuer declined transaction",
            "2": "Transaction already confirmed",
            "3": "Invalid merchant",
            "4": "Card captured",
            "5": "Transaction not processed",
            "6": "Error occurred",
            "12": "Invalid transaction",
            "13": "Incorrect correction amount",
            "14": "Invalid card number",
            "15": "Invalid issuer",
            "16": "Transaction approved, update track 3",
            "19": "Resend transaction",
            "23": "Invalid commission amount",
            "25": "Original transaction not found",
            "30": "Message format error",
            "31": "Merchant not supported by switch",
            "33": "Card expiration date exceeded",
            "34": "Transaction not successfully completed",
            "36": "Card restricted",
            "38": "Too many incorrect PIN entries",
            "39": "Credit card account not found",
            "40": "Requested operation not supported",
            "41": "Lost card, capture card",
            "43": "Stolen card, capture card",
            "51": "Insufficient funds",
            "54": "Card expiration date exceeded",
            "55": "Invalid card PIN",
            "57": "Transaction not allowed",
            "61": "Transaction amount exceeds limit",
            "63": "Security violation",
            "65": "Too many transaction attempts",
            "75": "Too many incorrect PIN attempts",
            "77": "Invalid transaction date",
            "78": "Card inactive",
            "79": "Invalid linked account",
            "80": "Transaction unsuccessful",
            "84": "Card issuer not responding",
            "86": "Transaction destination in off sign mode",
            "90": "Card issuer performing end-of-day operations",
            "92": "No routing to destination",
            "94": "Duplicate transaction",
            "96": "System error occurred",
            "97": "Issuer or acquirer performing key change"
        }
        return status_codes.get(status, "Unknown error")

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
        ref_id = request.POST.get("RefId") or self.get_tracking_code()  # استفاده از tracking_code در صورت نبودن RefId
        res_code = request.POST.get("ResCode")
        self._set_reference_number(ref_id)
        self._set_bank_record()
        if res_code == "0":
            self._bank.extra_information = f"ResCode={res_code}, RefId={ref_id}"
            self._bank.save()
        else:
            logging.error(f"Payment failed with ResCode: {res_code}")
            self._set_payment_status(PaymentStatus.CANCEL_BY_USER)

    def verify_from_gateway(self, request):
        super(AsanPardakht, self).verify_from_gateway(request)

    def get_verify_data(self):
        data = {
            "merchantConfigurationId": self._merchant_configuration_id,
            "payGateTranId": self.get_reference_number(),
        }
        return data

    def prepare_verify(self, tracking_code):
        super(AsanPardakht, self).prepare_verify(tracking_code)

    def verify(self, transaction_code):
        super(AsanPardakht, self).verify(transaction_code)
        data = self.get_verify_data()
        headers = {

            "usr": self._username,
            "pwd": self._password,
        }
        response_json = self._send_request(self._verify_api_url, data, headers)
        if response_json.get("IsSuccess"):
            self._set_payment_status(PaymentStatus.COMPLETE)
        else:
            self._set_payment_status(PaymentStatus.CANCEL_BY_USER)
            logging.error("Asan Pardakht verification failed.")

    def _send_request(self, api_url, data, headers, as_json=True):
        try:
            response = requests.post(api_url, json=data, headers=headers, timeout=10)
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

        if as_json:
            response_json = get_json(response)
            self._set_transaction_status_text(response_json.get("Message"))
            return response_json
        else:
            return response.text  

    def _get_local_date(self):
        url = 'https://ipgrest.asanpardakht.ir/v1/Time'
        headers = {
            'usr': self._username,  
            'pwd': self._password 
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            server_time = response.text.strip() 
            return server_time
        else:
            raise Exception(f"Failed to retrieve server time: {response.status_code}, {response.text}")

