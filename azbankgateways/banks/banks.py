import abc
import logging
import uuid
from urllib import parse
import six

from django.db.models import Q
from django.shortcuts import redirect
from django.utils import timezone
from django.urls import reverse

from .. import default_settings as settings
from ..exceptions import CurrencyDoesNotSupport, AmountDoesNotSupport, BankGatewayTokenExpired, BankGatewayStateInvalid
from ..models import Bank, CurrencyEnum, PaymentStatus
from ..utils import append_querystring


# TODO: handle and expire record after 15 minutes
@six.add_metaclass(abc.ABCMeta)
class BaseBank:
    """Base bank for sending to gateway."""
    _gateway_currency: str = CurrencyEnum.IRR
    _currency: str = CurrencyEnum.IRR
    _amount: int = 0
    _gateway_amount: int = 0
    _mobile_number: str = None
    _tracking_code: int = None
    _reference_number: str = ''
    _transaction_status_text: str = ''
    _client_callback_url: str = ''
    _bank: Bank = None
    _request = None

    def __init__(self, identifier: str, **kwargs):
        self.identifier = identifier
        self.default_setting_kwargs = kwargs
        self.set_default_settings()

    @abc.abstractmethod
    def set_default_settings(self):
        """default setting, like fetch merchant code, terminal id and etc"""
        pass

    def prepare_amount(self):
        """prepare amount"""
        if self._currency == self._gateway_currency:
            self._gateway_amount = self._amount
        elif self._currency == CurrencyEnum.IRR and self._gateway_currency == CurrencyEnum.IRT:
            self._gateway_amount = CurrencyEnum.rial_to_toman(self._amount)
        elif self._currency == CurrencyEnum.IRT and self._gateway_currency == CurrencyEnum.IRR:
            self._gateway_amount = CurrencyEnum.toman_to_rial(self._amount)
        else:
            self._gateway_amount = self._amount

        if self.get_gateway_amount() < 1000:
            raise AmountDoesNotSupport()

    @abc.abstractmethod
    def get_bank_type(self):
        pass

    def get_amount(self):
        """get the amount"""
        return self._amount

    def set_amount(self, amount):
        """set amount"""
        if int(amount) <= 0:
            raise AmountDoesNotSupport()
        self._amount = int(amount)

    @abc.abstractmethod
    def prepare_pay(self):
        logging.debug("Prepare pay method")
        self.prepare_amount()
        tracking_code = int(str(uuid.uuid4().int)[-1 * settings.TRACKING_CODE_LENGTH:])
        self._set_tracking_code(tracking_code)

    @abc.abstractmethod
    def get_pay_data(self):
        pass

    @abc.abstractmethod
    def pay(self):
        logging.debug("Pay method")
        self.prepare_pay()

    @abc.abstractmethod
    def get_verify_data(self):
        pass

    @abc.abstractmethod
    def prepare_verify(self, tracking_code):
        logging.debug("Prepare verify method")
        self._set_tracking_code(tracking_code)
        self._set_bank_record()
        self.prepare_amount()

    @abc.abstractmethod
    def verify(self, tracking_code):
        logging.debug("Verify method")
        self.prepare_verify(tracking_code)

    def ready(self) -> Bank:
        self.pay()
        bank = Bank.objects.create(
            bank_choose_identifier=self.identifier,
            bank_type=self.get_bank_type(),
            amount=self.get_amount(),
            reference_number=self.get_reference_number(),
            response_result=self.get_transaction_status_text(),
            tracking_code=self.get_tracking_code(),
        )
        self._bank = bank
        self._set_payment_status(PaymentStatus.WAITING)
        if self._client_callback_url:
            self._bank.callback_url = self._client_callback_url
        return bank

    @abc.abstractmethod
    def prepare_verify_from_gateway(self):
        pass

    def verify_from_gateway(self, request):
        """زمانی که کاربر از گیت وی بانک باز میگردد این متد فراخوانی می شود."""
        self.set_request(request)
        self.prepare_verify_from_gateway()
        self._set_payment_status(PaymentStatus.RETURN_FROM_BANK)
        self.verify(self.get_tracking_code())

    def get_client_callback_url(self):
        """این متد پس از وریفای شدن استفاده خواهد شد. لینک برگشت را بر میگرداند.حال چه وریفای موفقیت آمیز باشد چه با
        لغو کاربر مواجه شده باشد """
        url = append_querystring(self._bank.callback_url,
                                 {settings.TRACKING_CODE_QUERY_PARAM: self.get_tracking_code()})
        return url

    def redirect_client_callback(self):
        """"این متد کاربر را به مسیری که نرم افزار میخواهد هدایت خواهد کرد و پس از وریفای شدن استفاده می شود."""
        logging.debug("Redirect to client")
        return redirect(self.get_client_callback_url())

    def set_mobile_number(self, mobile_number):
        """شماره موبایل کاربر را جهت ارسال به درگاه برای فتچ کردن شماره کارت ها و ... ارسال خواهد کرد."""
        self._mobile_number = mobile_number

    def get_mobile_number(self):
        return self._mobile_number

    def set_client_callback_url(self, callback_url):
        """ذخیره کال بک از طریق نرم افزار برای بازگردانی کاربر پس از بازگشت درگاه بانک به پکیج و سپس از پکیج به نرم
        افزار. """
        if not self._bank:
            self._client_callback_url = callback_url
        else:
            logging.critical(
                "You are change the call back url in invalid situation.",
                extra={
                    'bank_id': self._bank.pk,
                    'status': self._bank.status,
                }
            )
            raise BankGatewayStateInvalid(
                'Bank state not equal to waiting. Probably finish or redirect to bank gateway. status is {}'.format(
                    self._bank.status
                )
            )

    def _set_reference_number(self, reference_number):
        """reference number get from bank """
        self._reference_number = reference_number

    def _set_bank_record(self):
        try:
            self._bank = Bank.objects.get(
                Q(
                    Q(reference_number=self.get_reference_number()) | Q(tracking_code=self.get_tracking_code())
                ),
                Q(bank_type=self.get_bank_type())
            )
            logging.debug("Set reference find bank object.")
        except Bank.DoesNotExist:
            logging.debug("Cant find bank record object.")
            raise BankGatewayStateInvalid(
                "Cant find bank record with reference number reference number is {}".format(
                    self.get_reference_number()
                )
            )
        self._set_tracking_code(self._bank.tracking_code)
        self._set_reference_number(self._bank.reference_number)
        self.set_amount(self._bank.amount)

    def get_reference_number(self):
        return self._reference_number

    """
    ترنزکشن تکست متنی است که از طرف درگاه بانک به عنوان پیام باز میگردد.
    """

    def _set_transaction_status_text(self, txt):
        self._transaction_status_text = txt

    def get_transaction_status_text(self):
        return self._transaction_status_text

    def _set_payment_status(self, payment_status):
        if payment_status == PaymentStatus.RETURN_FROM_BANK and self._bank.status != PaymentStatus.REDIRECT_TO_BANK:
            logging.debug("Payment status is not status suitable.", extra={'status': self._bank.status})
            raise BankGatewayStateInvalid(
                "You change the status bank record before/after this record change status from redirect to bank. "
                "current status is {}".format(
                    self._bank.status
                )
            )
        self._bank.status = payment_status
        self._bank.save()
        logging.debug("Change bank payment status", extra={'status': payment_status})

    def set_gateway_currency(self, currency: CurrencyEnum):
        """واحد پولی درگاه بانک"""
        if currency not in [CurrencyEnum.IRR, CurrencyEnum.IRT]:
            raise CurrencyDoesNotSupport()
        self._gateway_currency = currency

    def get_gateway_currency(self):
        return self._gateway_currency

    def set_currency(self, currency: CurrencyEnum):
        """"واحد پولی نرم افزار"""
        if currency not in [CurrencyEnum.IRR, CurrencyEnum.IRT]:
            raise CurrencyDoesNotSupport()
        self._currency = currency

    def get_currency(self):
        return self._currency

    def get_gateway_amount(self):
        return self._gateway_amount

    """
    ترکینگ کد توسط برنامه تولید شده و برای استفاده های بعدی کاربرد خواهد داشت.
    """

    def _set_tracking_code(self, tracking_code):
        self._tracking_code = tracking_code

    def get_tracking_code(self):
        return self._tracking_code

    """ًRequest"""

    def set_request(self, request):
        self._request = request

    def get_request(self):
        return self._request

    """gateway"""
    def _prepare_check_gateway(self):
        """ست کردن داده های اولیه"""
        self.set_amount(10000)
        self.set_client_callback_url('/')

    def check_gateway(self):
        """با این متد از صحت و سلامت گیت وی برای اتصال اطمینان حاصل می کنیم."""
        self._prepare_check_gateway()
        self.pay()

    @abc.abstractmethod
    def _get_gateway_payment_url_parameter(self):
        """این متد بسته به بانک متفاوت پر می شود."""
        """
        :return
        url: str
        """
        pass

    @abc.abstractmethod
    def _get_gateway_payment_parameter(self):
        """این متد بسته به بانک متفاوت پر می شود."""
        """
        :return
        params: dict
        """
        pass

    @abc.abstractmethod
    def _get_gateway_payment_method_parameter(self):
        """این متد بسته به بانک متفاوت پر می شود."""
        """
        :return
        method: POST, GET
        """
        pass

    def redirect_gateway(self):
        """کاربر را به درگاه بانک هدایت می کند"""
        if (timezone.now() - self._bank.created_at).seconds > 120:
            self._set_payment_status(PaymentStatus.EXPIRE_GATEWAY_TOKEN)
            logging.debug("Redirect to bank expire!")
            raise BankGatewayTokenExpired()
        logging.debug("Redirect to bank")
        self._set_payment_status(PaymentStatus.REDIRECT_TO_BANK)
        return redirect(self.get_gateway_payment_url())

    def get_gateway_payment_url(self):
        redirect_url = reverse(settings.GO_TO_BANK_GATEWAY_NAMESPACE)
        url = self._get_gateway_payment_url_parameter()
        params = self._get_gateway_payment_parameter()
        method = self._get_gateway_payment_method_parameter()
        params.update({
            'url': url,
            'method': method,
        })
        redirect_url = append_querystring(redirect_url, params)
        if self.get_request():
            redirect_url = self.get_request().build_absolute_uri(redirect_url)
        return redirect_url

    def _get_gateway_callback_url(self):
        url = reverse(settings.CALLBACK_NAMESPACE)
        if self.get_request():
            url_parts = list(parse.urlparse(url))
            if not (url_parts[0] and url_parts[1]):
                url = self.get_request().build_absolute_uri(url)
            query = dict(parse.parse_qsl(self.get_request().GET.urlencode()))
            query.update({'bank_type': self.get_bank_type()})
            query.update({'identifier': self.identifier})
            url = append_querystring(url, query)

        return url
