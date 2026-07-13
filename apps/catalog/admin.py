"""Django admin — Winning Product Vault + Product Hunter."""

from __future__ import annotations

import threading

from django.contrib import admin, messages
from django.shortcuts import redirect
from django.utils.html import format_html

from apps.catalog.models import CatalogProduct, ScrapeRun, ShopImport
from apps.catalog.scraper.sheets_client import sheet_tab_default
from apps.catalog.services.pipeline import execute_scrape_run


def _start_run_async(run_id: int) -> None:
    thread = threading.Thread(
        target=execute_scrape_run,
        args=(run_id,),
        daemon=True,
        name=f"product-hunter-{run_id}",
    )
    thread.start()


@admin.register(ShopImport)
class ShopImportAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "shop",
        "status",
        "source_id",
        "sell_price",
        "updated_at",
    )
    list_filter = ("status", "shop", "category")
    search_fields = ("title", "source_id", "shop")
    readonly_fields = ("created_at", "updated_at", "node_import_id")


@admin.register(CatalogProduct)
class CatalogProductAdmin(admin.ModelAdmin):
    list_display = (
        "title_short",
        "category",
        "country",
        "price",
        "source_id",
        "updated_at",
    )
    list_filter = ("category", "country", "archived")
    search_fields = ("title", "product_url", "source_id", "page_name")
    readonly_fields = (
        "source_id",
        "product_key",
        "created_at",
        "updated_at",
        "last_synced_at",
    )
    ordering = ("-updated_at",)

    @admin.display(description="Title")
    def title_short(self, obj: CatalogProduct) -> str:
        return (obj.title or "")[:70]


@admin.register(ScrapeRun)
class ScrapeRunAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "mode",
        "status_badge",
        "query",
        "country",
        "target_rows",
        "rows_written",
        "started_by",
        "created_at",
    )
    list_filter = ("status", "mode")
    readonly_fields = (
        "status",
        "rows_written",
        "log",
        "error",
        "started_at",
        "finished_at",
        "created_at",
        "started_by",
    )
    fields = (
        "mode",
        "query",
        "country",
        "target_rows",
        "products_per_store",
        "sheet_tab",
        "status",
        "rows_written",
        "started_by",
        "started_at",
        "finished_at",
        "log",
        "error",
        "created_at",
    )
    change_list_template = "admin/catalog/scraperun/change_list.html"
    add_form_template = "admin/catalog/scraperun/change_form.html"
    change_form_template = "admin/catalog/scraperun/change_form.html"

    @admin.display(description="Status")
    def status_badge(self, obj: ScrapeRun) -> str:
        colors = {
            "pending": "#888",
            "running": "#c98a00",
            "success": "#10b981",
            "failed": "#dc2626",
            "cancelled": "#666",
        }
        color = colors.get(obj.status, "#888")
        return format_html(
            '<span style="color:{};font-weight:600">{}</span>',
            color,
            obj.get_status_display(),
        )

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context["title"] = "Product Hunter"
        return super().changelist_view(request, extra_context=extra_context)

    def add_view(self, request, form_url="", extra_context=None):
        extra_context = extra_context or {}
        extra_context["title"] = "Start Hunting"
        extra_context["subtitle"] = "Product Hunter"
        return super().add_view(request, form_url, extra_context=extra_context)

    def save_model(self, request, obj, form, change):
        is_new = obj.pk is None
        if not obj.sheet_tab:
            obj.sheet_tab = sheet_tab_default()
        if is_new and not obj.started_by_id:
            obj.started_by = request.user
        super().save_model(request, obj, form, change)
        if is_new and obj.status == ScrapeRun.Status.PENDING:
            _start_run_async(obj.pk)
            messages.info(
                request,
                "Hunt started in the background. Refresh this page to watch the log. "
                "New rows go to Google Sheet (Node) and Winning Product Vault.",
            )

    def response_add(self, request, obj, post_url_continue=None):
        return redirect("admin:catalog_scraperun_change", obj.pk)

    actions = ["rerun_selected"]

    @admin.action(description="Start hunting again (new job)")
    def rerun_selected(self, request, queryset):
        for run in queryset:
            if run.status == ScrapeRun.Status.RUNNING:
                continue
            clone = ScrapeRun.objects.create(
                mode=run.mode,
                query=run.query,
                country=run.country,
                target_rows=run.target_rows,
                products_per_store=run.products_per_store,
                sheet_tab=run.sheet_tab or sheet_tab_default(),
                started_by=request.user,
            )
            _start_run_async(clone.pk)
        messages.success(request, "Started hunting.")
