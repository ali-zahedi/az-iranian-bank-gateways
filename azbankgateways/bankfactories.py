from __future__ import absolute_import, unicode_literals
import importlib

import logging
from .models import BankType
from .banks import BaseBank
from . import default_settings as settings


class BankFactory:

    def __init__(self, bank_type: BankType = None):
        if not bank_type:
            bank_type = settings.BANK_DEFAULT
        logging.debug('Create bank factory', extra={'bank_type': bank_type})
        self.bank_type = bank_type

    def _import_bank(self):
        """
        helper to import bank aliases from string paths.

        raises an AttributeError if a bank can't be found by it's alias
        """
        try:
            bank_settings = settings.BANK_GATEWAYS[self.bank_type]
        except KeyError:
            raise AttributeError(
                '"%s" is not a valid delivery bank alias. '
                'Check your applications settings for AZ_IRANIAN_BANK_GATEWAYS'
                % self.bank_type
            )
        package, attr = bank_settings['PATH'].rsplit('.', 1)

        bank_class = getattr(importlib.import_module(package), attr)
        logging.debug('Import bank class')

        return bank_class, bank_settings

    def create(self) -> BaseBank:
        """Build bank class"""
        logging.debug('Request create bank')

        bank_klass, bank_settings = self._import_bank()
        bank = bank_klass(**bank_settings)
        bank.set_currency(settings.CURRENCY)

        logging.debug('Create bank')
        return bank
