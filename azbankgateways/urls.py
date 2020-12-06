from django.conf.urls import url
from .views import callback_view

app_name = 'azbankgateways'

urlpatterns = [
    url(r'^callback/$', callback_view, name='callback'),
]
