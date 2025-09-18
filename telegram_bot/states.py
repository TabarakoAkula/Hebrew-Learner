from aiogram.fsm.state import State, StatesGroup


class SearchStatesGroup(StatesGroup):
    menu = State()
    result = State()


class SendReportStatesGroup(StatesGroup):
    input = State()


class AnswerReportStatesGroup(StatesGroup):
    input = State()
