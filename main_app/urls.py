from django.urls import path

from .views import (
    index,
    reload_data,
    BossDetailView
)

urlpatterns = [
    path("", index, name="index"),
    path("reload-data/", reload_data, name="reload_data"),
    path("bosses/<int:pk>/", BossDetailView.as_view(), name="boss-detail"),
]

app_name = "main_app"
