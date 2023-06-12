from django.db.models import Count, Q
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from blog.models import Post, Comment
from blog.permissions import IsOwnerOrReadOnly
from blog.serializers import (
    PostSerializer,
    CommentSerializer,
    PostListSerializer,
    PostDetailSerializer,
    PostImageSerializer,
)


class PostViewSet(viewsets.ModelViewSet):
    queryset = (
        Post.objects.select_related("author")
        .prefetch_related("comments")
        .annotate(comment_count=Count("comments"))
    )
    serializer_class = PostSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)

    @staticmethod
    def _params_to_ints(qs):
        """Converts a list of string IDs to a list of integer"""
        return [int(str_id) for str_id in qs.split(",")]

    def get_queryset(self):
        queryset = self.queryset

        title = self.request.query_params.get("title")
        content = self.request.query_params.get("content")

        if title:
            queryset = queryset.filter(title__icontains=title)

        if content:
            queryset = queryset.filter(content__icontains=content)

        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return PostListSerializer

        if self.action == "retrieve":
            return PostDetailSerializer

        if self.action == "upload_image":
            return PostImageSerializer

        return PostSerializer

    @action(methods=["POST", "DELETE"], detail=True, url_path="upload-image")
    def upload_image(self, request, pk=None):
        """Endpoint for uploading/deleting image to specific post"""
        post = self.get_object()

        if request.method == "POST":
            serializer = self.get_serializer(post, data=request.data)
            serializer.is_valid(raise_exception=True)
            post.image = serializer.validated_data.get("image")
            post.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        if request.method == "DELETE":
            post.image.delete(save=True)
            post.save()
            return Response(
                {"detail": "Image deleted"}, status=status.HTTP_204_NO_CONTENT
            )

    # Only for documentation purposes
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="title",
                type=str,
                description="Filter by title"
            ),
            OpenApiParameter(
                name="content",
                type=str,
                description="Filter by content"
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.select_related("post", "author")
    serializer_class = CommentSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)


class FeedViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Post.objects.all()
    serializer_class = PostListSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        subscriber = self.request.user
        return (
            Post.objects.filter(
                Q(author__owner__subscriber=subscriber) | Q(author=subscriber)
            )
            .order_by("-created_at")
            .select_related("author")
            .prefetch_related("comments")
        )
