from django.urls import path
from .views import ComplianceWebhook

urlpatterns = [
    path('', ComplianceWebhook.as_view(), name='compliance_webhook'),
]