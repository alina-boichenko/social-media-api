from rest_framework import serializers

from blog.models import Post, Comment
from user.serializers import UserSerializer


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ("id", "title", "author", "created_at", "content")


class CommentSerializer(serializers.ModelSerializer):
    post_id = PostSerializer
    post_title = serializers.CharField(source="post.title", read_only=True)
    author = serializers.CharField(source="author.email", read_only=True)

    class Meta:
        model = Comment
        fields = (
            "id",
            "author",
            "created_at",
            "content",
            "post_id",
            "post_title"
        )


class PostListSerializer(PostSerializer):
    author = serializers.CharField(source="author.email", read_only=True)

    class Meta:
        model = Post
        fields = (
            "id",
            "title",
            "author",
            "created_at",
            "content",
            "image",
            "comments",
        )


class PostDetailSerializer(PostSerializer):
    author = UserSerializer(many=False, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = (
            "id",
            "title",
            "author",
            "created_at",
            "content",
            "image",
            "comments"
        )


class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ("id", "image")
