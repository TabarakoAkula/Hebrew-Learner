import apps.words.views as views
from django.urls import include, path
from rest_framework.routers import DefaultRouter


router = DefaultRouter()

urlpatterns = [
    path("words", views.GetWordView.as_view()),
    path("words/by-link", views.GetWordByLinkView.as_view()),
    path("", include(router.urls)),
]
