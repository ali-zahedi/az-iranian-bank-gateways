from django.contrib import admin
from .models import Bank

class BankAdmin(admin.ModelAdmin):
    fields = [
        'status',
        'bank_type',
        'tracking_code',
        'amount',
        'reference_number',
        'response_result',
        'callback_url',
        'extra_information',
        'bank_choose_identifier',
        'created_at',
        'update_at',
    ]
    list_display = [
        'status',
        'bank_type',
        'tracking_code',
        'amount',
        'reference_number',
        'response_result',
        'callback_url',
        'extra_information',
        'bank_choose_identifier',
        'created_at',
        'update_at',
    ]
    list_filter = [
        'status',
        'bank_type',
        'created_at',
        'update_at',
    ]
    search_fields = [
        'status',
        'bank_type',
        'tracking_code',
        'amount',
        'reference_number',
        'response_result',
        'callback_url',
        'extra_information',
        'created_at',
        'update_at',
    ]
    exclude = []
    dynamic_raw_id_fields = []
    readonly_fields = [
        'status',
        'bank_type',
        'tracking_code',
        'amount',
        'reference_number',
        'response_result',
        'callback_url',
        'extra_information',
        'created_at',
        'update_at',
    ]


admin.site.register(Bank, BankAdmin)
