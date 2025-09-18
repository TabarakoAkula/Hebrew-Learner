import apps.users.views as views
from django.urls import path


urlpatterns = [
    path("<str:telegram_id>", views.UserGetCreateView.as_view()),
    path("<str:telegram_id>/report/send", views.SendReportAPIView.as_view()),
    path("<str:telegram_id>/report/answer", views.AnswerReportAPIView.as_view()),
]
