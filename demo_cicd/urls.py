from django.urls import include, path

from notas.views import healthz

urlpatterns = [
    path("healthz/", healthz, name="healthz"),
    path("", include("notas.urls")),
]
