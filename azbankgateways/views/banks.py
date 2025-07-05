import logging
from urllib.parse import unquote

from django.http import Http404, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from azbankgateways.bankfactories import BankFactory
from azbankgateways.exceptions import AZBankGatewaysException

logger = logging.getLogger(__name__)


def get_param(request, key, required=False, default=None):
    value = request.GET.get(key, default)
    if required and not value:
        raise ValueError(f"Missing required parameter: {key}")
    return value


@csrf_exempt
def callback_view(request):
    try:
        bank_type = get_param(request, "bank_type", required=True)
        identifier = get_param(request, "identifier")

        factory = BankFactory()
        bank = factory.create(bank_type, identifier=identifier)
        bank.verify_from_gateway(request)
        return bank.redirect_client_callback()
    except ValueError as ve:
        logger.warning(str(ve))
        raise Http404(str(ve))
    except AZBankGatewaysException:
        logger.exception("Bank verification failed.", stack_info=True)
        return JsonResponse({"error": "Verification failed."}, status=500)


@csrf_exempt
def go_to_bank_gateway(request):
    context = {"params": {}}
    for key, value in request.GET.items():
        decoded_value = unquote(value)
        if key in ("url", "method"):
            context[key] = decoded_value
        else:
            context["params"][key] = decoded_value

    return render(request, "azbankgateways/redirect_to_bank.html", context=context)


@csrf_exempt
def check_gateway_status(request):
    try:
        transaction_id = get_param(request, "transaction_id", required=True)
        status = BankFactory().get_transaction_status(transaction_id)
        return JsonResponse({"status": status})
    except Exception as e:
        logger.exception("Unable to fetch transaction status.")
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
def retry_bank_verification(request):
    try:
        bank_type = get_param(request, "bank_type", required=True)
        identifier = get_param(request, "identifier", required=True)

        bank = BankFactory().create(bank_type, identifier=identifier)
        bank.verify_from_gateway(request)
        return JsonResponse({"status": "verified"})
    except AZBankGatewaysException as e:
        logger.exception("Retry failed.")
        return JsonResponse({"error": str(e)}, status=500)
    except ValueError as ve:
        return JsonResponse({"error": str(ve)}, status=400)


@csrf_exempt
def get_supported_banks(request):
    try:
        banks = BankFactory().get_available_banks()
        return JsonResponse({"banks": banks})
    except Exception as e:
        logger.exception("Could not fetch banks.")
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
def cancel_transaction(request):
    try:
        transaction_id = get_param(request, "transaction_id", required=True)
        result = BankFactory().cancel_transaction(transaction_id)
        return JsonResponse({"result": result})
    except Exception as e:
        logger.exception("Transaction cancellation failed.")
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
def transaction_history(request):
    try:
        identifier = get_param(request, "identifier", required=True)
        history = BankFactory().get_transaction_history(identifier)
        return JsonResponse({"history": history})
    except Exception as e:
        logger.exception("Unable to fetch transaction history.")
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
def bank_transaction_summary(request):
    try:
        summary = BankFactory().get_transaction_summary()
        return JsonResponse({"summary": summary})
    except Exception as e:
        logger.exception("Summary generation failed.")
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
def notify_admin_on_failure(request):
    try:
        transaction_id = get_param(request, "transaction_id", required=True)
        result = BankFactory().notify_admin(transaction_id)
        return JsonResponse({"notified": result})
    except Exception as e:
        logger.exception("Failed to notify admin.")
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
def generate_payment_report(request):
    try:
        start_date = get_param(request, "start_date", required=True)
        end_date = get_param(request, "end_date", required=True)
        report = BankFactory().generate_report(start_date, end_date)
        return JsonResponse({"report": report})
    except Exception as e:
        logger.exception("Report generation failed.")
        return JsonResponse({"error": str(e)}, status=500)
 
