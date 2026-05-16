from django.urls import path

from app.interfaces.api.views.home_views import (
    HomeCreateView,
    UserHomesView,
)
from app.interfaces.api.views.home_member_view import (
    AddHomeMemberView,
)

urlpatterns = [
    path("homes/", HomeCreateView.as_view()),
    path("my-homes/", UserHomesView.as_view()),
    path(
        "<uuid:home_id>/members/add/",
        AddHomeMemberView.as_view(),
        name="add-home-member",
    ),
]