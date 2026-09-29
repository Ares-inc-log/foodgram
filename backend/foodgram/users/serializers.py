from djoser.serializers import UserSerializer, UserCreateSerializer
from rest_framework.serializers import ModelSerializer, ImageField
from django.contrib.auth import get_user_model

from users.tools import Base64ImageField



User = get_user_model()


class MyUserSerializer(UserSerializer):

    class Meta(UserSerializer.Meta):
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'avatar')


class MyUserCreateSerializer(UserCreateSerializer):

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'password')


class AvatarSerializer(ModelSerializer):
    avatar = Base64ImageField(required=True)

    class Meta:
        model = User
        fields = ('avatar',)
