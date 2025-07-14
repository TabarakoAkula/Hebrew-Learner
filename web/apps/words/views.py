from apps.words.models import Category, Word
from apps.words.serializers import CategorySerializer, WordSerializer
from rest_framework.views import APIView, Response
from rest_framework.viewsets import ModelViewSet


class GetWordView(APIView):
    @staticmethod
    def get(request, word):
        try:
            message_id = request.GET["message_id"]
        except KeyError:
            return Response(
                {
                    "success": False,
                    "message": "Bad request: message_id was not provided",
                }
            )
        word_obj, new = Word.objects.get_or_create(hebrew_word=word)
        serializer = WordSerializer(word_obj)
        data = serializer.data
        data["new"] = new
        if new or not word_obj.analyzed:
            pass
            message_id += "use id for changing messages"
            # TODO Send CELERY task for analysis
        return Response({"success": True, "data": data})


class GetCategoriesView(ModelViewSet):
    lookup_field = "hebrew_name"
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
