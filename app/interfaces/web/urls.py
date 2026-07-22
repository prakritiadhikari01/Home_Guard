from django.urls import path

from . import views

app_name = "web"

urlpatterns = [
    path("", views.login_page, name="login"),
    path("register/", views.register_page, name="register"),

    path("dashboard/", views.dashboard_page, name="dashboard"),
    path("live/", views.live_page, name="live"),
    path("timeline/", views.timeline_page, name="timeline"),
    path("alerts/", views.alerts_page, name="alerts"),
    path("members/", views.members_page, name="members"),
    path("members/<uuid:member_id>/", views.member_detail_page, name="members_detail"),
    path("devices/", views.devices_page, name="devices"),
    path("devices/<uuid:device_id>/",views.devices_detail_page,name="devices-detail"),
    path("cameras/", views.cameras_page, name="cameras"),
    path("assistant/", views.assistant_page, name="assistant"),
    path("settings/", views.settings_page, name="settings"),
    path("home-setup/",views.home_setup_page,name="home_setup"),
    path("scan-face/",views.scan_page,name="scan-page",)
    
]