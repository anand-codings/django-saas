from django.contrib import admin

from apps.plans.models import Plan, PlanFeature, PlanFeatureDefinition


class PlanFeatureInline(admin.TabularInline):
    model = PlanFeature
    extra = 1


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "price_monthly", "price_yearly", "status", "is_public", "sort_order")
    list_filter = ("status", "is_public", "currency")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [PlanFeatureInline]


@admin.register(PlanFeatureDefinition)
class PlanFeatureDefinitionAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "category")
    search_fields = ("name", "slug")
    list_filter = ("category",)
    prepopulated_fields = {"slug": ("name",)}
