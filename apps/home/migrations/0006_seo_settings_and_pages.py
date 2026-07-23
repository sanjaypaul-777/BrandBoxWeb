"""
apps/home/migrations/0006_seo_settings_and_pages.py — Django migration: 0006_seo_settings_and_pages.
"""

# Generated manually for SiteSeoSettings + SeoPage

from decimal import Decimal

from django.db import migrations, models


def seed_seo(apps, schema_editor):
    SiteSeoSettings = apps.get_model("home", "SiteSeoSettings")
    SeoPage = apps.get_model("home", "SeoPage")

    SiteSeoSettings.objects.update_or_create(
        pk=1,
        defaults={
            "site_name": "BrandBox",
            "default_title_suffix": "BrandBox",
            "default_meta_description": (
                "Build a Shopify store by niche with AI Store Builder, "
                "import scored products from the Product Vault, "
                "and get coach chat when you need help."
            ),
            "default_og_image_url": "",
            "twitter_handle": "",
            "organization_name": "BrandBox",
            "organization_logo_url": "",
            "google_site_verification": "",
            "bing_site_verification": "",
            "robots_extra": "",
        },
    )

    pages = [
        {
            "key": "home",
            "meta_title": "BrandBox AI | The AI Store That Knows What Sells",
            "meta_description": (
                "Build a Shopify store by niche with AI Store Builder, "
                "import scored products from the Product Vault, "
                "and get coach chat when you need help."
            ),
            "meta_keywords": "BrandBox, AI Shopify store, product vault, AI store builder",
            "sitemap_priority": Decimal("1.0"),
            "sitemap_changefreq": "weekly",
        },
        {
            "key": "contact",
            "meta_title": "Contact BrandBox | Support & Sales",
            "meta_description": (
                "Contact BrandBox for billing help, store guidance, or getting started "
                "with AI Store Builder and the Product Vault."
            ),
            "meta_keywords": "BrandBox contact, BrandBox support",
            "sitemap_priority": Decimal("0.6"),
            "sitemap_changefreq": "monthly",
        },
        {
            "key": "about",
            "meta_title": "About Us · BrandBox",
            "meta_description": (
                "Learn about BrandBox — AI Store Builder, Product Vault, and coach support "
                "to help merchants launch Shopify stores that sell."
            ),
            "meta_keywords": "about BrandBox",
            "sitemap_priority": Decimal("0.5"),
            "sitemap_changefreq": "monthly",
        },
        {
            "key": "privacy",
            "meta_title": "Privacy Policy · BrandBox",
            "meta_description": (
                "Read how BrandBox collects, uses, and protects your information "
                "when you use our marketing site and product."
            ),
            "meta_keywords": "BrandBox privacy policy",
            "sitemap_priority": Decimal("0.3"),
            "sitemap_changefreq": "yearly",
        },
        {
            "key": "terms",
            "meta_title": "Terms of Service · BrandBox",
            "meta_description": (
                "BrandBox terms of service covering use of our website, "
                "AI Store Builder, and related products."
            ),
            "meta_keywords": "BrandBox terms of service",
            "sitemap_priority": Decimal("0.3"),
            "sitemap_changefreq": "yearly",
        },
        {
            "key": "refund",
            "meta_title": "Refund Policy · BrandBox",
            "meta_description": (
                "BrandBox refund policy for subscriptions and related purchases."
            ),
            "meta_keywords": "BrandBox refund policy",
            "sitemap_priority": Decimal("0.3"),
            "sitemap_changefreq": "yearly",
        },
    ]

    for row in pages:
        SeoPage.objects.update_or_create(
            key=row["key"],
            defaults={
                "meta_title": row["meta_title"],
                "meta_description": row["meta_description"],
                "meta_keywords": row["meta_keywords"],
                "canonical_url": "",
                "robots": "index, follow",
                "og_title": "",
                "og_description": "",
                "og_image_url": "",
                "include_in_sitemap": True,
                "sitemap_priority": row["sitemap_priority"],
                "sitemap_changefreq": row["sitemap_changefreq"],
            },
        )


