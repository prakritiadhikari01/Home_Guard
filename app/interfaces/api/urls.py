from django.urls import path
from app.interfaces.api.views.active_device_view import ActiveDeviceListView
from app.interfaces.api.views.event_views import EventIngestView, EventEnrichView

from app.interfaces.api.views.face_list_view import FaceListView
from app.interfaces.api.views.home_invitation_view import AcceptInvitationView, PendingInvitationsView, RejectInvitationView
from app.interfaces.api.views.home_views import (
    HomeCreateView,
    UserHomesView,
)

from app.interfaces.api.views.home_member_view import (
    AddHomeMemberView,
    ListHomeMembersView,
    MyHomeMembershipView,
    RemoveHomeMemberView,
    UpdateMemberRoleView,
)
from app.interfaces.api.views.enrollment_views import (
    EnrollmentStatusView,
    CompleteEnrollmentView,
    FailEnrollmentView,
    StartEnrollmentView,
)
from app.interfaces.api.views.device_views import (
    DeviceSettingsView,
    RegisterDeviceView,
    HomeDevicesView,
)

from app.interfaces.api.views.smart_lock_views import (
    LockDoorView,
    SmartLockDetailView,
    UnlockDoorView,
)
from app.interfaces.api.views.face_save_view import FaceSaveView
from app.interfaces.api.views.settings_views import SettingsView
from app.interfaces.api.views.dashboard_views import DashboardView

from app.interfaces.api.views.face_list_view import FaceListView, HomeFacesView

from app.interfaces.api.views.device_views import (
    RegisterDeviceView,
    HomeDevicesView,
    DeviceDetailView,
    DeviceHealthView,
    DeviceEventsView,
    DeviceRestartView,
)

urlpatterns = [
    #setting
    path(
        "settings/",
        SettingsView.as_view(),
        name="settings",
    ),

    #Invitations
    path(
    "home-invitations/",
    PendingInvitationsView.as_view(),
    ),

    path(
        "home-invitations/<uuid:invitation_id>/accept/",
        AcceptInvitationView.as_view(),
    ),

    path(
        "home-invitations/<uuid:invitation_id>/reject/",
        RejectInvitationView.as_view(),
    ),




    #Homes
    path("homes/", HomeCreateView.as_view()),
    path("my-homes/", UserHomesView.as_view()),

    path(
        "<uuid:home_id>/members/",
        ListHomeMembersView.as_view(),
    ),
    path(
        "<uuid:home_id>/members/add/",
        AddHomeMemberView.as_view(),
    ),
    path(
        "<uuid:home_id>/members/<int:user_id>/remove/",
        RemoveHomeMemberView.as_view(),
    ),
    path(
        "<uuid:home_id>/members/<int:user_id>/role/",
        UpdateMemberRoleView.as_view(),
    ),

    path(
        "homes/<uuid:home_id>/locks/<uuid:lock_id>/unlock/",
        UnlockDoorView.as_view(),
    ),
    #enrollments

    path(
        "enrollment/status/<uuid:session_id>/",
        EnrollmentStatusView.as_view(),
        name="enrollment-status",
    ),

    path(
        "enrollment/complete/",
        CompleteEnrollmentView.as_view(),
        name="complete-enrollment",
    ),

    path(
        "enrollment/fail/<uuid:session_id>/",
        FailEnrollmentView.as_view(),
        name="fail-enrollment",
    ),

    path("faces/save/", FaceSaveView.as_view()),
    path("faces/all/", FaceListView.as_view()),
    path("devices/active/",ActiveDeviceListView.as_view(),),


    path("events/ingest/", EventIngestView.as_view()),
    path("events/<uuid:event_id>/enrich/", EventEnrichView.as_view()),
        path(
        "enrollment/start/",
        StartEnrollmentView.as_view(),
        name="start-enrollment",
    ),
    path(
        "dashboard/<uuid:home_id>/",
        DashboardView.as_view(),
        name="dashboard",
    ),
    
    path("homes/<uuid:home_id>/members/me/", MyHomeMembershipView.as_view()),
    #devices
    path("homes/<uuid:home_id>/devices/",HomeDevicesView.as_view()),
    path("homes/<uuid:home_id>/devices/register/",RegisterDeviceView.as_view()),
    path("homes/<uuid:home_id>/devices/<uuid:device_id>/", DeviceDetailView.as_view()),
    path("homes/<uuid:home_id>/devices/<uuid:device_id>/settings/", DeviceSettingsView.as_view()),
    path("homes/<uuid:home_id>/devices/<uuid:device_id>/health/", DeviceHealthView.as_view()),
    path("homes/<uuid:home_id>/devices/<uuid:device_id>/events/", DeviceEventsView.as_view()),
    path("homes/<uuid:home_id>/devices/<uuid:device_id>/restart/", DeviceRestartView.as_view()),
    path("homes/<uuid:home_id>/locks/<uuid:lock_id>/lock/", LockDoorView.as_view()),
    path("homes/<uuid:home_id>/locks/<uuid:lock_id>/", SmartLockDetailView.as_view()),
    path("homes/<uuid:home_id>/faces/", HomeFacesView.as_view()),


]