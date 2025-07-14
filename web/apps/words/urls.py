import apps.words.views as views
from rest_framework.routers import DefaultRouter
from django.urls import include, path


router = DefaultRouter()
router.register(r"categories", views.GetCategoriesView, basename="category")

urlpatterns = [
    path("<str:word>/", views.GetWordView.as_view()),
    path("", include(router.urls)),
]
