# SEO: feature-aware meta for home, affiliate, help + keywords

from django.db import migrations

FEATURE_BLURB = (
    "AI Store Builder, Product Hunter, BrandBox Coach, and Training"
)

HOME_TITLE = "BrandBox AI | AI Store Builder, Product Hunter & Coach"
HOME_DESC = (
    "BrandBox helps you launch niche Shopify stores with AI Store Builder, "
    "find winners in Product Hunter, get BrandBox Coach support, and learn "
    "with Training — import, push, and grow in one dashboard."
)
HOME_KEYWORDS = (
    "BrandBox, AI Store Builder, Product Hunter, BrandBox Coach, Training, "
    "Shopify store builder, product vault, ecommerce coach, AI Shopify tools"
)

AFF_TITLE = "BrandBox Affiliate Program | Promote AI Store Builder Tools"
AFF_DESC = (
    "Earn commission promoting BrandBox — AI Store Builder, Product Hunter, "
    "BrandBox Coach, and Training for Shopify entrepreneurs. Join the affiliate "
    "program and get paid on referred sales."
)

HELP_TITLE = "BrandBox Help Center | AI Store Builder & Product Hunter Guides"
HELP_DESC = (
    "Learn BrandBox features in the Help Center: AI Store Builder, Product "
    "Hunter, BrandBox Coach, Training, Shopify connect, imports, billing, and "
    "store growth guides."
)

ABOUT_DESC = (
    "BrandBox is built for Shopify founders — AI Store Builder, Product Hunter, "
    "BrandBox Coach, and Training to launch niche stores, import scored "
    "products, and grow with guidance."
)

CONTACT_DESC = (
    "Contact BrandBox about AI Store Builder, Product Hunter, BrandBox Coach, "
    "Training, billing, or getting your Shopify store live."
)


def refresh(apps, schema_editor):
    SiteSeoSettings = apps.get_model("home", "SiteSeoSettings")
    SeoPage = apps.get_model("home", "SeoPage")

    SiteSeoSettings.objects.filter(pk=1).update(
        default_meta_description=HOME_DESC,
        site_name="BrandBox",
        organization_name="BrandBox",
    )

    updates = {
        "home": {
            "meta_title": HOME_TITLE,
            "meta_description": HOME_DESC,
            "meta_keywords": HOME_KEYWORDS,
            "og_title": HOME_TITLE,
            "og_description": HOME_DESC,
        },
        "affiliate": {
            "meta_title": AFF_TITLE,
            "meta_description": AFF_DESC,
            "meta_keywords": (
                "BrandBox affiliate, AI Store Builder affiliate, Product Hunter "
                "affiliate, Shopify affiliate program, BrandBox Coach affiliate"
            ),
            "og_title": AFF_TITLE,
            "og_description": AFF_DESC,
        },
        "affiliate_apply": {
            "meta_title": "Apply · BrandBox Affiliate | AI Store Builder Partners",
            "meta_description": (
                "Apply to promote BrandBox features — AI Store Builder, Product "
                "Hunter, BrandBox Coach, and Training — and earn commission on "
                "every referred sale."
            ),
            "meta_keywords": (
                "BrandBox affiliate apply, AI Store Builder partner, Shopify affiliate"
            ),
        },
        "help": {
            "meta_title": HELP_TITLE,
            "meta_description": HELP_DESC,
            "meta_keywords": (
                "BrandBox help, AI Store Builder guide, Product Hunter help, "
                "BrandBox Coach FAQ, Training help, Shopify setup"
            ),
            "og_title": HELP_TITLE,
            "og_description": HELP_DESC,
        },
        "about": {
            "meta_description": ABOUT_DESC,
            "meta_keywords": (
                "about BrandBox, AI Store Builder, Product Hunter, BrandBox Coach, Training"
            ),
        },
        "contact": {
            "meta_description": CONTACT_DESC,
            "meta_keywords": (
                "BrandBox contact, AI Store Builder support, Product Hunter help, Coach support"
            ),
        },
    }

    for key, fields in updates.items():
        SeoPage.objects.filter(key=key).update(**fields)


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0013_refresh_public_seo"),
    ]

    operations = [
        migrations.RunPython(refresh, noop),
    ]
