from django.urls import path

from apps.assets import views

app_name = "ops"

urlpatterns = [
    path("dashboard/", views.ops_dashboard, name="dashboard"),
    path("fulfillment/", views.ops_fulfillment, name="fulfillment"),
    path("assets/", views.ops_asset_list, name="asset_list"),
    path("assets/new/", views.ops_asset_create, name="asset_create"),
    path("assets/<int:pk>/", views.ops_asset_detail, name="asset_detail"),
    path("assets/<int:pk>/assign/", views.ops_asset_assign, name="asset_assign"),
]
