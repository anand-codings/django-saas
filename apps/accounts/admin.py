"""Admin configuration for the accounts app."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User, UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = "profile"
    fk_name = "user"
    fields = (
        "display_name",
        "bio",
        "avatar_url",
        "timezone",
        "locale",
        "onboarding_completed",
    )


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "email",
        "username",
        "first_name",
        "last_name",
        "is_email_verified",
        "is_staff",
        "is_active",
        "date_joined",
    )
    list_filter = ("is_staff", "is_active", "is_email_verified")
    search_fields = ("email", "username", "first_name", "last_name", "phone_number")
    ordering = ("-date_joined",)
    inlines = (UserProfileInline,)

    # Extend the default fieldsets with our custom fields.
    fieldsets = BaseUserAdmin.fieldsets + (
        (
            "Additional info",
            {
                "fields": (
                    "is_email_verified",
                    "last_login_ip",
                    "phone_number",
                    "date_of_birth",
                ),
            },
        ),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (
            "Additional info",
            {
                "fields": (
                    "phone_number",
                    "date_of_birth",
                ),
            },
        ),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "display_name", "timezone", "onboarding_completed", "created_at")
    search_fields = ("user__email", "display_name")
    list_filter = ("onboarding_completed", "timezone")
    raw_id_fields = ("user",)
    readonly_fields = ("id", "created_at", "updated_at")
