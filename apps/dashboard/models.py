"""
Dashboard models — shop link, plan, and activity feed.

ShopConnection lifecycle:
  pending  — user entered a *.myshopify.com domain (Section A); no valid token yet.
             Must NOT count as "connected" anywhere in the app.
  active   — OAuth completed and install confirmed (app_installed=True).
             This is View B / Case A on Overview.
"""

from django.conf import settings
from django.db import models


class ShopConnection(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="shop_connections",
    )
    shop = models.CharField(max_length=255, unique=True)
    app_installed = models.BooleanField(default=False)
    installed_at = models.DateTimeField(auto_now_add=True)
    app_installed_at = models.DateTimeField(null=True, blank=True)
    # Cached live Shopify product count (from Node install-status)
    store_product_count = models.PositiveIntegerField(null=True, blank=True)
    store_product_count_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-installed_at"]

    def __str__(self) -> str:
        state = "active" if self.app_installed else "pending"
        return f"{self.user_id} → {self.shop} ({state})"

    @property
    def storefront_url(self) -> str:
        return f"https://{self.shop}"

    @property
    def is_preview(self) -> bool:
        """Staff-only demo shop — not a real Shopify storefront."""
        return self.shop.startswith("admin-preview-")

    @property
    def is_connected(self) -> bool:
        """True only when OAuth/install confirmed a valid session/token."""
        return bool(self.app_installed) and not self.is_preview

    @classmethod
    def active_for_user(cls, user) -> "ShopConnection | None":
        return (
            cls.objects.filter(user=user, app_installed=True)
            .exclude(shop__startswith="admin-preview-")
            .first()
        )

    @classmethod
    def pending_for_user(cls, user) -> "ShopConnection | None":
        return (
            cls.objects.filter(user=user, app_installed=False)
            .order_by("-installed_at")
            .first()
        )

    @classmethod
    def user_is_connected(cls, user) -> bool:
        return cls.active_for_user(user) is not None

    @classmethod
    def for_builder(cls, user) -> "ShopConnection | None":
        """
        Active shop for AI Store Builder.
        Customers must have a real connected store.
        Staff/superusers get a local preview shop so they can test the flow.
        """
        active = cls.active_for_user(user)
        if active:
            return active
        if getattr(user, "is_staff", False) or getattr(user, "is_superuser", False):
            return cls.ensure_staff_preview(user)
        return None

    @classmethod
    def ensure_staff_preview(cls, user) -> "ShopConnection":
        """Demo connection for Django admin/staff — not a real Shopify OAuth link."""
        from django.utils import timezone

        shop = f"admin-preview-{user.pk}.myshopify.com"
        connection, created = cls.objects.get_or_create(
            shop=shop,
            defaults={
                "user": user,
                "app_installed": True,
                "app_installed_at": timezone.now(),
            },
        )
        if connection.user_id != user.pk:
            # Shop uniqueness collision — attach a unique slug
            shop = f"admin-preview-{user.pk}-{timezone.now().timestamp():.0f}.myshopify.com"
            connection = cls.objects.create(
                user=user,
                shop=shop,
                app_installed=True,
                app_installed_at=timezone.now(),
            )
        elif not connection.app_installed:
            connection.app_installed = True
            connection.app_installed_at = timezone.now()
            connection.save(update_fields=["app_installed", "app_installed_at"])
        return connection


class UserPlan(models.Model):
    class Plan(models.TextChoices):
        FREE = "free", "Free"
        PRO = "pro", "Pro"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="plan_profile",
    )
    plan = models.CharField(
        max_length=16,
        choices=Plan.choices,
        default=Plan.FREE,
    )
    renews_on = models.DateField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.user_id} · {self.plan}"

    @property
    def is_pro(self) -> bool:
        return self.plan == self.Plan.PRO

    @property
    def label(self) -> str:
        return self.get_plan_display()


class NotificationPreferences(models.Model):
    """Per-user email notification toggles (Settings → Notifications)."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notification_prefs",
    )
    email_build_success = models.BooleanField(default=True)
    email_build_failed = models.BooleanField(default=True)
    email_winning_products = models.BooleanField(default=True)
    email_tips = models.BooleanField(default=False)
    # Preferred niche slug for AI Store Builder pre-select
    default_niche_slug = models.SlugField(max_length=64, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    NOTIFICATION_FIELDS = (
        "email_build_success",
        "email_build_failed",
        "email_winning_products",
        "email_tips",
    )

    def __str__(self) -> str:
        return f"notifications · user {self.user_id}"

    @classmethod
    def for_user(cls, user) -> "NotificationPreferences":
        prefs, _ = cls.objects.get_or_create(user=user)
        return prefs


class MerchantProfile(models.Model):
    """Customer profile under Settings → Account."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="merchant_profile",
    )
    company = models.CharField(max_length=255, blank=True)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=64, blank=True)
    vertical_industry = models.CharField(max_length=255, blank=True)
    desired_niche = models.CharField(max_length=255, blank=True)
    bio = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"profile · user {self.user_id}"

    @classmethod
    def for_user(cls, user) -> "MerchantProfile":
        profile, _ = cls.objects.get_or_create(user=user)
        return profile

    @property
    def display_name(self) -> str:
        full = (self.user.get_full_name() or "").strip()
        if full:
            return full
        if self.user.first_name:
            return self.user.first_name
        return "—"


class ActivityEvent(models.Model):
    class EventType(models.TextChoices):
        STORE = "store", "Store"
        PRODUCT = "product", "Product"
        IMPORT = "import", "Import"
        BILLING = "billing", "Billing"
        SYSTEM = "system", "System"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="activity_events",
    )
    event_type = models.CharField(
        max_length=32,
        choices=EventType.choices,
        default=EventType.SYSTEM,
    )
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.user_id}: {self.message[:40]}"
