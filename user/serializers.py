from django.contrib.auth import get_user_model
from rest_framework import serializers

from user.models import User, UserFollowing


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ("id", "email", "password", "is_staff")
        read_only_fields = ("id", "is_staff")
        extra_kwargs = {"password": {"write_only": True, "min_length": 8}}

    def create(self, validated_data):
        """Create a new user with encrypted password and return it"""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update a user, set the password correctly and return it"""
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "first_name", "last_name", "email", "photo")


class UserDetailSerializer(serializers.ModelSerializer):
    followers = serializers.IntegerField(
        source="following.count",
        read_only=True
    )

    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "email",
            "photo",
            "followers",
        )


class UserPhotoUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "photo")


class UserDetailFollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "photo")


class UserFollowingListSerializer(serializers.ModelSerializer):
    user = UserDetailFollowSerializer(many=False, read_only=True)

    class Meta:
        model = UserFollowing
        fields = ("user",)


class UserFollowersListSerializer(serializers.ModelSerializer):
    subscriber = UserDetailFollowSerializer(many=False, read_only=True)

    class Meta:
        model = UserFollowing
        fields = ("subscriber",)


class FollowingUserSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source="user.id", read_only=True)
    subscriber_id = serializers.IntegerField(
        source="subscriber.id",
        read_only=True
    )

    class Meta:
        model = User
        fields = ("user_id", "subscriber_id")
