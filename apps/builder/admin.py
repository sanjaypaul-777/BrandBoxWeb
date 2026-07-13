from django.contrib import admin

from .models import BuildJob, NichePack


@admin.register(NichePack)
class NichePackAdmin(admin.ModelAdmin):
    list_display = ("codename", "name", "slug", "product_count", "sort_order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("codename", "name", "slug")
    prepopulated_fields = {"slug": ("codename",)}


@admin.register(BuildJob)
class BuildJobAdmin(admin.ModelAdmin):
    list_display = ("shop", "user", "niche", "status", "product_count", "created_at")
    list_filter = ("status", "skip_products")
