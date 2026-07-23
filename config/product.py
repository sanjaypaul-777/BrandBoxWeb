"""
Public offer / affiliate display numbers.

Prefer editing in Django admin:
  Home → Site offer settings
  (offer %, countdown end, affiliate %)

Defaults below are fallbacks if the DB row is missing.
Coach chat strings stay here until you move them to admin later.
"""

from __future__ import annotations

from django.utils import timezone

# Fallbacks only (used if admin row missing)
OFFER_PERCENT = 65
OFFER_END_ISO = "2026-07-31T23:59:59+05:30"
AFFILIATE_PERCENT = 30

COACH_WELCOME = "Hey — what do you want to get done today?"
COACH_STATUS_BOT = "You've got this — ask anything and grow with confidence."
COACH_STATUS_WAITING = "A coach is on the way — hang tight."
COACH_STATUS_CLOSED = "Chat closed — start a new message anytime."


def _load_offer():
    """Return (offer_percent, affiliate_percent, offer_end_iso)."""
    try:
        from apps.home.models import SiteOfferSettings

        row = SiteOfferSettings.load()
        end = row.offer_ends_at
        if timezone.is_naive(end):
            end = timezone.make_aware(end)
        return (
            int(row.offer_percent),
            int(row.affiliate_percent),
            end.isoformat(),
        )
    except Exception:
        return OFFER_PERCENT, AFFILIATE_PERCENT, OFFER_END_ISO


def as_template_context() -> dict:
    offer_percent, affiliate_percent, offer_end_iso = _load_offer()
    return {
        "offer_badge": f"{offer_percent}% Off",
        "offer_cta_lock_in": f"Lock in {offer_percent}% off",
        "offer_cta_claim": f"Claim {offer_percent}% Discount",
        "offer_end_iso": offer_end_iso,
        "offer_footnote": (
            f"*{offer_percent}% off Plus annual for year one. "
            "Renews at the standard rate unless canceled. Offer may change."
        ),
        "offer_faq_blurb": (
            f"Eligible customers can get {offer_percent}% off Plus Annual for the first year. "
            "Check checkout for the current price and what’s included on your plan."
        ),
        "affiliate_commission_label": f"{affiliate_percent}%+",
        "affiliate_commission_blurb": (
            f"{affiliate_percent}%+ on every referred sale, not a flat one-time fee."
        ),
        "affiliate_commission_detail": (
            f"Partners start at {affiliate_percent}%+ commission per sale, with rates that "
            "can increase based on performance."
        ),
    }
