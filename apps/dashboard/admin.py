from django.contrib import admin

from .models import (
    ActivityEvent,
    NotificationPreferences,
    ShopConnection,
    UserPlan,
)


@admin.register(ShopConnection)
class ShopConnectionAdmin(admin.ModelAdmin):
    list_display = ("shop", "user", "app_installed", "installed_at", "app_installed_at")
    search_fields = ("shop", "user__username", "user__email")
    list_filter = ("app_installed",)
    readonly_fields = ("installed_at", "app_installed_at")


@admin.register(UserPlan)
class UserPlanAdmin(admin.ModelAdmin):
    list_display = ("user", "plan", "renews_on", "updated_at")
    list_filter = ("plan",)
    search_fields = ("user__username", "user__email")


@admin.register(NotificationPreferences)
class NotificationPreferencesAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "email_build_success",
        "email_build_failed",
        "email_winning_products",
        "email_tips",
        "default_niche_slug",
    )
    search_fields = ("user__username", "user__email")


@admin.register(ActivityEvent)
class ActivityEventAdmin(admin.ModelAdmin):
    list_display = ("message", "event_type", "user", "created_at")
    list_filter = ("event_type", "created_at")
    search_fields = ("message", "user__username", "user__email")
    readonly_fields = ("created_at",)