def unseed_seo(apps, schema_editor):
    SiteSeoSettings = apps.get_model("home", "SiteSeoSettings")
    SeoPage = apps.get_model("home", "SeoPage")
    SeoPage.objects.all().delete()
    SiteSeoSettings.objects.filter(pk=1).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0005_about_page"),
    ]

    operations = [
        migrations.CreateModel(
            name="SiteSeoSettings",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "site_name",
                    models.CharField(
                        default="BrandBox",
                        help_text="Shown in social previews (og:site_name).",
                        max_length=120,
                    ),
                ),
                (
                    "default_title_suffix",
                    models.CharField(
                        blank=True,
                        default="BrandBox",
                        help_text="Optional suffix for pages without a custom title (e.g. BrandBox).",
                        max_length=80,
                    ),
                ),
                (
                    "default_meta_description",
                    models.CharField(
                        blank=True,
                        help_text="Fallback meta description when a page has none. Aim for ~150–160 characters.",
                        max_length=320,
                    ),
                ),
                (
                    "default_og_image_url",
                    models.URLField(
                        blank=True,
                        help_text="Default share image (1200×630 recommended). Absolute URL.",
                        max_length=500,
                    ),
                ),
                (
                    "twitter_handle",
                    models.CharField(
                        blank=True,
                        help_text="Without @ — e.g. brandbox. Used for twitter:site.",
                        max_length=64,
                    ),
                ),
                (
                    "organization_name",
                    models.CharField(blank=True, default="BrandBox", max_length=120),
                ),
                (
                    "organization_logo_url",
                    models.URLField(
                        blank=True,
                        help_text="Logo URL for Organization JSON-LD. Absolute URL.",
                        max_length=500,
                    ),
                ),
                (
                    "google_site_verification",
                    models.CharField(
                        blank=True,
                        help_text="Google Search Console verification token only (not the full meta tag).",
                        max_length=120,
                    ),
                ),
                (
                    "bing_site_verification",
                    models.CharField(
                        blank=True,
                        help_text="Bing Webmaster verification token only.",
                        max_length=120,
                    ),
                ),
                (
                    "robots_extra",
                    models.TextField(
                        blank=True,
                        help_text="Extra lines appended to robots.txt (one directive per line).",
                    ),
                ),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Site SEO settings",
                "verbose_name_plural": "Site SEO settings",
            },
        ),
        migrations.CreateModel(
            name="SeoPage",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "key",
                    models.CharField(
                        choices=[
                            ("home", "Home"),
                            ("contact", "Contact"),
                            ("about", "About Us"),
                            ("privacy", "Privacy Policy"),
                            ("terms", "Terms of Service"),
                            ("refund", "Refund Policy"),
                        ],
                        help_text="Which public page these tags apply to.",
                        max_length=32,
                        unique=True,
                    ),
                ),
                (
                    "meta_title",
                    models.CharField(
                        help_text="Browser tab + Google title. Keep under ~60 characters.",
                        max_length=70,
                    ),
                ),
                (
                    "meta_description",
                    models.CharField(
                        blank=True,
                        help_text="Search snippet. Aim for ~150–160 characters.",
                        max_length=320,
                    ),
                ),
                (
                    "meta_keywords",
                    models.CharField(
                        blank=True,
                        help_text="Optional comma-separated keywords (low SEO impact; optional).",
                        max_length=255,
                    ),
                ),
                (
                    "canonical_url",
                    models.URLField(
                        blank=True,
                        help_text="Leave blank to auto-build from the page URL. Use only to force a specific canonical.",
                        max_length=500,
                    ),
                ),
                (
                    "robots",
                    models.CharField(
                        choices=[
                            ("index, follow", "Index + follow (default)"),
                            ("noindex, follow", "Noindex + follow"),
                            ("index, nofollow", "Index + nofollow"),
                            ("noindex, nofollow", "Noindex + nofollow"),
                        ],
                        default="index, follow",
                        help_text="Tell search engines whether to index this page.",
                        max_length=32,
                    ),
                ),
                (
                    "og_title",
                    models.CharField(
                        blank=True,
                        help_text="Open Graph / social title. Blank = use meta title.",
                        max_length=70,
                    ),
                ),
                (
                    "og_description",
                    models.CharField(
                        blank=True,
                        help_text="Social share description. Blank = use meta description.",
                        max_length=320,
                    ),
                ),
                (
                    "og_image_url",
                    models.URLField(
                        blank=True,
                        help_text="Social share image for this page. Blank = site default.",
                        max_length=500,
                    ),
                ),
                (
                    "include_in_sitemap",
                    models.BooleanField(
                        default=True,
                        help_text="Include this page in sitemap.xml.",
                    ),
                ),
                (
                    "sitemap_priority",
                    models.DecimalField(
                        decimal_places=1,
                        default=0.5,
                        help_text="0.1 (low) to 1.0 (highest). Home is usually 1.0.",
                        max_digits=2,
                    ),
                ),
                (
                    "sitemap_changefreq",
                    models.CharField(
                        choices=[
                            ("always", "Always"),
                            ("hourly", "Hourly"),
                            ("daily", "Daily"),
                            ("weekly", "Weekly"),
                            ("monthly", "Monthly"),
                            ("yearly", "Yearly"),
                            ("never", "Never"),
                        ],
                        default="weekly",
                        max_length=16,
                    ),
                ),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "verbose_name": "Page SEO",
                "verbose_name_plural": "Page SEO",
                "ordering": ["key"],
            },
        ),
        migrations.RunPython(seed_seo, unseed_seo),
    ]
