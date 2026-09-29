from djoser.serializers import UserSerializer
from django.contrib.auth import get_user_model


User = get_user_model()


class MyUserSerializer(UserSerializer):

    class Meta(UserSerializer.Meta):
        model = User
        fields = tuple(UserSerializer.Meta.fields) + ('avatar')
