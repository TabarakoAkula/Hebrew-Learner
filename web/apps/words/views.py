from apps.words.serializers import CategorySerializer, WordSerializer
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView, Response
from apps.words.models import Category, Word


class GetWordView(APIView):
    @staticmethod
    def get(request, word):
        try:
            message_id = request.GET["message_id"]
        except KeyError:
            return Response({"success": False, "message": "Bad request: message_id was not provided"})
        word_obj, new = Word.objects.get_or_create(hebrew_word=word)
        serializer = WordSerializer(word_obj)
        data = serializer.data
        data["new"] = new
        if new:
            pass
            # TODO Send CELERY task for analysis
        return Response({"success": True, "data": data})


class GetCategoriesView(ModelViewSet):
    lookup_field = "hebrew_name"
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
