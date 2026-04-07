from django.contrib import admin

from apps.notifications.models import Notification, NotificationPreference, NotificationType


@admin.register(NotificationType)
class NotificationTypeAdmin(admin.ModelAdmin):
    list_display = ("slug", "name", "category", "is_active")
    list_filter = ("is_active", "category")
    search_fields = ("name", "slug")


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("recipient", "notification_type", "title", "is_read", "priority", "created_at")
    list_filter = ("is_read", "priority", "notification_type")
    search_fields = ("recipient__email", "title")
    raw_id_fields = ("recipient", "actor", "notification_type")


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ("user", "notification_type", "channels", "is_muted")
    list_filter = ("is_muted",)
    raw_id_fields = ("user", "notification_type")
