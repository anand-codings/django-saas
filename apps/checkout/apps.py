from django.apps import AppConfig


class CheckoutConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.checkout"
    label = "checkout"
    verbose_name = "Checkout flow, coupon/promo codes, trial management, upgrade/downgrade logic"
