from django.urls import path

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
]