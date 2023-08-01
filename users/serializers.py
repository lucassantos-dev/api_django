from rest_framework import serializers  # Adicione esta linha
from .models import UserAccount
from djoser.serializers import UserCreateSerializer
from .models import UserAccount

class CustomUserSerializer(UserCreateSerializer):
    avatar = serializers.ImageField(required=False)

    class Meta(UserCreateSerializer.Meta):
        model = UserAccount
        fields = ('id', 'email', 'first_name', 'last_name', 'password', 'avatar')