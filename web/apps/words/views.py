from apps.words.models import Category, Word
from apps.words.serializers import CategorySerializer, WordSerializer
from apps.words.tasks import manager_analyze_word
from rest_framework.views import APIView, Response
from rest_framework.viewsets import ModelViewSet


class GetWordView(APIView):
    @staticmethod
    def get(request):
        try:
            word = request.GET["word"]
            message_id = request.GET["message_id"]
            telegram_id = request.GET["telegram_id"]
        except KeyError:
            return Response(
                {
                    "success": False,
                    "message": "Bad request: not all parameters were provided",
                }
            )
        word_obj, new = Word.objects.get_or_create(hebrew_word=word)
        serializer = WordSerializer(word_obj)
        data = serializer.data
        data["new"] = new
        if new or not word_obj.analyzed:
            manager_analyze_word(
                {
                    "word": word,
                    "telegram_id": telegram_id,
                    "message_id": message_id,
                }
            )
        return Response({"success": True, "data": data})


class GetCategoriesView(ModelViewSet):
    lookup_field = "hebrew_name"
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
