from azbankgateways.banks import BaseBank
from azbankgateways.exceptions import SettingDoesNotExist
from azbankgateways.models import CurrencyEnum


class BMI(BaseBank):
    merchant_code = None
    terminal_code = None
    secret_key = None

    def __init__(self, **kwargs):
        super(BMI, self).__init__(**kwargs)
        self.set_currency(CurrencyEnum.IRR)

    def prepare_pay(self):
        super(BMI, self).prepare_pay()

    def pay(self):
        amount = self.prepare_amount()
        # TODO: handle it

    def prepare_verify(self):
        pass

    def verify(self):
        pass

    def set_default_settings(self):
        for item in ['MERCHANT_CODE', 'TERMINAL_CODE', 'SECRET_KEY']:
            if item not in self.default_setting_kwargs:
                raise SettingDoesNotExist()
            setattr(self, item.lower(), self.default_setting_kwargs[item])

