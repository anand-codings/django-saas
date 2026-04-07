from django.urls import path

from apps.checkout.views import CheckoutSessionCreateView

app_name = "checkout"

urlpatterns = [
    path("create-session/", CheckoutSessionCreateView.as_view(), name="create-session"),
]
