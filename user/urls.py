from django.urls import path, include
from rest_framework import routers

from user.views import (
    CreateUserView,
    CreateTokenView,
    UserListViewSet,
    UserFollowingListView,
    UserFollowersListView,
    UserOwnProfileViewSet,
)

router = routers.DefaultRouter()
router.register("users", UserListViewSet, basename="users")
router.register("me", UserOwnProfileViewSet, basename="me")

urlpatterns = [
    path("register/", CreateUserView.as_view(), name="register"),
    path("token/", CreateTokenView.as_view(), name="token"),
    path(
        "following/<int:pk>/",
        UserFollowingListView.as_view(),
        name="following-list"
    ),
    path("followers/", UserFollowersListView.as_view(), name="follower-lisr"),
    path("", include(router.urls)),
]

app_name = "user"
