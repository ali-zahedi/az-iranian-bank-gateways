import datetime

from django.db import models
from django.utils.translation import gettext_lazy as _


class BankType(models.TextChoices):
    MELLI = 'melli', _('Melli Bank')
    SAMAN = 'saman', _('Saman Bank')
    TEJARAT = 'tejarat', _('Tejarat Bank')


class PaymentStatus(models.TextChoices):
    REDIRECT_TO_BANK = 'redirect_to_bank', _('Redirect to Bank')
    RETURN_FROM_BANK = 'return_from_bank', _('Return from Bank')
    COMPLETE = 'complete', _('Complete')
    EXPIRE_GATEWAY_TOKEN = 'expire_gateway_token', _('Expire Gateway Token')
    EXPIRE_VERIFY_PAYMENT = 'expire_verify_payment', _('Expire Verify Payment')
    FAILED = 'failed', _('Failed')
    REFUNDED = 'refunded', _('Refunded')


class BankQuerySet(models.QuerySet):
    def active(self):
        return self.exclude(status__in=[
            PaymentStatus.EXPIRE_GATEWAY_TOKEN,
            PaymentStatus.EXPIRE_VERIFY_PAYMENT,
            PaymentStatus.FAILED,
            PaymentStatus.REFUNDED,
        ])

    def completed(self):
        return self.filter(status=PaymentStatus.COMPLETE)

    def refunded(self):
        return self.filter(status=PaymentStatus.REFUNDED)

    def by_bank_type(self, bank_type):
        return self.filter(bank_type=bank_type)

    def by_tracking_code(self, code):
        return self.filter(tracking_code=code)

    def recent(self, minutes=30):
        return self.filter(update_at__gte=datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=minutes))

    def failed(self):
        return self.filter(status=PaymentStatus.FAILED)


class BankManager(models.Manager):
    def get_queryset(self):
        return BankQuerySet(self.model, using=self._db)

    def active(self):
        return self.get_queryset().active()

    def update_expire_records(self):
        expired_time = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=15)

        expired_return = self.active().filter(
            status=PaymentStatus.RETURN_FROM_BANK,
            update_at__lte=expired_time
        ).update(status=PaymentStatus.EXPIRE_VERIFY_PAYMENT)

        expired_redirect = self.active().filter(
            status=PaymentStatus.REDIRECT_TO_BANK,
            update_at__lt=expired_time
        ).update(status=PaymentStatus.EXPIRE_GATEWAY_TOKEN)

        return expired_return + expired_redirect

    def filter_return_from_bank(self):
        return self.active().filter(status=PaymentStatus.RETURN_FROM_BANK)

    def completed_transactions(self):
        return self.get_queryset().completed()

    def refunded_transactions(self):
        return self.get_queryset().refunded()

    def failed_transactions(self):
        return self.get_queryset().failed()

    def transactions_by_bank(self, bank_type):
        return self.get_queryset().by_bank_type(bank_type)

    def find_by_tracking_code(self, code):
        return self.get_queryset().by_tracking_code(code).first()

    def recent_transactions(self, minutes=30):
        return self.get_queryset().recent(minutes=minutes)

    def total_amount_by_status(self, status):
        return self.get_queryset().filter(status=status).aggregate(
            total=models.Sum('amount')
        ).get('total') or 0

    def count_transactions_by_status(self, status):
        return self.get_queryset().filter(status=status).count()


class Bank(models.Model):
    status = models.CharField(
        max_length=50,
        choices=PaymentStatus.choices,
        verbose_name=_("Status"),
    )
    bank_type = models.CharField(
        max_length=50,
        choices=BankType.choices,
        verbose_name=_("Bank"),
    )
    tracking_code = models.CharField(
        max_length=255,
        verbose_name=_("Tracking code"),
    )
    amount = models.CharField(
        max_length=10,
        verbose_name=_("Amount"),
    )
    reference_number = models.CharField(
        unique=True,
        max_length=255,
        verbose_name=_("Reference number"),
    )
    response_result = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Bank result"),
    )
    callback_url = models.TextField(
        verbose_name=_("Callback url"),
    )
    extra_information = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Extra information"),
    )
    bank_choose_identifier = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_("Bank choose identifier"),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        editable=False,
        verbose_name=_("Created at"),
    )
    update_at = models.DateTimeField(
        auto_now=True,
        editable=False,
        verbose_name=_("Updated at"),
    )

    objects = BankManager()

    class Meta:
        verbose_name = _("Bank gateway")
        verbose_name_plural = _("Bank gateways")

    def __str__(self):
        return f"{self.pk}-{self.tracking_code}"

    @property
    def is_success(self):
        return self.status == PaymentStatus.COMPLETE

    def mark_failed(self):
        self.status = PaymentStatus.FAILED
        self.save(update_fields=["status", "update_at"])

    def expire_token(self):
        self.status = PaymentStatus.EXPIRE_GATEWAY_TOKEN
        self.save(update_fields=["status", "update_at"])

    def mark_complete(self):
        self.status = PaymentStatus.COMPLETE
        self.save(update_fields=["status", "update_at"])

    def mark_refunded(self):
        self.status = PaymentStatus.REFUNDED
        self.save(update_fields=["status", "update_at"])

    def is_expired(self):
        return datetime.datetime.now(datetime.timezone.utc) > self.update_at + datetime.timedelta(minutes=15)

    def time_since_update(self):
        return (datetime.datetime.now(datetime.timezone.utc) - self.update_at).total_seconds()

    def short_info(self):
        return f"{self.tracking_code} | {self.amount} | {self.status}"

    def needs_verification(self):
        return self.status == PaymentStatus.RETURN_FROM_BANK
 
