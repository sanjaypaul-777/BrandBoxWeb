"""
apps/home/migrations/0015_site_offer_settings.py — Django migration: 0015_site_offer_settings.
"""

# Generated manually — SiteOfferSettings singleton

from datetime import datetime

from django.db import migrations, models
import django.utils.timezone


def seed_offer_settings(apps, schema_editor):
    SiteOfferSettings = apps.get_model("home", "SiteOfferSettings")
    end = django.utils.timezone.make_aware(datetime(2026, 7, 31, 23, 59, 59))
    SiteOfferSettings.objects.update_or_create(
        pk=1,
        defaults={
            "offer_percent": 65,
            "affiliate_percent": 30,
            "offer_ends_at": end,
        },
    )


def unseed_offer_settings(apps, schema_editor):
    SiteOfferSettings = apps.get_model("home", "SiteOfferSettings")
    SiteOfferSettings.objects.filter(pk=1).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0014_feature_seo_meta"),
    ]

    operations = [
        migrations.CreateModel(
            name="SiteOfferSettings",
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
                    "offer_percent",
                    models.PositiveSmallIntegerField(
                        default=65,
                        help_text='Homepage badge number only (e.g. 65 → “65% Off”).',
                    ),
                ),
                (
                    "offer_ends_at",
                    models.DateTimeField(
                        help_text='Hero countdown end. After this time the timer shows “Offer ended”.',
                    ),
                ),
                (
                    "affiliate_percent",
                    models.PositiveSmallIntegerField(
                        default=30,
                        help_text='Affiliate page number only (e.g. 30 → “30%+”).',
                    ),
                ),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Site offer settings",
                "verbose_name_plural": "Site offer settings",
            },
        ),
        migrations.RunPython(seed_offer_settings, unseed_offer_settings),
    ]
