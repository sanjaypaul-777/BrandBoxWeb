"""
apps/checkout/urls.py — URL routes for /checkout/.
"""

from django.urls import path

from .views import CheckoutView

app_name = "checkout"

urlpatterns = [
    path("", CheckoutView.as_view(), name="index"),
]
