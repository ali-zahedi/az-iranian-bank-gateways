from django.db import models
from django.utils.translation import gettext_lazy as _

from .enum import BankType


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
    bank_type = models.CharField(
        max_length=50,
        choices=BankType.choices,
        verbose_name=_('Bank'),
    )
    response_result = models.TextField(
        null=True,
        blank=True,
        verbose_name=_('Bank result')
    )
    reference_number = models.CharField(
        max_length=255,
        verbose_name=_('Reference number')
    )
    amount = models.CharField(
        max_length=10,
        null=False,
        blank=False,
        verbose_name=_('Amount')
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
