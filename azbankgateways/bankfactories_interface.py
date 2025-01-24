from django.http import request
from azbankgateways.banks import BaseBank
from azbankgateways.models import BankType
from azbankgateways.bankfactories import BankFactory as BaseBankFactory


class BankFactory(BaseBankFactory):
    def create(
        self,
        request: request,
        amount: int,
        callback_url : str,
        mobile_number: str = None,
        bank_type: BankType = None,
        identifier: str = "1",
    ) -> BaseBank:
        bank = super().create(bank_type, identifier)

        bank = self.set_payment_info(
            bank=bank,
            request=request,
            amount=amount,
            callback_url=callback_url,
            mobile_number=mobile_number,
        )
        return bank
    
    def auto_create(
        self,
        request: request,
        amount: int,
        callback_url : str,
        mobile_number: str = None,
        identifier: str = "1",
    ) -> BaseBank:

        bank = super().auto_create(identifier, amount)

        bank = self.set_payment_info(
            bank=bank,
            request=request,
            amount=amount,
            callback_url=callback_url,
            mobile_number=mobile_number,
        )
        return bank
    
    def set_payment_info(
        self,
        bank: BaseBank,
        request: request,
        amount: int,
        callback_url : str,
        mobile_number: str = None,
    ):
        bank.set_request(request=request)
        bank.set_amount(amount=amount)
        bank.set_client_callback_url(callback_url=callback_url)
        bank.set_mobile_number(mobile_number=mobile_number)
        return bank