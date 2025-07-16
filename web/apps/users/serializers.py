from apps.users.models import User
from rest_framework import serializers


class UserSerializer(serializers.Serializer):
    telegram_id = serializers.CharField(max_length=120, required=True)
    telegram_username = serializers.CharField(max_length=256, required=False)
    created_at = serializers.DateTimeField(read_only=True, required=False)
    updated_at = serializers.DateTimeField(read_only=True, required=False)
    moderator = serializers.BooleanField(default=False, read_only=True)

    def create(self, validated_data):
        try:
            user = User.objects.get(telegram_id=validated_data.get("telegram_id"))
        except User.DoesNotExist:
            user = User(
                telegram_id=validated_data.get("telegram_id"),
                telegram_username=validated_data.get("telegram_username"),
            )
            user.save()
        return user

    def update(self, instance, validated_data):
        instance.telegram_username = validated_data.get(
            "telegram_username", instance.telegram_username
        )
        instance.save()
        return instance
