"""
apps/builder/niches.py — Canonical niche pack seed data for the AI Store Builder.

Metadata only (slug, names, theme, sort). Product catalogs live on Node/R2.
Django stores NichePack rows; product_count syncs from Node GET /api/niches.
Builder cards use static/images/niches/*.jpg thumbs — not accent colors.
"""

from __future__ import annotations

from config.palette import ACCENTS

# Ten niches — Pod has zero products on the engine.
# Accents cycle BrandBox palette (config.palette.ACCENTS).

NICHES = (
    {
        "slug": "living",
        "codename": "Living",
        "name": "Home Decor",
        "theme_name": "BrandBox Living",
        "description": "Warm, editorial spaces built to feel premium.",
        "accent": ACCENTS[0],
        "sort_order": 1,
        "default_product_count": 20,
    },
    {
        "slug": "peak",
        "codename": "Peak",
        "name": "Fitness",
        "theme_name": "BrandBox Peak",
        "description": "Gear and essentials built for movers.",
        "accent": ACCENTS[1],
        "sort_order": 2,
        "default_product_count": 20,
    },
    {
        "slug": "care",
        "codename": "Care",
        "name": "Beauty",
        "theme_name": "BrandBox Care",
        "description": "Clean beauty, skincare, and self-care.",
        "accent": ACCENTS[2],
        "sort_order": 3,
        "default_product_count": 20,
    },
    {
        "slug": "junior",
        "codename": "Junior",
        "name": "Kids & Baby",
        "theme_name": "BrandBox Junior",
        "description": "Soft essentials for little ones.",
        "accent": ACCENTS[3],
        "sort_order": 4,
        "default_product_count": 20,
    },
    {
        "slug": "paws",
        "codename": "Paws",
        "name": "Pet",
        "theme_name": "BrandBox Paws",
        "description": "Products pets (and their people) love.",
        "accent": ACCENTS[0],
        "sort_order": 5,
        "default_product_count": 20,
    },
    {
        "slug": "lux",
        "codename": "Luxe",
        "name": "Jewelry",
        "theme_name": "BrandBox Luxe",
        "description": "Fine pieces with a modern edge.",
        "accent": ACCENTS[1],
        "sort_order": 6,
        "default_product_count": 20,
    },
    {
        "slug": "tech",
        "codename": "Tech",
        "name": "Electronics",
        "theme_name": "BrandBox Tech",
        "description": "Gadgets and everyday tech.",
        "accent": ACCENTS[2],
        "sort_order": 7,
        "default_product_count": 20,
    },
    {
        "slug": "vogue",
        "codename": "Vogue",
        "name": "Fashion",
        "theme_name": "BrandBox Vogue",
        "description": "Apparel and accessories that move.",
        "accent": ACCENTS[3],
        "sort_order": 8,
        "default_product_count": 20,
    },
    {
        "slug": "mart",
        "codename": "Mart",
        "name": "General",
        "theme_name": "BrandBox Mart",
        "description": "A broad mix of winning bestsellers.",
        "accent": ACCENTS[0],
        "sort_order": 9,
        "default_product_count": 100,
    },
    {
        "slug": "pod",
        "codename": "POD",
        "name": "Print on Demand",
        "theme_name": "BrandBox POD",
        "description": "Print-on-demand ready storefront.",
        "accent": ACCENTS[1],
        "sort_order": 10,
        "default_product_count": 0,
    },
)


def ensure_niche_packs():
    """Upsert niche metadata; sync product counts from Node when reachable."""
    from config.brandbox_client import sync_niche_product_counts

    from .models import NichePack

    keep_slugs = set()
    for item in NICHES:
        keep_slugs.add(item["slug"])
        NichePack.objects.update_or_create(
            slug=item["slug"],
            defaults={
                "codename": item["codename"],
                "name": item["name"],
                "theme_name": item["theme_name"],
                "description": item["description"],
                "accent": item["accent"],
                "sort_order": item["sort_order"],
                "is_active": True,
                "product_count": item["default_product_count"],
            },
        )

    NichePack.objects.exclude(slug__in=keep_slugs).update(is_active=False)
    sync_niche_product_counts()
