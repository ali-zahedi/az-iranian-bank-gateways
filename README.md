# AZ Iranian Bank Gateway Framework config

[[_TOC_]]

# Install

``pip install az-iranian-bank-gateways``

## settings
 
 در فایل `settings.py` تنظیمات زیر را انجام میدهیم.
 
 ``` python

 AZ_IRANIAN_BANK_GATEWAYS = {
    'CHANNELS': {
        'BMI': {
            'PATH': 'azbankgateways.banks.BMI',
            'MERCHANT_CODE': '<YOUR MERCHANT CODE>',
            'TERMINAL_CODE': '<YOUR TERMINAL CODE>',
            'SECRET_KEY': '<YOUR SECRET KEY>',
        },
    },
    'DEFAULT': 'BMI',
    'CURRENCY': 'IRR',
    'CALLBACK_URL': '/bankgateways/callback',
    'TRANSACTION_QUERY_PARAM': 'tc',
}
 
```
 
# TODO
[] bank model structure
[] bmi gateway support
[] zarinpal gateway support
[] saman gateway support
