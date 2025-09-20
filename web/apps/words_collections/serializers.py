from apps.words_collections.models import Collection
from rest_framework import serializers


class CollectionSerializer(serializers.ModelSerializer):
    words = serializers.SerializerMethodField()
    owner = serializers.SerializerMethodField()

    class Meta:
        model = Collection
        fields = [
            "id",
            "name",
            "is_close",
            "created_at",
            "updated_at",
            "owner",
            "words",
        ]

    @staticmethod
    def get_words(obj):
        return obj.data.get("words", {})

    @staticmethod
    def get_owner(obj):
        return obj.owner.telegram_id


class CollectionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ["id", "name"]
