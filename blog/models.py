import os.path
import uuid

from django.conf import settings
from django.db import models
from django.utils.text import slugify


def post_image_file_path(instance, file_name):
    _, extension = os.path.splitext(file_name)
    filename = f"{slugify(instance.image)}-{uuid.uuid4()}{extension}"
    return os.path.join("uploads/posts/", filename)


class Post(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="posts",
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    content = models.CharField(max_length=255)
    image = models.ImageField(upload_to=post_image_file_path, blank=True)

    def __str__(self) -> str:
        return self.title


class Comment(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="comments",
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    content = models.CharField(max_length=255)
    post = models.ForeignKey(
        Post,
        related_name="comments",
        on_delete=models.CASCADE
    )

    def __str__(self) -> str:
        return f"{self.author}: {self.content}"
