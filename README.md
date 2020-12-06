# AZ Iranian Bank Gateway Framework config

 کدهای آزاد و متن باز به زبان پایتون (python) که برای ارتباط درگاه های بانکهای ایرانی توسعه داده شده است.
 پشتیبانی از درگاه بانک ملی و زرین پال.
 
  ورژن جنگو مورد استفاده باید بالاتر از 2.2 باشد.
 
[[_TOC_]]

# Install

``pip install az-iranian-bank-gateways``

## settings
 
### settings.py
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
    'TRANSACTION_QUERY_PARAM': 'tc',
    'TRACKING_CODE_LENGTH': 20,
}
 
```

1. `CHANNELS` : در چنل ها آدرس کلاس اجرا کننده آن بانک قراردارد که می تواند توسط نرم افزار شخصی سازی شود.

1. `DEFAULT`: بانک دیفالت

1. `CURRENCY`: واحد پولی که سیستم از آن استفاده می کند.

1. `TRANSACTION_QUERY_PARAM`: پارامتری که در کوئری استرینگ از آن استفاده خواهد شد.
 
1. `TRACKING_CODE_LENGTH`: طول آی دی طول شده که به منزله شناسه فاکتور در درگاه ها استفاده خواهد شد. اعداد بزرگتر از ۱۶ ممکن است در برخی درگاه ها شما را با مشکل مواجه کند. به عنوان مثال طول آی دی ۲۰ در بانک ملی کار نمی کند.


### urls.py

در فایل `urls.py`

```python
from django.contrib import admin
from django.urls import path

from azbankgateways.urls import az_bank_gateways_urls

admin.autodiscover()

urlpatterns = [
    path('admin/', admin.site.urls),
    path('bankgateways/', az_bank_gateways_urls()),
]
```

با اضافه کردن `path('bankgateways/', az_bank_gateways_urls()),` به لیست یو آر ال ها پرداخت ها پس از درگاه به این مسیر هدایت و اعتبار سنجی پرداخت در این مرحله صورت خواهد پذیرفت.


# Usage

## ارسال به بانک

 برای استفاده و اتصال به درگاه بانک کافی است یک فکتوری ایجاد کنیم و پارامترهای اجباری را تنظیم کنیم. سپس کاربر را می توانیم به درگاه بانک هدایت کنیم.
  
```python
"""
BankFactory()  می توانید به صورت دیفالت نیز استفاده کنید که از بانک پیش فرض استفاده خواهد کرد.
یا اینکه بانک مورد نظر را در هنگام ساخت فکتوری به آن ارسال کنید.
"""
from azbankgateways.bankfactories import BankFactory, BankType

factory = BankFactory() # or BankFactory(BankType.BMI) 

bank = factory.create()
bank.set_request(request)
bank.set_amount(1000)
bank.set_client_callback_url('/gateway/callback') 
bank.set_mobile_number('+989112221234') # Optional

bank_record = bank.ready()

bank.redirect_gateway()

```

`set_mobile_number` پارامتری است که شماره موبایل کاربری که قصد خرید دارد را با آن تنظیم کرده و این شماره موبایل جهت پرداخت و پیگیری آسان تر به درگاه ارسال می شود

## بازگشت از بانک




# TODO

- [ ] Documentation

- [ ] Bank model structure

- [X] BMI gateway support

- [ ] Zarinpal gateway support

- [ ] Saman gateway support

