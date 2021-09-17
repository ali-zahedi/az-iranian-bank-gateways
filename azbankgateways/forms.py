from django import forms


class PaymentSampleForm(forms.Form):
    amount = forms.IntegerField(label='Amount', initial=1000)
    mobile_number = forms.CharField(label='Mobile', max_length=100, initial='+989112223344')
