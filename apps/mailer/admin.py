from django.contrib import admin

from apps.mailer.models import EmailLog, EmailTemplate


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "category", "version", "is_active", "updated_at")
    list_filter = ("is_active", "category")
    search_fields = ("name", "slug", "subject")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ("to_email", "subject", "provider", "status", "created_at")
    list_filter = ("status", "provider")
    search_fields = ("to_email", "subject", "message_id")
    raw_id_fields = ("user", "template")
    readonly_fields = ("message_id", "status", "error", "opened_at", "clicked_at")
