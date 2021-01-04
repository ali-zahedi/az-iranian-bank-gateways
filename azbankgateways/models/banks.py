import datetime

from django.db import models
from django.utils.translation import gettext_lazy as _

from .enum import BankType, PaymentStatus


class BankQuerySet(models.QuerySet):
    def __init__(self, *args, **kwargs):
        super(BankQuerySet, self).__init__(*args, **kwargs)

    def active(self):
        return self.filter()


class BankManager(models.Manager):
    def get_queryset(self):
        return BankQuerySet(self.model, using=self._db)

    def active(self):
        return self.get_queryset().active()

    def update_expire_records(self):
        count = self.active().filter(
            status=PaymentStatus.RETURN_FROM_BANK,
            update_at__lte=datetime.datetime.now() - datetime.timedelta(minutes=15)
        ).update(
            status=PaymentStatus.EXPIRE_VERIFY_PAYMENT
        )

        count = count + self.active().filter(
            status=PaymentStatus.REDIRECT_TO_BANK,
            update_at__lt=datetime.datetime.now() - datetime.timedelta(minutes=15)
        ).update(
            status=PaymentStatus.EXPIRE_GATEWAY_TOKEN
        )
        return count

    def filter_return_from_bank(self):
        return self.active().filter(status=PaymentStatus.RETURN_FROM_BANK)


class Bank(models.Model):
    status = models.CharField(
        max_length=50,
        null=False,
        blank=False,
        choices=PaymentStatus.choices,
        verbose_name=_('Status'),
    )
    bank_type = models.CharField(
        max_length=50,
        choices=BankType.choices,
        verbose_name=_('Bank'),
    )
    # It's local and generate locally
    tracking_code = models.CharField(
        max_length=255,
        null=False,
        blank=False,
        verbose_name=_('Tracking code')
    )
    amount = models.CharField(
        max_length=10,
        null=False,
        blank=False,
        verbose_name=_('Amount')
    )
    # Reference number return from bank
    reference_number = models.CharField(
        unique=True,
        max_length=255,
        null=False,
        blank=False,
        verbose_name=_('Reference number')
    )
    response_result = models.TextField(
        null=True,
        blank=True,
        verbose_name=_('Bank result')
    )
    callback_url = models.TextField(
        null=False,
        blank=False,
        verbose_name=_('Callback url')
    )
    extra_information = models.TextField(
        null=True,
        blank=True,
        verbose_name=_('Extra information')
    )
    bank_choose_identifier = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_('Bank choose identifier')
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        editable=False,
    )
    update_at = models.DateTimeField(
        auto_now=True,
        editable=False,
    )

    objects = BankManager()

    class Meta:
        verbose_name = _('Bank gateway')
        verbose_name_plural = _('Bank gateways')

    @property
    def is_success(self):
        return self.status == PaymentStatus.COMPLETE
