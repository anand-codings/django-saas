"""Admin configuration for the organizations app."""

from django.contrib import admin

from .models import Membership, Organization, OrganizationInvite


class MembershipInline(admin.TabularInline):
    model = Membership
    extra = 0
    readonly_fields = ("created_at", "joined_at")
    raw_id_fields = ("user", "invited_by")


class InviteInline(admin.TabularInline):
    model = OrganizationInvite
    extra = 0
    readonly_fields = ("token", "created_at")
    raw_id_fields = ("invited_by",)


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "owner", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("name", "slug", "owner__email")
    prepopulated_fields = {"slug": ("name",)}
    raw_id_fields = ("owner",)
    inlines = [MembershipInline, InviteInline]
    readonly_fields = ("id", "created_at", "updated_at")


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ("user", "organization", "role", "is_active", "joined_at")
    list_filter = ("role", "is_active")
    search_fields = ("user__email", "organization__name")
    raw_id_fields = ("user", "organization", "invited_by")
    readonly_fields = ("id", "created_at", "updated_at")


@admin.register(OrganizationInvite)
class OrganizationInviteAdmin(admin.ModelAdmin):
    list_display = ("email", "organization", "role", "status", "expires_at", "created_at")
    list_filter = ("status", "role")
    search_fields = ("email", "organization__name")
    raw_id_fields = ("organization", "invited_by")
    readonly_fields = ("id", "token", "created_at", "updated_at")
