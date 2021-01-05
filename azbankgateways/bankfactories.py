from __future__ import absolute_import, unicode_literals
import importlib

import logging

from .exceptions.exceptions import BankGatewayAutoConnectionFailed
from .models import BankType
from .banks import BaseBank
from . import default_settings as settings


class BankFactory:

    def __init__(self):
        logging.debug('Create bank factory')
        self._secret_value_reader = self._import(settings.SETTING_VALUE_READER_CLASS)()

    @staticmethod
    def _import(path):
        package, attr = path.rsplit('.', 1)
        klass = getattr(importlib.import_module(package), attr)
        return klass

    def _import_bank(self, bank_type: BankType, identifier: str):
        """
        helper to import bank aliases from string paths.

        raises an AttributeError if a bank can't be found by it's alias
        """
        bank_class = self._import(self._secret_value_reader.klass(bank_type=bank_type, identifier=identifier))
        logging.debug('Import bank class')

        return bank_class, self._secret_value_reader.read(bank_type=bank_type, identifier=identifier)

    def create(self, bank_type: BankType = None, identifier: str = '1') -> BaseBank:
        """Build bank class"""
        if not bank_type:
            bank_type = self._secret_value_reader.default(identifier)
        logging.debug('Request create bank', extra={'bank_type': bank_type})

        bank_klass, bank_settings = self._import_bank(bank_type, identifier)
        bank = bank_klass(**bank_settings, identifier=identifier)
        bank.set_currency(self._secret_value_reader.currency(identifier))

        logging.debug('Create bank')
        return bank

    def auto_create(self, identifier: str = '1') -> BaseBank:
        logging.debug('Request create bank automatically')
        bank_list = self._secret_value_reader.get_bank_priorities(identifier)
        for bank_type in bank_list:
            try:
                bank = self.create(bank_type, identifier)
                bank.check_gateway()
                return bank
            except Exception as e:
                logging.debug(str(e))
                logging.debug('Try to connect another bank...')
                continue
        raise BankGatewayAutoConnectionFailed()
