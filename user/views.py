from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import generics, mixins, viewsets, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.viewsets import ReadOnlyModelViewSet

from user.models import User, UserFollowing
from user.permissions import IsOwnProfileOrReadOnly
from user.serializers import (
    UserSerializer,
    UserListSerializer,
    UserDetailSerializer,
    UserPhotoUploadSerializer,
    UserFollowingListSerializer,
    UserFollowersListSerializer,
    FollowingUserSerializer,
)


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class UserOwnProfileViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """
    Endpoint for displaying a registered user's own profile.
    Use any 'pk', this endpoint redirects only to own profile.
    """

    queryset = User.objects.all()
    serializer_class = UserDetailSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get_object(self):
        user = self.request.user
        return User.objects.get(id=user.id)

    def retrieve(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    def get_serializer_class(self):
        if self.action == "upload_photo":
            return UserPhotoUploadSerializer

        return UserDetailSerializer

    @action(methods=["POST", "DELETE"], detail=True, url_path="upload-photo")
    def upload_photo(self, request, pk=None):
        """Endpoint for uploading/deleting profile photo"""
        profile = self.request.user

        if request.method == "POST":
            serializer = self.get_serializer(profile, data=request.data)
            serializer.is_valid(raise_exception=True)
            profile.photo = serializer.validated_data.get("photo")
            profile.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        if request.method == "DELETE":
            profile.photo.delete()
            profile.save()
            return Response(
                {"detail": "Photo deleted"}, status=status.HTTP_204_NO_CONTENT
            )


class UserListViewSet(ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated, IsOwnProfileOrReadOnly)
    authentication_classes = (TokenAuthentication,)

    def get_queryset(self):
        queryset = self.queryset

        email = self.request.query_params.get("email")
        first_name = self.request.query_params.get("first_name")
        last_name = self.request.query_params.get("last_name")

        if email:
            queryset = queryset.filter(email__icontains=email)

        if first_name:
            queryset = queryset.filter(first_name__icontains=first_name)

        if last_name:
            queryset = queryset.filter(last_name__icontains=last_name)

        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return UserListSerializer

        if self.action == "retrieve":
            return UserDetailSerializer

        if self.action == "following_change":
            return FollowingUserSerializer

        return UserSerializer

    @action(
        methods=["POST", "DELETE"],
        detail=True,
        url_path="following-change"
    )
    def following_change(self, request, pk=None):
        """Follow or unfollow a user"""
        subscriber = User.objects.get(pk=self.request.user.id)
        user = get_object_or_404(User, id=pk)
        serializer = self.get_serializer(
            data={"user": user, "subscriber": subscriber}
        )
        serializer.is_valid(raise_exception=True)

        if request.method == "POST":
            UserFollowing.objects.create(user=user, subscriber=subscriber)
            return Response({"detail": "Follow"}, status=status.HTTP_200_OK)

        if request.method == "DELETE":
            UserFollowing.objects.filter(
                user=user, subscriber=subscriber
            ).delete()
            return Response(
                {"detail": "Unfollow"},
                status=status.HTTP_204_NO_CONTENT
            )

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="email",
                type=str,
                description="Filter by user email"
            ),
            OpenApiParameter(
                name="first_name",
                type=str,
                description="Filter by user first name"
            ),
            OpenApiParameter(
                name="last_name",
                type=str,
                description="Filter by user last name"
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class UserFollowingListView(generics.ListAPIView):
    """Output a list of the user's following"""

    permission_classes = (IsAuthenticated,)
    serializer_class = UserFollowingListSerializer
    authentication_classes = (TokenAuthentication,)

    def get_queryset(self):
        return UserFollowing.objects.filter(subscriber=self.request.user).all()


class UserFollowersListView(generics.ListAPIView):
    """Output a list of the user's followers"""

    permission_classes = (IsAuthenticated,)
    serializer_class = UserFollowersListSerializer
    authentication_classes = (TokenAuthentication,)

    def get_queryset(self):
        return UserFollowing.objects.filter(user=self.request.user).all()
