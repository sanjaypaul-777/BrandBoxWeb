"""
Product Hunter + My Imports — local vault + Node Shopify bridge adapters.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from math import ceil
from typing import Any, Literal

from django.db.models import Q

from apps.catalog.services.money import format_usd, money_or_default, normalize_price_usd
from apps.dashboard.models import ShopConnection

ProductStatus = Literal["default", "imported", "in_store"]


def _money(value: Any, default: str = "0") -> Decimal:
    # Coerce Shopify-cents style amounts for display/math
    coerced = normalize_price_usd(value, "")
    if coerced:
        return money_or_default(coerced, default)
    return money_or_default(value, default)


def _hue_from_id(raw: str) -> int:
    total = sum(ord(c) for c in (raw or "x"))
    return 120 + (total % 160)


@dataclass
class FinderProduct:
    id: str
    title: str
    niche: str
    country: str
    cost: Decimal
    sell: Decimal
    source_url: str
    status: ProductStatus = "default"
    image_url: str = ""
    image_hue: int = 160
    already_imported: bool = False
    already_published: bool = False
    image_fallbacks: list[str] | None = None

    @property
    def margin_pct(self) -> int:
        if self.cost <= 0 or self.sell <= 0:
            return 0
        return int(round(((self.sell - self.cost) / self.sell) * 100))

    @property
    def cost_label(self) -> str:
        return format_usd(self.cost)

    @property
    def sell_label(self) -> str:
        return format_usd(self.sell)


@dataclass
class ImportItem:
    id: str
    title: str
    niche: str
    country: str
    cost: Decimal
    sell: Decimal
    compare_at: Decimal | None = None
    status: str = "imported"
    image_url: str = ""
    image_hue: int = 160
    push_failed: bool = False
    shopify_product_id: str = ""

    @property
    def cost_label(self) -> str:
        return format_usd(self.cost)

    @property
    def sell_label(self) -> str:
        return format_usd(self.sell)

    @property
    def compare_at_label(self) -> str | None:
        if self.compare_at is None:
            return None
        return format_usd(self.compare_at)


def connected_shop_for_user(user) -> ShopConnection | None:
    return ShopConnection.active_for_user(user)


def _normalize_image_url(url: str) -> str:
    raw = (url or "").strip().strip("'\"")
    if not raw:
        return ""
    if raw.startswith("//"):
        raw = "https:" + raw
    elif raw.startswith("http://"):
        raw = "https://" + raw[len("http://") :]
    return raw


def _image_candidates_from_row(row) -> list[str]:
    """Primary + gallery URLs; drop empties / dupes; add https + no-width variants."""
    seen: set[str] = set()
    out: list[str] = []

    def add(u: str) -> None:
        u = _normalize_image_url(u)
        if not u or u in seen:
            return
        seen.add(u)
        out.append(u)
        # Shopify sometimes 404s on &width=… — try without query size hints
        if "width=" in u or "_1920x" in u or "_1000x" in u:
            base = u.split("?")[0]
            if base and base not in seen:
                seen.add(base)
                out.append(base)

    add(getattr(row, "feature_image", "") or "")
    for part in (getattr(row, "product_images", "") or "").split(","):
        add(part)
    return out


def map_catalog_row(
    row, *, imported: bool = False, published: bool = False
) -> FinderProduct:
    """Map Winning Product Vault (CatalogProduct) → FinderProduct."""
    source_id = str(row.source_id or "")
    cost = _money(row.price, "10")
    sell = cost * 3
    if published:
        status: ProductStatus = "in_store"
    elif imported:
        status = "imported"
    else:
        status = "default"
    candidates = _image_candidates_from_row(row)
    image = candidates[0] if candidates else ""
    return FinderProduct(
        id=source_id,
        title=str(row.title or "Untitled"),
        niche=str(row.category or "—"),
        country=str(row.country or "—"),
        cost=cost,
        sell=sell,
        source_url=str(row.product_url or ""),
        status=status,
        image_url=image,
        image_hue=_hue_from_id(source_id),
        already_imported=imported or published,
        already_published=published,
        image_fallbacks=candidates[1:],
    )


def search_vault(
    *,
    q: str = "",
    country: str = "",
    niche: str = "",
    page: int = 1,
    page_size: int = 16,
    imported_ids: set[str] | None = None,
    published_ids: set[str] | None = None,
) -> dict[str, Any]:
    """
    Product Hunter catalog from Django SQL (Winning Product Vault).
    Does not call Node / Cloudflare.
    """
    from apps.catalog.models import CatalogProduct

    imported_ids = imported_ids or set()
    published_ids = published_ids or set()
    page = max(1, int(page))
    page_size = max(1, min(50, int(page_size)))

    qs = CatalogProduct.objects.filter(archived=False)
    if q:
        qs = qs.filter(
            Q(title__icontains=q)
            | Q(category__icontains=q)
            | Q(country__icontains=q)
            | Q(description__icontains=q)
        )
    if country:
        qs = qs.filter(country__iexact=country)
    if niche:
        qs = qs.filter(category__icontains=niche)

    total = qs.count()
    total_pages = max(1, ceil(total / page_size) if total else 1)
    if page > total_pages:
        page = total_pages
    offset = (page - 1) * page_size
    rows = list(qs.order_by("-updated_at")[offset : offset + page_size])

    products = [
        map_catalog_row(
            row,
            imported=row.source_id in imported_ids,
            published=row.source_id in published_ids,
        )
        for row in rows
    ]

    countries = list(
        CatalogProduct.objects.filter(archived=False)
        .exclude(country="")
        .values_list("country", flat=True)
        .distinct()
        .order_by("country")
    )
    niches = list(
        CatalogProduct.objects.filter(archived=False)
        .exclude(category="")
        .values_list("category", flat=True)
        .distinct()
        .order_by("category")
    )

    return {
        "ok": True,
        "products": products,
        "countries": countries,
        "niches": niches,
        "total": total,
        "page": page,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1,
    }


TOAST_VARIANTS = (
    {
        "key": "success",
        "label": "All pushed",
        "tone": "success",
        "message": "Products pushed — now live in your store.",
    },
    {
        "key": "partial",
        "label": "Partial",
        "tone": "warn",
        "message": "Some products pushed. Retry the ones that failed.",
    },
    {
        "key": "error",
        "label": "Failed",
        "tone": "error",
        "message": "We couldn't push your products. Try again.",
    },
)
