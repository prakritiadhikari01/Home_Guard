from django.urls import path
from app.interfaces.api.views.event_views import DetectionEventAPIView

from app.interfaces.api.views.face_list_view import FaceListView
from app.interfaces.api.views.home_views import (
    HomeCreateView,
    UserHomesView,
)
from app.interfaces.api.views.home_member_view import (
    AddHomeMemberView,
    ListHomeMembersView,
    RemoveHomeMemberView,
    UpdateMemberRoleView,
)
from app.interfaces.api.views.device_views import (
    RegisterDeviceView,
    HomeDevicesView,
)

from app.interfaces.api.views.smart_lock_views import (
    UnlockDoorView,
)

from app.interfaces.api.views.face_profile_views import (
    RegisterFaceView
)
from app.interfaces.api.views.face_save_view import FaceSaveView

urlpatterns = [
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
        "homes/<uuid:home_id>/devices/",
        HomeDevicesView.as_view(),
    ),

    path(
        "homes/<uuid:home_id>/devices/register/",
        RegisterDeviceView.as_view(),
    ),

    path(
        "homes/<uuid:home_id>/locks/<uuid:lock_id>/unlock/",
        UnlockDoorView.as_view(),
    ),
    path(
        "faces/register/",
        RegisterFaceView.as_view()
    ),
    path("faces/save/", FaceSaveView.as_view()),
    path("faces/all/", FaceListView.as_view()),
    path(
        "events/detect/",
        DetectionEventAPIView.as_view(),
        name="events-detect"
    ),
]