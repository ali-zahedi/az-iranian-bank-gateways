<!--![GitHub All Releases](https://img.shields.io/github/downloads/ali-zahedi/az-iranian-bank-gateways/total)-->
<!--![GitHub issues](https://img.shields.io/github/issues/ali-zahedi/az-iranian-bank-gateways)-->
![GitHub](https://img.shields.io/github/license/ali-zahedi/az-iranian-bank-gateways)
![GitHub](https://img.shields.io/pypi/pyversions/az-iranian-bank-gateways.svg?maxAge=2592000)
![GitHub](https://img.shields.io/pypi/v/az-iranian-bank-gateways.svg?maxAge=2592000)
# AZ Iranian Bank Gateway Framework config

<p dir="rtl">
 کدهای آزاد و متن باز به زبان پایتون (python) که برای ارتباط با درگاه های بانکهای ایرانی در جنگو (Django) توسعه داده شده است.
 
 <p dir="rtl">
 در حال حاضر درگاه های با درگاه های زیر می توانید پرداخت کنید.
 </p>
 
 1. [درگاه پرداخت بانک ملی ایران (BMI)](https://mmp.sadadpsp.ir/Browse/MerchantRequestForm?@TermType_Shaparakabbr=INT)
 
 1. [درگاه پرداخت بانک سامان (SEP)](https://www.sep.ir/iemerchantregister)
 
 1. [درگاه پرداخت زرین پال](https://next.zarinpal.com/auth/register)
 
 1. [درگاه پرداخت آی دی پی (IDPay)](https://idpay.ir/s/664153)
 
 1. [درگاه پرداخت زیبال](https://zibal.ir)
 
 1. [درگاه پرداخت باهمتا](https://webpay.bahamta.com?rc=Sv7oH)
 
 
[[_TOC_]]

<h1 dir="rtl">نصب</h1>

<p dir="rtl"> نصب از طریق پکیج منیجر </p>

``pip install az-iranian-bank-gateways``


<h1 dir="rtl">تنظیمات</h1>
 
### settings.py

<p dir="rtl"> در فایل `settings.py` تنظیمات زیر را انجام میدهیم. </p>

 
 ``` python
INSTALLED_APPS = [
    # ....
    'azbankgateways',
    # ...
]
AZ_IRANIAN_BANK_GATEWAYS = {
    'GATEWAYS': {
        'BMI': {
            'MERCHANT_CODE': '<YOUR MERCHANT CODE>',
            'TERMINAL_CODE': '<YOUR TERMINAL CODE>',
            'SECRET_KEY': '<YOUR SECRET CODE>',
        },
        'SEP': {
            'MERCHANT_CODE': '<YOUR MERCHANT CODE>',
            'TERMINAL_CODE': '<YOUR TERMINAL CODE>',
        },
        'ZARINPAL': {
            'MERCHANT_CODE': '<YOUR MERCHANT CODE>',
        },
        'IDPAY': {
            'MERCHANT_CODE': '<YOUR MERCHANT CODE>',
            'METHOD': 'POST',  # GET or POST
            'X_SANDBOX': 0,  # 0 disable, 1 active
        },
        'ZIBAL': {
            'MERCHANT_CODE': '<YOUR MERCHANT CODE>',
        },
        'BAHAMTA': {
            'MERCHANT_CODE': '<YOUR MERCHANT CODE>',
        },
    },
    'DEFAULT': 'BMI',
    'CURRENCY': 'IRR', # اختیاری
    'TRACKING_CODE_QUERY_PARAM': 'tc', # اختیاری
    'TRACKING_CODE_LENGTH': 16, # اختیاری
    'SETTING_VALUE_READER_CLASS': 'azbankgateways.readers.DefaultReader', # اختیاری
    'BANK_PRIORITIES': [
        'BMI',
        'SEP',
        # and so on ...
    ], # اختیاری
}
 ```

1. `GATEWAYS` :  تنظیمات مربوط به هر بانک به صورت دیکشنری های جدا در این قسمت وجود دارد. تنظیماتی مانند کلاس اجرا کننده، کلیدهای امنیتی که توسط بانک در اختیار شما قرار می گیرد.

1. `DEFAULT`: در زمانی که به سازنده فکتوری پارامتری ارسال نشود از این تنظیم به عنوان بانک پیش فرض استفاده خواهد شد و ارتباطات با این بانک برقرار می شود. 

1. `CURRENCY - (IRR, IRT)`: واحد پولی که نرم افزار با آن کار می کند. این واحد پولی فارغ از واحد پولی درگاه خواهد بود.  در صورتی که واحد پولی نرم افزار با واحد پولی درگاه بانک متفاوت باشد تبدیل ریال به تومان یا بالعکس انجام خواهد شد.  

1. `TRACKING_CODE_QUERY_PARAM `: پارامتری که در هنگام بازگشت از درگاه به کال بک یو آر ال تعیین شده تنظیم و ارسال می گردد. به عنوان مثال زمانی که از کاربر از درگاه بانک باز می گردد چه پرداخت موفق داشته باشد و چه نا موفق کاربر به لینکی که در هنگام استفاده از درگاه تنظیم شده است٬ ارجاع داده می شود و در انتهای آن این رشته + کد پیگیری بازگردانده می شود تا بتوان داده ها را از این طریق بازیابی کرد.  
 
1. `TRACKING_CODE_LENGTH`: طول کد پیگیری تولید شده توسط سیستم است. دقت شود که در برخی درگاه ها مانند درگاه بانک ملی ایران، طول ۲۰ کاراکتر خطای `شماره سفارش ارسال نشده است` را می دهد. 

1. `SETTING_VALUE_READER_CLASS`: با مقدار دهی به این تنظیم شما می توانید حالت یک متغیر خوان اضافه کنید که قابلیت های دیگری مثل پروایدر و پشتیبانی از یک بانک با چند اکانت و ... را به آن اضافه کنید.
 
1. `BANK_PRIORITIES`: این آرایه اختیاری است. زمانی که وضعیت اتصال به درگاه به صورت خودکار تعیین شده باشد، ابتدا به بانک پیش فرض متصل می شود و سپس بر این اساس شروع به اتصال خواهد کرد، تا به اولین درگاه فعال برسد. در حالت پیش فرض این آرایه خالی است که بعد از اتصال به درگاه مورد نظر در صورت خطا بقیه درگاه ها امتحان نخواهند شد.

### urls.py

<p dir="rtl">
 در فایل `urls.py`
</p>

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
<p dir="rtl">
با اضافه کردن آدرس بالا به لیست یو آر ال ها، پرداخت ها پس از درگاه به این مسیر هدایت و اعتبار سنجی می شوند و سپس مجدد به سمت کال بکی که به ازای هر درخواست تنظیم می شود، مسیر یابی خواهد شد.
</p>

### Migrate
<p dir="rtl">
بعد از انجام تنظیمات دستور زیر را اجرا می کنیم.
</p>

```
python manage.py migrate
```


<h1 dir="rtl">نحوه استفاده</h1>
<h2 dir="rtl">ارسال به بانک</h2>


<p dir="rtl">
 برای استفاده و اتصال به درگاه بانک کافی است یک `BankFactory` ایجاد کنیم و پارامترهای اجباری را تنظیم کنیم. سپس کاربر را می توانیم به درگاه بانک هدایت  کنیم.
</p>

  
```python
from django.urls import reverse
from azbankgateways import bankfactories, models as bank_models, default_settings as settings



def go_to_gateway_view(request):
    # خواندن مبلغ از هر جایی که مد نظر است
    amount = 1000
    # تنظیم شماره موبایل کاربر از هر جایی که مد نظر است
    user_mobile_number = '+989112221234'  # اختیاری

    factory = bankfactories.BankFactory()
    bank = factory.create() # or factory.create(bank_models.BankType.BMI) or set identifier
    bank.set_request(request)
    bank.set_amount(amount)
    # یو آر ال بازگشت به نرم افزار برای ادامه فرآیند
    bank.set_client_callback_url(reverse('callback-gateway'))
    bank.set_mobile_number(user_mobile_number)  # اختیاری

    # در صورت تمایل اتصال این رکورد به رکورد فاکتور یا هر چیزی که بعدا بتوانید ارتباط بین محصول یا خدمات را با این
    # پرداخت برقرار کنید. 
    bank_record = bank.ready()
    
    # هدایت کاربر به درگاه بانک
    return bank.redirect_gateway()

```

<p dir="rtl"> 
در صورتیکه تمایل دارید به صورت خودکار به اولین درگاه در دسترس متصل شوید. ابتدا از قسمت تنظیمات در بخش `BANK_PRIORITIES
` اولویت های بانک های مد نظر را وارید کنید. سپس به جای استفاده از متد `factory.create` از متد ‍`factory.auto_create` در این بخش استفاده کنید.
 </p>

`set_mobile_number` متدی است که پارامتر شماره موبایل کاربری که قصد خرید دارد را به آن پاس میدهیم. این شماره موبایل جهت پرداخت و پیگیری آسان تر به درگاه ارسال می شود

<h2 dir="rtl">بازگشت از بانک</h2>

<p dir="rtl"> 
وضعیت رکورد بانک به شرح ذیل می باشد.
 </p>

1. `WAITING`: در انتظار برای انتقال کاربر به درگاه بانک

1. `REDIRECT_TO_BANK`: کاربر به درگاه بانک منتقل شده است ولی هنوز از درگاه باز نگشته است.
 
1. `RETURN_FROM_BANK`: کاربر از درگاه برگشته ولی عملیات صحت سنجی٬ یا تکمیل نشده است یا با خطا درهنگام تایید از سوی بانک مواجه شده است. در این شرایط می توان با فراخوانی مجدد در بازه زمانی کمتر از ۱۵ دقیقه که کاربر بازگشته است٬ عملیات تایید را مجدد درخواست کرد. شرح تایید مجدد در پایین تر آورده شده است. 
 
1. `CANCEL_BY_USER`: پرداخت توسط کاربر کنسل شده است. 

1. `EXPIRE_GATEWAY_TOKEN`: ارتباط با درگاه بانک برقرار شده ولی کاربر به درگاه هدایت نشده است. 

1. `EXPIRE_VERIFY_PAYMENT`: در بازه زمانی ۱۵ دقیقه پس از بازگشت٬ موفق به تایید اطلاعات پرداخت نشده ایم. 

1. `COMPLETE`: وضعیت پرداخت موفق است.


```python
import logging

from django.http import HttpResponse, Http404
from django.urls import reverse

from azbankgateways import bankfactories, models as bank_models, default_settings as settings


def callback_gateway_view(request):
    tracking_code = request.GET.get(settings.TRACKING_CODE_QUERY_PARAM, None)
    if not tracking_code:
        logging.debug("این لینک معتبر نیست.")
        raise Http404

    try:
        bank_record = bank_models.Bank.objects.get(tracking_code=tracking_code)
    except bank_models.Bank.DoesNotExist:
        logging.debug("این لینک معتبر نیست.")
        raise Http404

    # در این قسمت باید از طریق داده هایی که در بانک رکورد وجود دارد، رکورد متناظر یا هر اقدام مقتضی دیگر را انجام دهیم
    if bank_record.is_success:
        # پرداخت با موفقیت انجام پذیرفته است و بانک تایید کرده است.
        # می توانید کاربر را به صفحه نتیجه هدایت کنید یا نتیجه را نمایش دهید.
        return HttpResponse("پرداخت با موفقیت انجام شد.")

    # پرداخت موفق نبوده است. اگر پول کم شده است ظرف مدت ۴۸ ساعت پول به حساب شما بازخواهد گشت.
    return HttpResponse("پرداخت با شکست مواجه شده است. اگر پول کم شده است ظرف مدت ۴۸ ساعت پول به حساب شما بازخواهد گشت.")
```


<h2 dir="rtl">درخواست تایید مجدد از بانک</h2>

```python
import logging
from azbankgateways import bankfactories, models as bank_models, default_settings as settings

factory = bankfactories.BankFactory()

# غیر فعال کردن رکورد های قدیمی
bank_models.Bank.objects.update_expire_records()

# مشخص کردن رکوردهایی که باید تعیین وضعیت شوند
for item in bank_models.Bank.objects.filter_return_from_bank():
	bank = factory.create(bank_type=item.bank_type, identifier=item.bank_choose_identifier)
	bank.verify(item.tracking_code)		
	bank_record = bank_models.Bank.objects.get(tracking_code=item.tracking_code)
	if bank_record.is_success:
		logging.debug("This record is verify now.", extra={'pk': bank_record.pk})

```


# TODO

- [X] Documentation

- [X] Support multiple provider 

- [X] Auto rotation

- [X] Priority auto rotation

- [X] Bank connection fail handling for auto rotation

- [X] Bank model structure

- [X] BMI gateway support

- [X] Zarinpal gateway support

- [X] IDPay gateway support

- [X] Zibal gateway support

- [X] Bahamta gateway support

- [X] Saman gateway support


## توسعه

<p dir="rtl">
 اگر از این بسته استفاده می کنید و خوشتون اومده با دادن ستاره به ما دلگرمی بدید.البته که اگر زمان بگذارید و گسترش بدید خیلی استقبال می کنیم و خوشحال میشیم. البته که در هیچ کدوم از این موارد اصراری نیست. 
</p>
<p dir="rtl">
 شاد باشید و خندون
</p>

## License

The MIT License (MIT). Please see [License File](LICENSE) for more information.
