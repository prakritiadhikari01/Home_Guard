from django.urls import path

from app.interfaces.api.views.home_views import (
    HomeCreateView,
    UserHomesView,
)

urlpatterns = [
    path("homes/", HomeCreateView.as_view()),
    path("my-homes/", UserHomesView.as_view()),
]