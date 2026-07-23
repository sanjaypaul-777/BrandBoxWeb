"""
apps/home/migrations/0013_refresh_public_seo.py — Django migration: 0013_refresh_public_seo.
"""

# Refresh public SEO copy + Help Center page tags

from decimal import Decimal

from django.db import migrations, models


HOME_TITLE = "BrandBox AI | AI Shopify Store Builder & Product Vault"
HOME_DESC = (
    "Build a niche Shopify store with BrandBox AI Store Builder, import "
    "AI-scored products from the Product Vault, and get BrandBox Coach "
    "support when you need help launching and growing."
)
HOME_KEYWORDS = (
    "BrandBox, BrandBox AI, AI Shopify store builder, Shopify store builder, "
    "product vault, winning products, dropshipping tools, ecommerce coach, "
    "AI product research, Shopify product importer"
)

DEFAULT_DESC = HOME_DESC


def refresh_seo(apps, schema_editor):
    SiteSeoSettings = apps.get_model("home", "SiteSeoSettings")
    SeoPage = apps.get_model("home", "SeoPage")

    SiteSeoSettings.objects.update_or_create(
        pk=1,
        defaults={
            "site_name": "BrandBox",
            "default_title_suffix": "BrandBox",
            "default_meta_description": DEFAULT_DESC,
            "organization_name": "BrandBox",
            "default_og_image_url": "/static/images/offer.png",
            "organization_logo_url": "/static/images/favicon.png",
        },
    )

    pages = [
        {
            "key": "home",
            "meta_title": HOME_TITLE,
            "meta_description": HOME_DESC,
            "meta_keywords": HOME_KEYWORDS,
            "og_title": HOME_TITLE,
            "og_description": HOME_DESC,
            "og_image_url": "/static/images/offer.png",
            "sitemap_priority": Decimal("1.0"),
            "sitemap_changefreq": "weekly",
            "include_in_sitemap": True,
            "robots": "index, follow",
        },
        {
            "key": "contact",
            "meta_title": "Contact BrandBox | Support for Shopify Merchants",
            "meta_description": (
                "Contact BrandBox for help with AI Store Builder, Product Vault "
                "imports, billing questions, or getting your Shopify store live "
                "with coach support."
            ),
            "meta_keywords": (
                "BrandBox contact, BrandBox support, Shopify store help, "
                "AI store builder support"
            ),
            "sitemap_priority": Decimal("0.6"),
            "sitemap_changefreq": "monthly",
        },
        {
            "key": "about",
            "meta_title": "About BrandBox | AI Tools for Shopify Entrepreneurs",
            "meta_description": (
                "BrandBox helps ecommerce founders launch niche Shopify stores "
                "with AI Store Builder, an AI-chosen Product Vault, and BrandBox "
                "Coach mentoring when you get stuck."
            ),
            "meta_keywords": (
                "about BrandBox, BrandBox AI company, Shopify AI platform, "
                "ecommerce store builder"
            ),
            "sitemap_priority": Decimal("0.5"),
            "sitemap_changefreq": "monthly",
        },
        {
            "key": "privacy",
            "meta_title": "Privacy Policy · BrandBox",
            "meta_description": (
                "Learn how BrandBox collects, uses, and protects your data when "
                "you use our marketing site, dashboard, Help Center, and Shopify "
                "store tools."
            ),
            "meta_keywords": "BrandBox privacy policy, data protection, GDPR",
            "sitemap_priority": Decimal("0.3"),
            "sitemap_changefreq": "yearly",
        },
        {
            "key": "terms",
            "meta_title": "Terms of Service · BrandBox",
            "meta_description": (
                "Read the BrandBox Terms of Service for using AI Store Builder, "
                "Product Vault, coach chat, affiliate program, and related "
                "Shopify ecommerce services."
            ),
            "meta_keywords": "BrandBox terms of service, user agreement",
            "sitemap_priority": Decimal("0.3"),
            "sitemap_changefreq": "yearly",
        },
        {
            "key": "refund",
            "meta_title": "Refund Policy · BrandBox",
            "meta_description": (
                "Review BrandBox refund eligibility, timelines, and how to "
                "request a refund for Plus Plan and related purchases."
            ),
            "meta_keywords": "BrandBox refund policy, cancellation, money back",
            "sitemap_priority": Decimal("0.3"),
            "sitemap_changefreq": "yearly",
        },
        {
            "key": "disclaimer",
            "meta_title": "Disclaimer · BrandBox",
            "meta_description": (
                "Important BrandBox disclaimer covering AI recommendations, "
                "product data, earnings examples, and Shopify store results."
            ),
            "meta_keywords": "BrandBox disclaimer, earnings disclaimer",
            "sitemap_priority": Decimal("0.2"),
            "sitemap_changefreq": "yearly",
        },
        {
            "key": "affiliate",
            "meta_title": "BrandBox Affiliate Program | Earn on Every Sale",
            "meta_description": (
                "Join the BrandBox affiliate program and earn recurring "
                "commission promoting AI Shopify Store Builder, Product Vault, "
                "and coach tools to ecommerce founders."
            ),
            "meta_keywords": (
                "BrandBox affiliate, Shopify affiliate program, ecommerce "
                "affiliate, AI store builder affiliate"
            ),
            "sitemap_priority": Decimal("0.7"),
            "sitemap_changefreq": "monthly",
        },
        {
            "key": "affiliate_apply",
            "meta_title": "Apply · BrandBox Affiliate Partner",
            "meta_description": (
                "Apply to become a BrandBox affiliate partner. Share AI Shopify "
                "store tools with your audience and earn commission on referred "
                "sales."
            ),
            "meta_keywords": (
                "BrandBox affiliate register, affiliate application, partner signup"
            ),
            "sitemap_priority": Decimal("0.5"),
            "sitemap_changefreq": "monthly",
        },
        {
            "key": "help",
            "meta_title": "BrandBox Help Center | Guides for Store Setup & Growth",
            "meta_description": (
                "Search BrandBox Help for AI Store Builder, Product Vault, "
                "Shopify connect, imports, billing, and BrandBox Coach guides "
                "so you can launch and grow faster."
            ),
            "meta_keywords": (
                "BrandBox help center, Shopify store setup help, AI store "
                "builder guide, product vault help, BrandBox coach FAQ"
            ),
            "sitemap_priority": Decimal("0.8"),
            "sitemap_changefreq": "weekly",
            "include_in_sitemap": True,
            "robots": "index, follow",
        },
    ]

    for row in pages:
        key = row.pop("key")
        defaults = {
            "robots": "index, follow",
            "include_in_sitemap": True,
            "sitemap_changefreq": "monthly",
            "sitemap_priority": Decimal("0.5"),
            "og_title": "",
            "og_description": "",
            "og_image_url": "",
            "canonical_url": "",
        }
        defaults.update(row)
        SeoPage.objects.update_or_create(key=key, defaults=defaults)


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0012_affiliate_current_activity"),
    ]

    operations = [
        migrations.AlterField(
            model_name="seopage",
            name="key",
            field=models.CharField(
                choices=[
                    ("home", "Home"),
                    ("contact", "Contact"),
                    ("about", "About Us"),
                    ("privacy", "Privacy Policy"),
                    ("terms", "Terms of Service"),
                    ("refund", "Refund Policy"),
                    ("disclaimer", "Disclaimer"),
                    ("affiliate", "Affiliate"),
                    ("affiliate_apply", "Affiliate Register"),
                    ("help", "Help Center"),
                ],
                help_text="Which public page these tags apply to.",
                max_length=32,
                unique=True,
            ),
        ),
        migrations.RunPython(refresh_seo, noop_reverse),
    ]
