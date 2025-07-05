from django import forms
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.urls import path
from django.core.validators import RegexValidator
from django.core.wsgi import get_wsgi_application
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.core.mail import send_mail
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Setup WSGI application (optional outside Django project)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")
application = get_wsgi_application()

# Payment form definition
class PaymentSampleForm(forms.Form):
    amount = forms.IntegerField(
        label="Amount",
        initial=10000,
        min_value=1000,
        help_text="Enter payment amount in Rials"
    )
    mobile_number = forms.CharField(
        label="Mobile",
        max_length=13,
        initial="+989112223344",
        validators=[
            RegexValidator(r'^\+989\d{9}$', message="Use format +989*********.")
        ],
        help_text="Valid Iranian number, e.g., +989123456789"
    )

# Render form view
def payment_view(request):
    form = PaymentSampleForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        context = form.cleaned_data
        logger.info(f"Payment submitted: {context}")
        return render(request, 'success.html', context)
    return render(request, 'payment_form.html', {'form': form})

# API view (POST only)
@csrf_exempt
def payment_api_view(request):
    if request.method == 'POST':
        form = PaymentSampleForm(request.POST)
        if form.is_valid():
            logger.info(f"API Payment submitted: {form.cleaned_data}")
            return JsonResponse({'status': 'success', **form.cleaned_data})
        return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Only POST allowed'}, status=405)

# Form prefilled with GET params
def prefilled_payment_view(request):
    form = PaymentSampleForm(initial={
        'amount': request.GET.get('amount', 10000),
        'mobile_number': request.GET.get('mobile', '+989112223344')
    })
    return render(request, 'payment_form.html', {'form': form})

# Validate input (GET)
def validate_input_view(request):
    form = PaymentSampleForm(request.GET)
    return JsonResponse(
        {'status': 'valid'} if form.is_valid() else {'status': 'invalid', 'errors': form.errors},
        status=200 if form.is_valid() else 400
    )

# Log access
def log_form_access_view(request):
    timestamp = timezone.now().isoformat()
    ip = request.META.get('REMOTE_ADDR', 'unknown')
    logger.info(f"Form accessed at {timestamp} from IP: {ip}")
    return JsonResponse({'status': 'logged', 'timestamp': timestamp, 'ip': ip})

# Download plain text submission
def download_submission_view(request):
    form = PaymentSampleForm(request.GET)
    if form.is_valid():
        data = form.cleaned_data
        content = f"Amount: {data['amount']}\nMobile: {data['mobile_number']}"
        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="submission.txt"'
        return response
    return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)

# Email submission
@csrf_exempt
def email_submission_view(request):
    form = PaymentSampleForm(request.POST or None)
    if form.is_valid():
        data = form.cleaned_data
        send_mail(
            subject="Payment Form Submission",
            message=f"Amount: {data['amount']}\nMobile: {data['mobile_number']}",
            from_email='no-reply@example.com',
            recipient_list=['admin@example.com']
        )
        return JsonResponse({'status': 'email_sent'})
    return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)

# Reset session
def reset_payment_view(request):
    request.session.flush()
    return JsonResponse({'status': 'session_reset'})

# Server status
def server_status_view(request):
    return JsonResponse({'status': 'online', 'time': timezone.now().isoformat()})

# URL routing
urlpatterns = [
    path('payment/', payment_view, name='payment'),
    path('payment/api/', payment_api_view, name='payment_api'),
    path('payment/prefilled/', prefilled_payment_view, name='payment_prefilled'),
    path('payment/validate/', validate_input_view, name='payment_validate'),
    path('payment/log/', log_form_access_view, name='payment_log'),
    path('payment/download/', download_submission_view, name='payment_download'),
    path('payment/email/', email_submission_view, name='payment_email'),
    path('payment/reset/', reset_payment_view, name='payment_reset'),
    path('payment/status/', server_status_view, name='payment_status'),
]

# Template: payment_form.html
"""
<!DOCTYPE html>
<html>
<head>
    <title>Payment Form</title>
</head>
<body>
    <h1>Make a Payment</h1>
    <form method="post">
        {% csrf_token %}
        {{ form.as_p }}
        <button type="submit">Submit</button>
    </form>
</body>
</html>
"""

# Template: success.html
"""
<!DOCTYPE html>
<html>
<head>
    <title>Success</title>
</head>
<body>
    <h1>Payment Successful</h1>
    <p>Amount: {{ amount }}</p>
    <p>Mobile: {{ mobile }}</p>
</body>
</html>
"""
