from django.contrib import admin

from apps.tenancy.models import Tenant, TenantMembership


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "domain", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("name", "slug", "domain")
    readonly_fields = ("id", "created_at", "updated_at")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("-created_at",)


@admin.register(TenantMembership)
class TenantMembershipAdmin(admin.ModelAdmin):
    list_display = ("user", "tenant", "role", "is_default", "created_at")
    list_filter = ("role", "is_default")
    search_fields = ("user__email", "tenant__name")
    readonly_fields = ("id", "created_at", "updated_at")
    raw_id_fields = ("user", "tenant")
    ordering = ("-created_at",)
