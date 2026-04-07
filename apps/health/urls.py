from django.urls import path

from . import views

app_name = "health"

urlpatterns = [
    path("liveness/", views.liveness, name="liveness"),
]
