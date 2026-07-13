"""Catalog money: always store USD (detect FX → convert → cents fix)."""

from __future__ import annotations

import re
import time
from decimal import Decimal, InvalidOperation
from typing import Any

import httpx

# Symbols + ISO codes we strip before parsing the numeric amount.
_CURRENCY_TOKEN = re.compile(
    r"(?:USD|EUR|GBP|CAD|AUD|INR|NZD|JPY|CHF|SEK|NOK|DKK|MXN|BRL|ZAR|PLN|SGD|HKD|TRY|AED|"
    r"Rs\.?|USD\$|US\$|A\$|C\$|CA\$|AU\$|NZ\$|HK\$|"
    r"[€£¥₹$₽₩₪])",
    re.IGNORECASE,
)

# Detect currency from raw price text / symbols / ISO codes.
_DETECT_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\bUSD\b|US\$|USD\$", re.I), "USD"),
    (re.compile(r"\bEUR\b|€", re.I), "EUR"),
    (re.compile(r"\bGBP\b|£", re.I), "GBP"),
    (re.compile(r"\bCAD\b|C\$|CA\$", re.I), "CAD"),
    (re.compile(r"\bAUD\b|A\$|AU\$", re.I), "AUD"),
    (re.compile(r"\bNZD\b|NZ\$", re.I), "NZD"),
    (re.compile(r"\bINR\b|Rs\.?|₹", re.I), "INR"),
    (re.compile(r"\bJPY\b|¥|円", re.I), "JPY"),
    (re.compile(r"\bCHF\b", re.I), "CHF"),
    (re.compile(r"\bSEK\b", re.I), "SEK"),
    (re.compile(r"\bNOK\b", re.I), "NOK"),
    (re.compile(r"\bDKK\b", re.I), "DKK"),
    (re.compile(r"\bMXN\b", re.I), "MXN"),
    (re.compile(r"\bBRL\b|R\$", re.I), "BRL"),
    (re.compile(r"\bZAR\b", re.I), "ZAR"),
    (re.compile(r"\bPLN\b|zł", re.I), "PLN"),
    (re.compile(r"\bSGD\b", re.I), "SGD"),
    (re.compile(r"\bHKD\b|HK\$", re.I), "HKD"),
    (re.compile(r"\bTRY\b|₺", re.I), "TRY"),
    (re.compile(r"\bAED\b", re.I), "AED"),
    # Bare $ last — treat as USD unless country hint says otherwise
    (re.compile(r"\$"), "USD"),
]

_COUNTRY_CURRENCY = {
    "US": "USD",
    "USA": "USD",
    "UNITED STATES": "USD",
    "GB": "GBP",
    "UK": "GBP",
    "UNITED KINGDOM": "GBP",
    "CA": "CAD",
    "CANADA": "CAD",
    "AU": "AUD",
    "AUSTRALIA": "AUD",
    "NZ": "NZD",
    "DE": "EUR",
    "FR": "EUR",
    "IT": "EUR",
    "ES": "EUR",
    "NL": "EUR",
    "BE": "EUR",
    "AT": "EUR",
    "IE": "EUR",
    "PT": "EUR",
    "IN": "INR",
    "INDIA": "INR",
    "JP": "JPY",
    "JAPAN": "JPY",
    "CH": "CHF",
    "SE": "SEK",
    "NO": "NOK",
    "DK": "DKK",
    "MX": "MXN",
    "BR": "BRL",
    "ZA": "ZAR",
    "PL": "PLN",
    "SG": "SGD",
    "HK": "HKD",
    "TR": "TRY",
    "AE": "AED",
}

# Approximate USD per 1 unit of currency (fallback when API unavailable).
# Updated periodically; Frankfurter live rates preferred.
_FALLBACK_USD_PER_UNIT = {
    "USD": Decimal("1"),
    "EUR": Decimal("1.08"),
    "GBP": Decimal("1.27"),
    "CAD": Decimal("0.73"),
    "AUD": Decimal("0.65"),
    "NZD": Decimal("0.60"),
    "INR": Decimal("0.012"),
    "JPY": Decimal("0.0067"),
    "CHF": Decimal("1.12"),
    "SEK": Decimal("0.095"),
    "NOK": Decimal("0.092"),
    "DKK": Decimal("0.145"),
    "MXN": Decimal("0.058"),
    "BRL": Decimal("0.18"),
    "ZAR": Decimal("0.055"),
    "PLN": Decimal("0.25"),
    "SGD": Decimal("0.74"),
    "HKD": Decimal("0.128"),
    "TRY": Decimal("0.029"),
    "AED": Decimal("0.272"),
}

