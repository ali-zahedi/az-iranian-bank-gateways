import logging
from json import dumps, loads
from time import gmtime, strftime

from zeep import Client, Transport

from azbankgateways.banks import BaseBank
from azbankgateways.exceptions import SettingDoesNotExist
from azbankgateways.exceptions.exceptions import BankGatewayRejectPayment
from azbankgateways.models import BankType, CurrencyEnum, PaymentStatus


class Mellat(BaseBank):
    _terminal_code = None
    _username = None
    _password = None

    def __init__(self, **kwargs):
        super(Mellat, self).__init__(**kwargs)
        self.set_gateway_currency(CurrencyEnum.IRR)
        self._payment_url = "https://bpm.shaparak.ir/pgwchannel/startpay.mellat"

    def get_bank_type(self):
        return BankType.MELLAT

    def set_default_settings(self):
        for item in ["TERMINAL_CODE", "USERNAME", "PASSWORD"]:
            if item not in self.default_setting_kwargs:
                raise SettingDoesNotExist()
            setattr(self, f"_{item.lower()}", self.default_setting_kwargs[item])

    """
    gateway
    """

    @classmethod
    def get_minimum_amount(cls):
        return 1000

    def _get_gateway_payment_url_parameter(self):
        return self._payment_url

    def _get_gateway_payment_parameter(self):
        params = {
            "RefId": self.get_reference_number(),
            "MobileNo": self.get_mobile_number(),
        }
        return params

    def _get_gateway_payment_method_parameter(self):
        return "GET"

    """
    pay
    """

    def get_pay_data(self):
        description = "خرید با شماره پیگیری - {}".format(self.get_tracking_code())
        data = {
            "terminalId": int(self._terminal_code),
            "userName": self._username,
            "userPassword": self._password,
            "orderId": int(self.get_tracking_code()),
            "amount": int(self.get_gateway_amount()),
            "localDate": self._get_current_date(),
            "localTime": self._get_current_time(),
            "additionalData": description,
            "callBackUrl": self._get_gateway_callback_url(),
            "payerId": 0,
        }
        return data

    def prepare_pay(self):
        super(Mellat, self).prepare_pay()

    def pay(self):
        super(Mellat, self).pay()

        data = self.get_pay_data()
        client = self._get_client()
        response = client.service.bpPayRequest(**data)
        try:
            status, token = response.split(",")
            if status == "0":
                self._set_reference_number(token)
        except ValueError:
            status_text = "Unknown error"
            if response == "11":
                status_text = "Card number is invalid"
            elif response == "12":
                status_text = "Insufficient inventory"
            elif response == "13":
                status_text = "Password is incorrect"
            elif response == "14":
                status_text = "Max try reached"
            elif response == "15":
                status_text = "Card is invalid"
            elif response == "16":
                status_text = "The number of withdrawals is more than allowed"
            elif response == "17":
                status_text = "The user has abandoned the transaction"
            elif response == "18":
                status_text = "The card has expired"
            elif response == "19":
                status_text = "The withdrawal amount is over the limit"
            elif response == "21":
                status_text = "Invalid service"
            elif response == "23":
                status_text = "A security error has occurred"
            elif response == "24":
                status_text = "The recipient's user information is invalid"
            elif response == "25":
                status_text = "The amount is invalid"
            elif response == "31":
                status_text = "The response is invalid"
            elif response == "32":
                status_text = "The format of the entered information is not correct"
            elif response == "33":
                status_text = "The account is invalid"
            elif response == "34":
                status_text = "System error"
            elif response == "35":
                status_text = "Date is invalid"
            elif response == "41":
                status_text = "The request number is duplicate"
            elif response == "42":
                status_text = "Sale transaction not found"
            elif response == "43":
                status_text = "Verify has already been requested"
            elif response == "44":
                status_text = "Verify request not found"
            elif response == "45":
                status_text = "The transaction has been settled"
            elif response == "46":
                status_text = "The transaction has not been settled"
            elif response == "47":
                status_text = "Settle transaction not found"
            elif response == "48":
                status_text = "The transaction has been reversed"
            elif response == "49":
                status_text = "Refund transaction not found"
            elif response == "51":
                status_text = "The transaction is repeated"
            elif response == "54":
                status_text = "The reference transaction does not exist"
            elif response == "55":
                status_text = "The transaction is invalid"
            elif response == "61":
                status_text = "Error in deposit"
            elif response == "111":
                status_text = "Card issuer is invalid"
            elif response == "112":
                status_text = "Card issuing switch error"
            elif response == "113":
                status_text = "No response was received from the card issuer"
            elif response == "114":
                status_text = "The cardholder is not authorized to perform this transaction"
            elif response == "113":
                status_text = "No response was received from the card issuer"
            elif response == "412":
                status_text = "The invoice ID is incorrect"
            elif response == "413":
                status_text = "Payment ID is incorrect"
            elif response == "414":
                status_text = "The organization issuing the bill is invalid"
            elif response == "415":
                status_text = "The working session has ended"
            elif response == "416":
                status_text = "The working session has ended"
            elif response == "417":
                status_text = "Payer ID is invalid"
            elif response == "418":
                status_text = "Problems in defining customer information"
            elif response == "419":
                status_text = "The number of data entries has exceeded the limit"
            elif response == "421":
                status_text = "Invalid IP address"

            self._set_transaction_status_text(status_text)
            logging.critical(status_text)
            raise BankGatewayRejectPayment(self.get_transaction_status_text())

    """
    verify from gateway
    """

    def prepare_verify_from_gateway(self):
        super(Mellat, self).prepare_verify_from_gateway()
        post = self.get_request().POST
        token = post.get("RefId", None)
        if not token:
            return
        self._set_reference_number(token)
        self._set_bank_record()
        self._bank.extra_information = dumps(dict(zip(post.keys(), post.values())))
        self._bank.save()

    def verify_from_gateway(self, request):
        super(Mellat, self).verify_from_gateway(request)

    """
    verify
    """

    def get_verify_data(self):
        super(Mellat, self).get_verify_data()
        data = {
            "terminalId": self._terminal_code,
            "userName": self._username,
            "userPassword": self._password,
            "orderId": self.get_tracking_code(),
            "saleOrderId": self.get_tracking_code(),
            "saleReferenceId": self._get_sale_reference_id(),
        }
        return data

    def prepare_verify(self, tracking_code):
        super(Mellat, self).prepare_verify(tracking_code)

    def verify(self, transaction_code):
        super(Mellat, self).verify(transaction_code)
        data = self.get_verify_data()
        client = self._get_client()

        verify_result = client.service.bpVerifyRequest(**data)
        if verify_result == "0":
            self._settle_transaction()
        else:
            verify_result = client.service.bpInquiryRequest(**data)
            if verify_result == "0":
                self._settle_transaction()
            else:
                logging.debug("Not able to verify the transaction, Making reversal request")
                reversal_result = client.service.bpReversalRequest(**data)

                if reversal_result != "0":
                    logging.debug("Reversal request was not successfull")

                self._set_payment_status(PaymentStatus.CANCEL_BY_USER)
                logging.debug("Mellat gateway unapproved the payment")

    def _settle_transaction(self):
        data = self.get_verify_data()
        client = self._get_client()
        settle_result = client.service.bpSettleRequest(**data)
        if settle_result == "0":
            self._set_payment_status(PaymentStatus.COMPLETE)
        else:
            logging.debug("Mellat gateway did not settle the payment")

    @staticmethod
    def _get_client():
        transport = Transport(timeout=5, operation_timeout=5)
        client = Client("https://bpm.shaparak.ir/pgwchannel/services/pgw?wsdl", transport=transport)
        return client

    @staticmethod
    def _get_current_time():
        return strftime("%H%M%S")

    @staticmethod
    def _get_current_date():
        return strftime("%Y%m%d", gmtime())

    def _get_sale_reference_id(self):
        extra_information = loads(getattr(self._bank, "extra_information", "{}"))
        return extra_information.get("SaleReferenceId", "1")
