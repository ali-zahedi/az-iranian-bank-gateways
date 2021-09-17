from django import forms


class PaymentSampleForm(forms.Form):
    amount = forms.IntegerField(label='Amount', initial=10000)
    mobile_number = forms.CharField(label='Mobile', max_length=13, initial='+989112223344')
