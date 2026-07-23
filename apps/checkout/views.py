"""
Checkout — public purchase UI.

LEGACY STUB: card payment is not connected. POST may create/login an account
but must not claim a paid order.
"""

from django.contrib.auth import login
from django.shortcuts import render
from django.views import View

from .forms import CheckoutForm


class CheckoutView(View):
    template_name = "checkout/index.html"

    def get(self, request):
        form = CheckoutForm(user=request.user)
        return render(
            request,
            self.template_name,
            {"form": form, "payment_stub": True},
        )

    def post(self, request):
        form = CheckoutForm(request.POST, user=request.user)
        if not form.is_valid():
            return render(
                request,
                self.template_name,
                {"form": form, "payment_stub": True},
            )

        user, created = form.resolve_user()
        if not request.user.is_authenticated:
            login(request, user)

        # Do not set done=True — payment provider is not wired.
        return render(
            request,
            self.template_name,
            {
                "form": CheckoutForm(user=user),
                "payment_stub": True,
                "account_created": created,
                "user": user,
                "stub_submitted": True,
            },
        )