_rate_cache: dict[str, tuple[float, Decimal]] = {}  # currency -> (expires_epoch, usd_per_unit)
_RATE_TTL_SEC = 6 * 60 * 60


def detect_currency(
    value: Any = None,
    *,
    explicit: str | None = None,
    country: str | None = None,
) -> str:
    """Return ISO currency code (default USD)."""
    if explicit:
        code = str(explicit).strip().upper()
        if len(code) == 3:
            return code
    if value is not None:
        s = str(value)
        for pat, code in _DETECT_PATTERNS:
            if pat.search(s):
                # Bare $ + non-US country → prefer country currency
                if code == "USD" and "$" in s and "US" not in s.upper() and country:
                    hinted = _COUNTRY_CURRENCY.get(str(country).strip().upper())
                    if hinted and hinted != "USD":
                        return hinted
                return code
    if country:
        hinted = _COUNTRY_CURRENCY.get(str(country).strip().upper())
        if hinted:
            return hinted
        # Try full country name contained in label
        label = str(country).strip().upper()
        for key, code in _COUNTRY_CURRENCY.items():
            if key in label or label in key:
                return code
    return "USD"


def parse_usd_amount(value: Any) -> Decimal | None:
    """Parse numeric amount (no FX). Strips currency symbols/codes."""
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, Decimal):
        return value.quantize(Decimal("0.01"))
    if isinstance(value, (int, float)):
        try:
            return Decimal(str(value)).quantize(Decimal("0.01"))
        except (InvalidOperation, ValueError):
            return None

    s = str(value).strip()
    if not s or s.lower() in ("none", "null", "n/a", "nan", "new version"):
        return None

    s = _CURRENCY_TOKEN.sub("", s).strip()
    if re.search(r",\d{1,2}$", s) and "." in s:
        s = s.replace(".", "").replace(",", ".")
    elif re.search(r",\d{1,2}$", s):
        s = s.replace(",", ".")
    else:
        s = s.replace(",", "")

    m = re.search(r"(\d+(?:\.\d+)?)", s)
    if not m:
        return None
    try:
        return Decimal(m.group(1)).quantize(Decimal("0.01"))
    except (InvalidOperation, ValueError):
        return None


def _fetch_live_usd_rate(currency: str) -> Decimal | None:
    """Frankfurter free API: how many USD per 1 unit of currency."""
    currency = currency.upper()
    if currency == "USD":
        return Decimal("1")
    try:
        with httpx.Client(timeout=4.0) as client:
            # INR etc. — frankfurter may not support all; try anyway
            resp = client.get(
                f"https://api.frankfurter.app/latest?from={currency}&to=USD"
            )
            if resp.status_code != 200:
                return None
            data = resp.json()
            rate = data.get("rates", {}).get("USD")
            if rate is None:
                return None
            return Decimal(str(rate))
    except Exception:
        return None


def usd_rate(currency: str) -> Decimal:
    """USD amount for 1 unit of `currency` (cached)."""
    currency = (currency or "USD").upper()
    if currency == "USD":
        return Decimal("1")
    now = time.time()
    cached = _rate_cache.get(currency)
    if cached and cached[0] > now:
        return cached[1]
    live = _fetch_live_usd_rate(currency)
    rate = live if live is not None else _FALLBACK_USD_PER_UNIT.get(currency, Decimal("1"))
    _rate_cache[currency] = (now + _RATE_TTL_SEC, rate)
    return rate


def to_usd(amount: Decimal, currency: str) -> Decimal:
    """Convert amount in `currency` to USD."""
    currency = (currency or "USD").upper()
    if currency == "USD":
        return amount.quantize(Decimal("0.01"))
    converted = (amount * usd_rate(currency)).quantize(Decimal("0.01"))
    return converted


