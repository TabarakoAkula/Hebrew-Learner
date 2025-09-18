from apps.words_collections.models import Collection
from apps.words_collections.serializers import (
    CollectionListSerializer,
    CollectionSerializer,
)
from rest_framework import generics


class CollectionListCreateView(generics.ListCreateAPIView):
    queryset = Collection.objects.all()

    def get_serializer_class(self):
        if self.request.method == "GET":
            return CollectionListSerializer


class CollectionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Collection.objects.all()
    serializer_class = CollectionSerializer
