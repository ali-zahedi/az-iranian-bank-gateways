# AZ Iranian Bank Gateway Framework config

 کدهای آزاد و متن باز به زبان پایتون (python) که برای ارتباط درگاه های بانکهای ایرانی توسعه داده شده است.
 پشتیبانی از درگاه بانک ملی و زرین پال.
 
  ورژن جنگو مورد استفاده باید بالاتر از 2.2 باشد.
 
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

1. `CHANNELS` : در چنل ها آدرس کلاس اجرا کننده آن بانک قراردارد که می تواند توسط نرم افزار شخصی سازی شود.

1. `DEFAULT`: بانک دیفالت

1. `CURRENCY`: واحد پولی که سیستم از آن استفاده می کند.

1. `TRANSACTION_QUERY_PARAM`: پارامتری که در کوئری استرینگ از آن استفاده خواهد شد.
 
# Usage

 برای استفاده و اتصال به درگاه بانک کافی است یک فکتوری ایجاد کنیم و پارامترهای اجباری را تنظیم کنیم. سپس کاربر را می توانیم به درگاه بانک هدایت کنیم.
  
```python
from azbankgateways.bankfactories import BankFactory, BankType
"""
BankFactory()  می توانید به صورت دیفالت نیز استفاده کنید که از بانک پیش فرض استفاده خواهد کرد.
یا اینکه بانک مورد نظر را در هنگام ساخت فکتوری به آن ارسال کنید.
"""

factory = BankFactory() # or BankFactory(BankType.BMI) 

bank = factory.create()
bank.set_amount(100)
bank.set_callback_url('/gateway/callback') 

bank.set_mobile_number('+989112221234') #optional

bank.ready()

order_id = bank.get_order_id()

bank.redirect_gateway()

```

`set_mobile_number` پارامتری است که شماره موبایل کاربری که قصد خرید دارد را با آن تنظیم کرده و این شماره موبایل جهت پرداخت و پیگیری آسان تر به درگاه ارسال می شود

# TODO

- [ ] Documentation

- [ ] Bank model structure

- [ ] BMI gateway support

- [ ] Zarinpal gateway support

- [ ] Saman gateway support

