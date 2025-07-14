import apps.users.views as views
from django.urls import path


urlpatterns = [
    path("<str:telegram_id>", views.UserGetCreateView.as_view()),
]