def coerce_shopify_cents(
    value: Any,
    *,
    reference: Any = None,
) -> Decimal | None:
    """
    Shopify liquid/Admin often exposes money as integer cents (2999 → $29.99).
    """
    amount = parse_usd_amount(value)
    if amount is None or amount <= 0:
        return None
    ref = parse_usd_amount(reference)
    is_whole = amount == amount.to_integral_value()
    if not is_whole or amount < 100:
        return amount
    as_dollars = (amount / Decimal(100)).quantize(Decimal("0.01"))
    if ref and ref > 0:
        if amount >= ref * 10 and Decimal("0.25") * ref <= as_dollars <= ref * 8:
            return as_dollars
        if amount >= ref * 20 and as_dollars < amount:
            return as_dollars
    cents_part = int(amount) % 100
    if cents_part in (0, 49, 50, 90, 95, 99) and Decimal("0.99") <= as_dollars <= Decimal(
        "299.99"
    ):
        if amount <= 200 and cents_part == 0:
            return amount
        return as_dollars
    if amount >= 1000 and as_dollars <= Decimal("500"):
        return as_dollars
    return amount


def normalize_usd(value: Any, default: str = "") -> str:
    """Store-ready USD amount string (no FX)."""
    amount = parse_usd_amount(value)
    if amount is None or amount <= 0:
        return default
    return f"{amount:.2f}"


def normalize_price_usd(
    value: Any,
    default: str = "",
    *,
    currency: str | None = None,
    country: str | None = None,
) -> str:
    """
    Normalize product cost/price to USD only:
    detect currency → optional Shopify-cents fix → FX to USD.
    """
    cur = detect_currency(value, explicit=currency, country=country)
    # Shopify cents only for major shop currencies (not INR/JPY/etc.)
    if cur in ("USD", "CAD", "AUD", "EUR", "GBP", "NZD", "CHF", "SEK", "NOK", "DKK", "MXN"):
        amount = coerce_shopify_cents(value)
    else:
        amount = parse_usd_amount(value)
    if amount is None or amount <= 0:
        return default
    usd = to_usd(amount, cur)
    if usd <= 0:
        return default
    return f"{usd:.2f}"


def normalize_compare_usd(
    value: Any,
    *,
    cost: Any = None,
    sell: Any = None,
    currency: str | None = None,
    country: str | None = None,
) -> str:
    """Normalize compare-at to USD (same FX as price)."""
    cur = detect_currency(value, explicit=currency, country=country)
    ref = cost if parse_usd_amount(cost) else sell
    if cur in ("USD", "CAD", "AUD", "EUR", "GBP", "NZD", "CHF", "SEK", "NOK", "DKK", "MXN"):
        amount = coerce_shopify_cents(value, reference=None if cur != "USD" else ref)
    else:
        amount = parse_usd_amount(value)
    if amount is None or amount <= 0:
        return ""
    usd = to_usd(amount, cur)
    if usd <= 0:
        return ""
    return f"{usd:.2f}"


def format_usd(value: Any, default: str = "$0.00") -> str:
    """UI label always as $X.XX."""
    amount = parse_usd_amount(value)
    if amount is None:
        return default
    return f"${amount:.2f}"


def money_or_default(value: Any, default: str = "0") -> Decimal:
    """Decimal for math; falls back to default when unparseable."""
    amount = parse_usd_amount(value)
    if amount is not None:
        return amount
    fallback = parse_usd_amount(default)
    return fallback if fallback is not None else Decimal("0.00")


def pick_offer_price_and_currency(offers: Any) -> tuple[str, str]:
    """
    From JSON-LD offers, prefer USD offer; else first offer + its currency.
    Returns (price_str, currency_code).
    """
    if isinstance(offers, dict):
        cur = str(offers.get("priceCurrency") or "USD").upper() or "USD"
        return str(offers.get("price") or ""), cur
    if not isinstance(offers, list) or not offers:
        return "", "USD"
    usd = None
    first = None
    for o in offers:
        if not isinstance(o, dict):
            continue
        if first is None and o.get("price") not in (None, ""):
            first = o
        cur = str(o.get("priceCurrency") or "").upper()
        if cur == "USD" and o.get("price") not in (None, ""):
            usd = o
            break
    chosen = usd or first
    if not chosen:
        return "", "USD"
    return str(chosen.get("price") or ""), str(chosen.get("priceCurrency") or "USD").upper() or "USD"


def pick_usd_offer_price(offers: Any) -> str:
    """Back-compat: price string only (prefer USD offer)."""
    price, _cur = pick_offer_price_and_currency(offers)
    return price
