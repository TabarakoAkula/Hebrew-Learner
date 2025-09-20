from apps.words_collections import views
from django.urls import path

urlpatterns = [
    path(
        "<int:pk>/remove_word",
        views.CollectionRemoveWordView.as_view(),
        name="collection_remove_word",
    ),
    path(
        "<int:pk>/add_word",
        views.CollectionAddWordView.as_view(),
        name="collection_add_word",
    ),
    path("<int:pk>", views.CollectionDetailView.as_view(), name="collection_detail"),
    path("", views.CollectionListCreateView.as_view(), name="collection_list_create"),
]
