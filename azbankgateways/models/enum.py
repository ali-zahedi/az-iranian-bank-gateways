from django.db import models
from django.utils.translation import gettext_lazy as _


class BankType(models.TextChoices):
    BMI = "BMI", _("BMI")
    SEP = "SEP", _("SEP")
    ZARINPAL = "ZARINPAL", _("Zarinpal")
    IDPAY = "IDPAY", _("IDPay")
    ZIBAL = "ZIBAL", _("Zibal")
    BAHAMTA = "BAHAMTA", _("Bahamta")
    MELLAT = "MELLAT", _("Mellat")
    PAYV1 = "PAYV1", _("PayV1")

    @classmethod
    def values_list(cls):
        """Return all enum values as a list."""
        return [choice.value for choice in cls]

    @classmethod
    def is_valid(cls, value):
        """Check if a given value is a valid enum option."""
        return value in cls.values_list()

    @classmethod
    def get_label(cls, value):
        """Get the display label for a given enum value."""
        try:
            return cls(value).label
        except ValueError:
            return None


class CurrencyEnum(models.TextChoices):
    IRR = "IRR", _("Rial")
    IRT = "IRT", _("Toman")

    @classmethod
    def rial_to_toman(cls, amount):
        """Convert Rial to Toman."""
        return amount / 10 if isinstance(amount, (int, float)) else None

    @classmethod
    def toman_to_rial(cls, amount):
        """Convert Toman to Rial."""
        return amount * 10 if isinstance(amount, (int, float)) else None

    @classmethod
    def is_valid(cls, value):
        """Validate a given currency code."""
        return value in cls.values_list()

    @classmethod
    def values_list(cls):
        """Return all currency values as a list."""
        return [choice.value for choice in cls]

    @classmethod
    def choices_dict(cls):
        """Return a dictionary of enum names and their labels."""
        return {choice.name: choice.label for choice in cls}

    @classmethod
    def get_label(cls, value):
        """Get the display label for a given currency value."""
        try:
            return cls(value).label
        except ValueError:
            return None


class PaymentStatus(models.TextChoices):
    WAITING = "WAITING", _("Waiting")
    REDIRECT_TO_BANK = "REDIRECT_TO_BANK", _("Redirect to bank")
    RETURN_FROM_BANK = "RETURN_FROM_BANK", _("Return from bank")
    CANCEL_BY_USER = "CANCEL_BY_USER", _("Cancel by user")
    EXPIRE_GATEWAY_TOKEN = "EXPIRE_GATEWAY_TOKEN", _("Expire gateway token")
    EXPIRE_VERIFY_PAYMENT = "EXPIRE_VERIFY_PAYMENT", _("Expire verify payment")
    COMPLETE = "COMPLETE", _("Complete")
    ERROR = "ERROR", _("Unknown error acquired")

    @classmethod
    def values_list(cls):
        """Return all status values as a list."""
        return [choice.value for choice in cls]

    @classmethod
    def is_valid(cls, value):
        """Check if the value is a valid payment status."""
        return value in cls.values_list()

    @classmethod
    def get_label(cls, value):
        """Return the human-readable label for a payment status."""
        try:
            return cls(value).label
        except ValueError:
            return None

    @classmethod
    def final_statuses(cls):
        """Statuses indicating a completed or failed payment process."""
        return [cls.COMPLETE, cls.ERROR, cls.CANCEL_BY_USER]

    @classmethod
    def in_progress_statuses(cls):
        """Statuses indicating an ongoing payment process."""
        return [cls.WAITING, cls.REDIRECT_TO_BANK, cls.RETURN_FROM_BANK]

    @classmethod
    def is_terminal(cls, status):
        """Check if a status is terminal (final and not changing)."""
        return status in cls.final_statuses()

    @classmethod
    def has_failed(cls, status):
        """Determine if the given status indicates a failure."""
        return status in [cls.ERROR, cls.EXPIRE_GATEWAY_TOKEN, cls.EXPIRE_VERIFY_PAYMENT]
 
