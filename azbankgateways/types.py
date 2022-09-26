

class PayIRParams:
    """
    Pay.ir Parameters type:
    ابتدا می بایست پارامترهای موجود در جدول زیر رو با متد POST به آدرسی که مشخص شده ارسال کنید. به نوع داده ها و نام فیلد توجه کنید.


    api (String) :
        API Key دریافتی از پنل کاربری شما که بعد از تایید درخواست درگاه صادر میشه

    amount (Integer):
        مبلغ تراکنش به صورت ریال و بدون رقم اعشار. بزرگتر یا مساوی 10,000 ریال

    redirect (String):
        آدرس بازگشتی که باید به صورت urlencode ارسال بشه و باید با آدرس درگاه پرداخت تایید شده در شبکه پرداخت پی در یک ادرس باشه

    mobile (String):
        شماره موبایل ( اختیاری ، جهت نمایش شماره کارت Mask شده روی درگاه )

    factorNumber (String):
        شماره فاکتور شما ( اختیاری )

    description (String):
        توضیحات تراکنش ( اختیاری ، حداکثر 255 کاراکتر )

    validCardNumber (String):
        اعلام شماره کارت مجاز برای انجام تراکنش ( اختیاری، بصورت عددی (لاتین) و چسبیده بهم در 16 رقم. مثال 6219861012345678 )    
    """

    def __init__(self, api: str, amount: int, redirect: str, mobile: str | None, factorNumber: str | None, description: str | None, validCardNumber: str | None) -> None:
        self.api = api
        self.amount = amount
        self.redirect = redirect
        self.mobile = mobile
        self.factorNumber = factorNumber
        self.description = description
        self.validCardNumber = validCardNumber

    def __repr__(self) -> str:
        return "PayIRParams(api={0}, amount={1}, redirect={2}, mobile={3}, factorNumber={4}, description={5}, validCardNumber={6})" % (
         self.api
        ,self.amount
        ,self.redirect
        ,self.mobile
        ,self.factorNumber
        ,self.description
        ,self.validCardNumber
        )
    
        

