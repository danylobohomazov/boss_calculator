from django.urls import path

from .views import (
    index,
    BossDetailView
)

urlpatterns = [
    path("", index, name="index"),
    path("bosses/<int:pk>/", BossDetailView.as_view(), name="boss-detail"),
]

app_name = "main_app"
