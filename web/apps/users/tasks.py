# import asyncio
#
# from apps.questions.constants import TR_TG_BUTTONS
# from apps.questions.models import Question
# from apps.questions.notifier import edit_message, logs_snitch, send_message
# from apps.questions.utils import ask_question
# from celery import shared_task
# from django.conf import settings
#
# USE_CELERY = settings.USE_CELERY


# def manager_ask_question(data: dict) -> None:
#     if USE_CELERY:
#         return celery_ask_question.delay(data)
#     return celery_ask_question(data)
#
#
# @shared_task()
# def celery_ask_question(data: dict) -> None:
#     return asyncio.run(
#         edit_message(
#             data["telegram_id"],
#             {
#                 "message": answer_text,
#                 "message_id": data["message_id"],
#                 "inline_reply_markup": [
#                     [
#                         {
#                             "title": TR_TG_BUTTONS["ask_question"][data["language"]],
#                             "callback": "ask_question",
#                         },
#                     ],
#                     [
#                         {
#                             "title": TR_TG_BUTTONS["back_to_menu"][data["language"]],
#                             "callback": "back_to_menu",
#                         },
#                     ],
#                 ],
#             },
#         ),
#     )
