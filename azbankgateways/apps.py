# -*- coding: utf-8 -*-
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AZIranianBankGatewaysConfig(AppConfig):
    name = 'azbankgateways'
    verbose_name = _('Iranian bank gateway')
    verbose_name_plural = _('Iranian bank gateways')
