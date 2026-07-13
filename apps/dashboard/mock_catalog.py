"""
UI shell only — backend later.

Shared mock catalog for Product Finder and My Imports.
Feature-aligned with the Zentra Shopify app flow:
Product Finder → Import → My Imports → Push to store.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Literal


ProductStatus = Literal["default", "imported", "in_store"]


COUNTRIES = [
    "United States",
    "United Kingdom",
    "Canada",
    "Australia",
    "Germany",
    "France",
]

NICHES = [
    "Living",
    "Peak",
    "Vogue",
    "Lux",
    "Paws",
    "Junior",
    "Care",
    "Tech",
    "Mart",
]


@dataclass(frozen=True)
class MockProduct:
    id: str
    title: str
    niche: str
    country: str
    cost: Decimal
    source_url: str
    status: ProductStatus = "default"
    image_hue: int = 160  # placeholder tint

    @property
    def sell(self) -> Decimal:
        return (self.cost * 3).quantize(Decimal("0.01"))

    @property
    def margin_pct(self) -> int:
        if self.cost <= 0:
            return 0
        return int(round(((self.sell - self.cost) / self.sell) * 100))

    @property
    def cost_label(self) -> str:
        return f"${self.cost:.2f}"

    @property
    def sell_label(self) -> str:
        return f"${self.sell:.2f}"


@dataclass
class MockImport:
    id: str
    title: str
    niche: str
    country: str
    cost: Decimal
    sell: Decimal
    compare_at: Decimal | None = None
    push_failed: bool = False
    editing: bool = False
    image_hue: int = 160

    @property
    def cost_label(self) -> str:
        return f"${self.cost:.2f}"

    @property
    def sell_label(self) -> str:
        return f"${self.sell:.2f}"

    @property
    def compare_at_label(self) -> str | None:
        if self.compare_at is None:
            return None
        return f"${self.compare_at:.2f}"


# 10 finder products — mix of Import / Added / In store states
FINDER_PRODUCTS: list[MockProduct] = [
    MockProduct(
        id="pf-01",
        title="Magnetic Floating Plant Shelf",
        niche="Living",
        country="United States",
        cost=Decimal("12.40"),
        source_url="https://example.com/products/magnetic-plant-shelf",
        status="default",
        image_hue=145,
    ),
    MockProduct(
        id="pf-02",
        title="Compact Resistance Band Kit Pro",
        niche="Peak",
        country="United Kingdom",
        cost=Decimal("9.80"),
        source_url="https://example.com/products/resistance-band-kit",
        status="imported",
        image_hue=200,
    ),
    MockProduct(
        id="pf-03",
        title="Silk Scrunchie Duo — Midnight",
        niche="Vogue",
        country="France",
        cost=Decimal("4.25"),
        source_url="https://example.com/products/silk-scrunchie-duo",
        status="default",
        image_hue=320,
    ),
    MockProduct(
        id="pf-04",
        title="Brushed Brass Desk Tray",
        niche="Lux",
        country="Germany",
        cost=Decimal("18.90"),
        source_url="https://example.com/products/brass-desk-tray",
        status="in_store",
        image_hue=40,
    ),
    MockProduct(
        id="pf-05",
        title="Orthopedic Memory Foam Pet Bed",
        niche="Paws",
        country="Canada",
        cost=Decimal("22.50"),
        source_url="https://example.com/products/memory-foam-pet-bed",
        status="default",
        image_hue=25,
    ),
    MockProduct(
        id="pf-06",
        title="Stackable Sensory Blocks Set",
        niche="Junior",
        country="Australia",
        cost=Decimal("14.10"),
        source_url="https://example.com/products/sensory-blocks",
        status="imported",
        image_hue=55,
    ),
    MockProduct(
        id="pf-07",
        title="LED Acne Spot Patch Wand",
        niche="Care",
        country="United States",
        cost=Decimal("16.75"),
        source_url="https://example.com/products/acne-spot-wand",
        status="default",
        image_hue=280,
    ),
    MockProduct(
        id="pf-08",
        title="MagSafe Cable Organizer Clip",
        niche="Tech",
        country="United Kingdom",
        cost=Decimal("6.30"),
        source_url="https://example.com/products/magsafe-cable-clip",
        status="default",
        image_hue=190,
    ),
    MockProduct(
        id="pf-09",
        title="Collapsible Market Tote Bundle",
        niche="Mart",
        country="United States",
        cost=Decimal("8.45"),
        source_url="https://example.com/products/market-tote-bundle",
        status="default",
        image_hue=110,
    ),
    MockProduct(
        id="pf-10",
        title="Ceramic Diffuser Stone Set",
        niche="Living",
        country="Australia",
        cost=Decimal("11.20"),
        source_url="https://example.com/products/diffuser-stone-set",
        status="default",
        image_hue=170,
    ),
]


# 4 imports — one push-failed (edit fields only after clicking Edit)
IMPORTS: list[MockImport] = [
    MockImport(
        id="imp-01",
        title="Compact Resistance Band Kit Pro",
        niche="Peak",
        country="United Kingdom",
        cost=Decimal("9.80"),
        sell=Decimal("29.40"),
        compare_at=Decimal("39.00"),
        image_hue=200,
    ),
    MockImport(
        id="imp-02",
        title="Stackable Sensory Blocks Set",
        niche="Junior",
        country="Australia",
        cost=Decimal("14.10"),
        sell=Decimal("42.30"),
        image_hue=55,
    ),
    MockImport(
        id="imp-03",
        title="LED Acne Spot Patch Wand",
        niche="Care",
        country="United States",
        cost=Decimal("16.75"),
        sell=Decimal("50.25"),
        push_failed=True,
        image_hue=280,
    ),
    MockImport(
        id="imp-04",
        title="MagSafe Cable Organizer Clip",
        niche="Tech",
        country="United Kingdom",
        cost=Decimal("6.30"),
        sell=Decimal("18.90"),
        compare_at=Decimal("24.00"),
        image_hue=190,
    ),
]


TOAST_VARIANTS = [
    {
        "key": "success_single",
        "label": "Success single",
        "tone": "success",
        "message": "Pushed — now live in your store.",
    },
    {
        "key": "success_bulk",
        "label": "Success bulk",
        "tone": "success",
        "message": "3 products pushed — now live in your store.",
    },
    {
        "key": "partial",
        "label": "Partial",
        "tone": "warn",
        "message": "2 of 3 products pushed. 1 failed — try again below.",
    },
    {
        "key": "all_failed",
        "label": "All failed",
        "tone": "error",
        "message": "We couldn't push your products. Try again, or contact support if this continues.",
    },
]
