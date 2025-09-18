from apps.words_collections.models import Collection
from rest_framework import serializers


class CollectionSerializer(serializers.ModelSerializer):
    words = serializers.SerializerMethodField()

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
        return [
            {"word": word.hebrew_word, "translation": word.data.get("translation", "")}
            for word in obj.words.all()
        ]


class CollectionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ["id", "name"]
