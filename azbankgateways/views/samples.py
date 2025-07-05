import logging

from django.http import Http404, JsonResponse
from django.shortcuts import render
from django.urls import reverse

from azbankgateways import bankfactories
from azbankgateways import default_settings as settings
from azbankgateways import models as bank_models
from azbankgateways.exceptions import AZBankGatewaysException

from ..forms import PaymentSampleForm


def sample_payment_view(request):
    if request.method == "POST":
        form = PaymentSampleForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data["amount"]
            mobile_number = form.cleaned_data["mobile_number"]
            factory = bankfactories.BankFactory()
            try:
                bank = factory.auto_create()
                bank.set_request(request)
                bank.set_amount(amount)
                bank.set_client_callback_url(reverse(settings.SAMPLE_RESULT_NAMESPACE))
                bank.set_mobile_number(mobile_number)

                bank_record = bank.ready()

                if settings.IS_SAMPLE_FORM_ENABLE:
                    return render(request, 'azbankgateways/redirect_to_bank.html', context=bank.get_gateway())
                return bank.redirect_gateway()
            except AZBankGatewaysException as e:
                logging.critical(e)
                return render(request, "azbankgateways/samples/error.html", {"error": str(e)})
    else:
        form = PaymentSampleForm()

    return render(request, "azbankgateways/samples/gateway.html", {"form": form})


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

    return render(request, "azbankgateways/samples/result.html", {"bank_record": bank_record})


def sample_status_api(request):
    tracking_code = request.GET.get(settings.TRACKING_CODE_QUERY_PARAM)
    if not tracking_code:
        return JsonResponse({"error": "Tracking code is required."}, status=400)

    try:
        bank_record = bank_models.Bank.objects.get(tracking_code=tracking_code)
        return JsonResponse({
            "amount": bank_record.amount,
            "status": bank_record.status,
            "transaction_code": bank_record.transaction_code,
            "card_number": bank_record.card_number,
            "bank_name": bank_record.bank_name,
        })
    except bank_models.Bank.DoesNotExist:
        return JsonResponse({"error": "Transaction not found."}, status=404)


def sample_cancel_view(request):
    tracking_code = request.GET.get(settings.TRACKING_CODE_QUERY_PARAM)
    if not tracking_code:
        return JsonResponse({"error": "Tracking code is required."}, status=400)

    try:
        bank_record = bank_models.Bank.objects.get(tracking_code=tracking_code)
        if bank_record.status != bank_models.Bank.STATUS_PENDING:
            return JsonResponse({"error": "Only pending transactions can be cancelled."}, status=400)

        bank_record.status = bank_models.Bank.STATUS_CANCELED_MANUAL
        bank_record.save()
        return JsonResponse({"success": True, "message": "Transaction cancelled."})
    except bank_models.Bank.DoesNotExist:
        return JsonResponse({"error": "Transaction not found."}, status=404)


def sample_payment_history(request):
    records = bank_models.Bank.objects.all().order_by('-created_at')[:10]
    data = []
    for rec in records:
        data.append({
            "tracking_code": rec.tracking_code,
            "amount": rec.amount,
            "status": rec.status,
            "created_at": rec.created_at.strftime('%Y-%m-%d %H:%M'),
        })
    return JsonResponse({"payments": data})


def sample_verify_status(request):
    tracking_code = request.GET.get(settings.TRACKING_CODE_QUERY_PARAM)
    if not tracking_code:
        return JsonResponse({"error": "Tracking code is required."}, status=400)

    try:
        bank_record = bank_models.Bank.objects.get(tracking_code=tracking_code)
        if bank_record.status == bank_models.Bank.STATUS_SUCCESS:
            return JsonResponse({"verified": True, "message": "Transaction was successful."})
        else:
            return JsonResponse({"verified": False, "message": "Transaction was not successful."})
    except bank_models.Bank.DoesNotExist:
        return JsonResponse({"error": "Transaction not found."}, status=404)


def sample_transaction_detail(request):
    tracking_code = request.GET.get(settings.TRACKING_CODE_QUERY_PARAM)
    if not tracking_code:
        return JsonResponse({"error": "Tracking code is required."}, status=400)

    try:
        bank_record = bank_models.Bank.objects.get(tracking_code=tracking_code)
        detail = {
            "tracking_code": bank_record.tracking_code,
            "amount": bank_record.amount,
            "status": bank_record.status,
            "transaction_code": bank_record.transaction_code,
            "card_number": bank_record.card_number,
            "bank_name": bank_record.bank_name,
            "created_at": bank_record.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            "verified_at": bank_record.verified_at.strftime('%Y-%m-%d %H:%M:%S') if bank_record.verified_at else None
        }
        return JsonResponse({"transaction": detail})
    except bank_models.Bank.DoesNotExist:
        return JsonResponse({"error": "Transaction not found."}, status=404)


def sample_total_amount_by_status(request):
    """
    Return the total payment amount grouped by transaction status.
    """
    from django.db.models import Sum
    grouped = bank_models.Bank.objects.values('status').annotate(total=Sum('amount'))
    result = {entry['status']: entry['total'] for entry in grouped}
    return JsonResponse({"totals_by_status": result})


def sample_most_recent_success(request):
    """
    Return the most recent successful transaction.
    """
    try:
        latest = bank_models.Bank.objects.filter(status=bank_models.Bank.STATUS_SUCCESS).latest('created_at')
        return JsonResponse({
            "tracking_code": latest.tracking_code,
            "amount": latest.amount,
            "created_at": latest.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    except bank_models.Bank.DoesNotExist:
        return JsonResponse({"error": "No successful transaction found."}, status=404)


def sample_refund_eligible_transactions(request):
    """
    List transactions that may be eligible for refund (e.g., status success but flagged by business logic).
    """
    eligible = bank_models.Bank.objects.filter(status=bank_models.Bank.STATUS_SUCCESS, is_flagged=True)
    data = [{
        "tracking_code": r.tracking_code,
        "amount": r.amount,
        "created_at": r.created_at.strftime('%Y-%m-%d %H:%M')
    } for r in eligible]
    return JsonResponse({"eligible_for_refund": data})
 
