import logging

from django.http import Http404
from django.shortcuts import render
from django.urls import reverse

from azbankgateways import bankfactories, models as bank_models, default_settings as settings
from azbankgateways.apps import AZIranianBankGatewaysConfig
from azbankgateways.exceptions import AZBankGatewaysException
from ..forms import PaymentSampleForm


def sample_payment_view(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = PaymentSampleForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            amount = form.cleaned_data['amount']
            mobile_number = form.cleaned_data['mobile_number']
            factory = bankfactories.BankFactory()
            try:
                bank = factory.auto_create()
                bank.set_request(request)
                bank.set_amount(amount)
                # یو آر ال بازگشت به نرم افزار برای ادامه فرآیند
                bank.set_client_callback_url(reverse(f'{AZIranianBankGatewaysConfig.name}:sample-result'))
                bank.set_mobile_number(mobile_number)  # اختیاری

                # در صورت تمایل اتصال این رکورد به رکورد فاکتور یا هر چیزی که بعدا بتوانید ارتباط بین محصول یا خدمات را با این
                # پرداخت برقرار کنید.

                bank_record = bank.ready()

                # هدایت کاربر به درگاه بانک
                return bank.redirect_gateway()
            except AZBankGatewaysException as e:
                logging.critical(e)
                # TODO: redirect to failed result.
                raise e

    # if a GET (or any other method) we'll create a blank form
    else:
        form = PaymentSampleForm()

    return render(request, 'azbankgateways/samples/gateway.html', {'form': form})


def sample_result_view(request):
    tracking_code = request.GET.get(settings.TRACKING_CODE_QUERY_PARAM, None)
    if not tracking_code:
        logging.debug("این لینک معتبر نیست.")
        raise Http404

    try:
        bank_record = bank_models.Bank.objects.get(tracking_code=tracking_code)
    except bank_models.Bank.DoesNotExist:
        logging.debug("این لینک معتبر نیست.")
        raise Http404

    return render(request, 'azbankgateways/samples/result.html', {'bank_record': bank_record})
