"""
Catalog products (Django mirror of Meta Ads Google Sheet) + scrape runs.

Sheet remains Node's live catalog source for now.
Django DB is the webapp mirror — future cutover: shared DB for both.
"""

from __future__ import annotations

from django.conf import settings
from django.db import models


class CatalogProduct(models.Model):
    """One scraped / sheet product row."""

    source_id = models.CharField(
        max_length=64,
        unique=True,
        help_text="Stable id (hash of product URL). Prefer this over sheet-N.",
    )
    product_key = models.CharField(
        max_length=512,
        unique=True,
        db_index=True,
        help_text="Normalized domain::handle for dedup",
    )
    ad_id = models.CharField(max_length=128, blank=True, default="")
    page_name = models.CharField(max_length=255, blank=True, default="")
    landing_url = models.URLField(max_length=1000, blank=True, default="")
    product_url = models.URLField(max_length=1000)
    title = models.CharField(max_length=500)
    price = models.CharField(max_length=64, blank=True, default="")
    compare_price = models.CharField(max_length=64, blank=True, default="")
    ratings = models.CharField(max_length=32, blank=True, default="")
    review_count = models.CharField(max_length=32, blank=True, default="")
    product_images = models.TextField(blank=True, default="")
    feature_image = models.URLField(max_length=1000, blank=True, default="")
    category = models.CharField(max_length=128, blank=True, default="", db_index=True)
    country = models.CharField(max_length=64, blank=True, default="", db_index=True)
    description = models.TextField(blank=True, default="")
    archived = models.BooleanField(default=False)
    sheet_row = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Last known 1-based sheet data row (fragile; for sync only)",
    )
    last_synced_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        verbose_name = "Winning Product Vault"
        verbose_name_plural = "Winning Product Vault"

    def __str__(self) -> str:
        return f"{self.title[:60]} ({self.source_id})"


class ShopImport(models.Model):
    """
    My Imports draft queue — owned by Django.
    Node is only used on Push + live store status sync.
    """

    class Status(models.TextChoices):
        IMPORTED = "imported", "Imported"
        IN_STORE = "in_store", "In store"
        REMOVED = "removed_from_store", "Removed from store"

    shop = models.CharField(max_length=255, db_index=True)
    source_id = models.CharField(max_length=64, db_index=True)
    title = models.CharField(max_length=500)
    cost = models.CharField(max_length=64, blank=True, default="10")
    sell_price = models.CharField(max_length=64, blank=True, default="")
    compare_at_price = models.CharField(max_length=64, blank=True, default="")
    description = models.TextField(blank=True, default="")
    category = models.CharField(max_length=128, blank=True, default="")
    country = models.CharField(max_length=64, blank=True, default="")
    image_url = models.URLField(max_length=1000, blank=True, default="")
    product_url = models.URLField(max_length=1000, blank=True, default="")
    status = models.CharField(
        max_length=32,
        choices=Status.choices,
        default=Status.IMPORTED,
        db_index=True,
    )
    shopify_product_id = models.CharField(max_length=128, blank=True, default="")
    # Prisma PendingProduct.id after first Node sync/push (optional)
    node_import_id = models.CharField(max_length=64, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        verbose_name = "My Import"
        verbose_name_plural = "My Imports"
        constraints = [
            models.UniqueConstraint(
                fields=["shop", "source_id"],
                name="uniq_shop_import_source",
            )
        ]

    def __str__(self) -> str:
        return f"{self.title[:50]} ({self.shop})"


class ScrapeRun(models.Model):

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        RUNNING = "running", "Running"
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"
        CANCELLED = "cancelled", "Cancelled"

    class Mode(models.TextChoices):
        SINGLE = "single", "Single query"
        ALL_NICHES = "all_niches", "All niches"
        SYNC_SHEET = "sync_sheet", "Sync from sheet"
        CLEAN_DUPES = "clean_dupes", "Clean sheet duplicates"
        FILL_IDS = "fill_ids", "Fill stable ids on sheet"
        PURGE_DEAD = "purge_dead", "Purge dead (404) products"
        CLEAN_PRICES = "clean_prices", "Clean sheet prices to USD"

    status = models.CharField(
        max_length=16, choices=Status.choices, default=Status.PENDING, db_index=True
    )
    mode = models.CharField(max_length=16, choices=Mode.choices, default=Mode.SINGLE)
    query = models.CharField(max_length=255, blank=True, default="fashion")
    country = models.CharField(max_length=8, blank=True, default="US")
    target_rows = models.PositiveIntegerField(default=50)
    products_per_store = models.PositiveIntegerField(default=10)
    sheet_tab = models.CharField(max_length=128, blank=True, default="")
    rows_written = models.PositiveIntegerField(default=0)
    log = models.TextField(blank=True, default="")
    error = models.TextField(blank=True, default="")
    started_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="scrape_runs",
    )
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Product Hunter"
        verbose_name_plural = "Product Hunter"

    def __str__(self) -> str:
        return f"{self.get_mode_display()} · {self.status} · {self.created_at:%Y-%m-%d %H:%M}"

    def append_log(self, line: str) -> None:
        self.log = (self.log + line.rstrip() + "\n")[-50000:]
        self.save(update_fields=["log"])
