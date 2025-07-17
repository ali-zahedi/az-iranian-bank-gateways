from __future__ import absolute_import, unicode_literals

import importlib
import logging
from enum import Enum


class BankGatewayAutoConnectionFailed(Exception):
    """Raised when all bank gateways fail to connect during auto-creation."""
    pass


class BankType(Enum):
    SADAD = "Sadad"
    SEP = "Sep"


class BaseBank:
    def __init__(self, **kwargs):
        self.identifier = kwargs.get("identifier")
        self.config = kwargs
        self.currency = None
        self.status = "initialized"
        self.transaction_log = []

    def set_currency(self, currency):
        self.currency = currency

    def check_gateway(self, amount):
        logging.debug(f"[Bank: {self.identifier}] Checking gateway with amount: {amount}")

    def connect(self):
        logging.debug(f"[Bank: {self.identifier}] Connecting to gateway.")
        self.status = "connected"

    def disconnect(self):
        logging.debug(f"[Bank: {self.identifier}] Disconnecting from gateway.")
        self.status = "disconnected"

    def is_connected(self):
        return self.status == "connected"

    def get_config(self):
        return self.config

    def get_identifier(self):
        return self.identifier

    def process_transaction(self, amount, transaction_id):
        if not self.is_connected():
            raise RuntimeError(f"Bank '{self.identifier}' is not connected.")

        transaction = {
            "id": transaction_id,
            "amount": amount,
            "currency": self.currency,
            "status": "success"
        }
        self.transaction_log.append(transaction)
        logging.debug(f"[Bank: {self.identifier}] Transaction processed: {transaction}")
        return transaction

    def get_transaction_log(self):
        return self.transaction_log


class DefaultSettings:
    SETTING_VALUE_READER_CLASS = "__main__.DefaultSecretValueReader"


class DefaultSecretValueReader:
    def klass(self, bank_type: BankType, identifier: str):
        if bank_type == BankType.SADAD:
            return "__main__.SadadBank"
        if bank_type == BankType.SEP:
            return "__main__.SepBank"
        raise AttributeError("Unsupported bank type")

    def read(self, bank_type: BankType, identifier: str):
        return {
            "merchant_id": f"merchant-{identifier}",
            "api_key": "secure-key"
        }

    def default(self, identifier: str):
        return BankType.SADAD

    def currency(self, identifier: str):
        return "IRR"

    def get_bank_priorities(self, identifier: str):
        return [BankType.SADAD, BankType.SEP]


class SadadBank(BaseBank):
    pass


class SepBank(BaseBank):
    pass


settings = DefaultSettings()


class BankFactory:
    def __init__(self):
        logging.debug("Initializing BankFactory")
        self._secret_value_reader = self._import(settings.SETTING_VALUE_READER_CLASS)()

    @staticmethod
    def _import(path):
        package, attr = path.rsplit(".", 1)
        return getattr(importlib.import_module(package), attr) if package != "__main__" else globals()[attr]

    def _import_bank(self, bank_type: BankType, identifier: str):
        class_path = self._secret_value_reader.klass(bank_type, identifier)
        bank_class = self._import(class_path)
        logging.debug(f"Imported bank class '{bank_class.__name__}' for type {bank_type.name}")
        bank_settings = self._secret_value_reader.read(bank_type, identifier)
        return bank_class, bank_settings

    def create(self, bank_type: BankType = None, identifier: str = "1") -> BaseBank:
        if not bank_type:
            bank_type = self._secret_value_reader.default(identifier)

        logging.debug(f"Creating bank instance for type: {bank_type.name}")
        bank_class, settings_dict = self._import_bank(bank_type, identifier)
        bank = bank_class(**settings_dict, identifier=identifier)
        bank.set_currency(self._secret_value_reader.currency(identifier))
        bank.connect()
        logging.debug(f"Bank '{bank.get_identifier()}' created and connected.")
        return bank

    def auto_create(self, identifier: str = "1", amount=None) -> BaseBank:
        logging.debug(f"Attempting automatic bank creation for identifier '{identifier}'")
        errors = []

        for bank_type in self._secret_value_reader.get_bank_priorities(identifier):
            try:
                bank = self.create(bank_type, identifier)
                bank.check_gateway(amount)
                return bank
            except Exception as e:
                logging.debug(f"Failed with {bank_type.name}: {e}")
                errors.append(e)

        raise BankGatewayAutoConnectionFailed("\n".join(map(str, errors)))

    def disconnect_bank(self, bank: BaseBank):
        if bank.is_connected():
            bank.disconnect()
            logging.debug(f"Bank '{bank.get_identifier()}' successfully disconnected.")
        else:
            logging.debug(f"Bank '{bank.get_identifier()}' was not connected.")

    def get_bank_config(self, bank: BaseBank):
        config = bank.get_config()
        logging.debug(f"Retrieved config for bank '{bank.get_identifier()}': {config}")
        return config

    def get_bank_status(self, bank: BaseBank):
        status = bank.status
        logging.debug(f"Status for bank '{bank.get_identifier()}': {status}")
        return status

    def execute_transaction(self, bank: BaseBank, amount, transaction_id):
        logging.debug(f"Executing transaction '{transaction_id}' for bank '{bank.get_identifier()}'")
        return bank.process_transaction(amount, transaction_id)

    def retrieve_transaction_log(self, bank: BaseBank):
        log = bank.get_transaction_log()
        logging.debug(f"Transaction log for bank '{bank.get_identifier()}': {log}")
        return log
 
