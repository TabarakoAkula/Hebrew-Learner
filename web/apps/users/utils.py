def get_report_keyboard(telegram_id: str) -> list[list[dict[str, str]]]:
    return [
        [
            {
                "title": "💬 Ответить на запрос",
                "callback": f"answer_report_{telegram_id}",
            },
        ]
    ]


def get_report_answer_keyboard() -> list[list[dict[str, str]]]:
    return [
        [
            {
                "title": "🔙 В меню",
                "callback": "back_to_menu",
            },
            {
                "title": "📍",
                "callback": "report",
            },
        ]
    ]
