from apps.users.models import User
from apps.words.models import Word
from apps.words_collections.models import Collection
from apps.words_collections.serializers import (
    CollectionListSerializer,
    CollectionSerializer,
)
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

PEALIM_LINK = "https://www.pealim.com"


class CollectionListCreateView(generics.ListCreateAPIView):
    queryset = Collection.objects.all()

    def get_serializer_class(self):
        if self.request.method == "GET":
            return CollectionListSerializer
        return CollectionSerializer

    def create(self, request, *args, **kwargs):
        telegram_id = request.data.get("telegram_id")
        if not telegram_id:
            return Response(
                {
                    "success": False,
                    "message": "telegram_id обязателен для создания коллекции",
                },
            )
        try:
            user = User.objects.get(telegram_id=telegram_id)
        except User.DoesNotExist:
            return Response(
                {
                    "success": False,
                    "message": "Пользователь с данным telegram_id не найден",
                },
            )
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(owner=user)
        return Response(
            {
                "success": True,
                "message": "Коллекция успешно создана",
                "data": serializer.data,
            },
        )


class CollectionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Collection.objects.all()
    serializer_class = CollectionSerializer


class CollectionRemoveWordView(APIView):
    @staticmethod
    def post(request, pk):
        collection = Collection.objects.get(pk=pk)
        word_text = request.data.get("word")

        collection_data = collection.data
        words_list: dict = collection_data.get("words", {})

        try:
            del words_list[word_text]
        except KeyError:
            return Response(
                {
                    "success": False,
                    "message": "Ошибка удаления слова - "
                    "слово не существует в данной коллекции",
                },
                status=status.HTTP_200_OK,
            )
        collection_data["words"] = words_list
        collection.data = collection_data
        collection.save()

        return Response(
            {"success": True, "message": "Слово успешно удалено из коллекции"},
            status=status.HTTP_200_OK,
        )


class CollectionAddWordView(APIView):
    @staticmethod
    def post(request, pk):
        collection = Collection.objects.get(pk=pk)
        word_data = request.data

        collection_data = collection.data
        words_list: dict = collection_data.get("words", {})
        words_keys = list(words_list.keys())

        if word_data.get("existing", False):
            is_multiple = word_data.get("is_multiple", False)
            if is_multiple:
                try:
                    word = Word.objects.get(hebrew_word=word_data.get("word"))
                except Word.DoesNotExist:
                    return Response(
                        {
                            "success": False,
                            "message": "Ошибка добавления слова, "
                            "слово отсутствует в системе",
                        }
                    )
                existing_word_data = word.data
                current_word = list(
                    filter(
                        lambda x: word_data.get("id").replace("_", "-") in x.get("link"),
                        existing_word_data,
                    )
                )
                if not current_word:
                    return Response(
                        {
                            "success": False,
                            "message": "Ошибка добавления слова, "
                            "слово отсутствует в системе",
                        }
                    )
                current_word = current_word[0]
                hebrew_word = current_word.get("word")
                data_to_add = {
                    "word": hebrew_word,
                    "base_form": current_word.get("label"),
                    "translation": current_word.get("translation"),
                    "link": PEALIM_LINK + current_word.get("link"),
                }
                words_list[hebrew_word] = data_to_add
                final_word = hebrew_word
            else:
                try:
                    word = Word.objects.get(pk=word_data.get("id"))
                except Word.DoesNotExist:
                    return Response(
                        {
                            "success": False,
                            "message": "Ошибка добавления слова, "
                            "слово отсутствует в системе",
                        }
                    )
                if words_keys.count(word.hebrew_word) > 0:
                    return Response(
                        {"success": False, "message": "Слово уже есть в коллекции"}
                    )
                data_to_add = {
                    "word": word.hebrew_word,
                    "base_form": word_data.get("base_form", word.data.get("base_form")),
                    "translation": word_data.get(
                        "translation", word.data.get("translation")
                    ),
                    "link": word.pealim_link,
                }
                words_list[word.hebrew_word] = data_to_add
                final_word = word.hebrew_word
        else:
            word = word_data.get("word")
            if words_keys.count(word) > 0:
                return Response(
                    {"success": False, "message": "Слово уже есть в коллекции"}
                )
            data_to_add = {
                "word": word_data.get("word"),
                "base_form": word_data.get("base_form", ""),
                "translation": word_data.get("translation", ""),
                "link": word_data.get("link", ""),
            }
            words_list[word] = data_to_add
            final_word = word
        collection_data["words"] = words_list
        collection.data = collection_data
        collection.save()

        return Response(
            {
                "success": True,
                "message": f"✔️ Слово {final_word} успешно добавлено в коллекцию",
                "data": data_to_add,
            },
            status=status.HTTP_200_OK,
        )
