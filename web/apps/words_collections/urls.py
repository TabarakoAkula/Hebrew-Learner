from apps.words_collections import views
from django.urls import path

urlpatterns = [
    path("<int:pk>", views.CollectionDetailView.as_view(), name="collection_detail"),
    path("", views.CollectionListCreateView.as_view(), name="collection_list_create"),
]
