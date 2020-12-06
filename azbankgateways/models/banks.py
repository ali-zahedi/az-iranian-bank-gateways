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
    # reference number return from bank
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
