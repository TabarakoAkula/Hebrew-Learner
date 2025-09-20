from aiogram.fsm.state import State, StatesGroup


class SearchStatesGroup(StatesGroup):
    menu = State()
    result = State()


class SendReportStatesGroup(StatesGroup):
    input = State()


class AnswerReportStatesGroup(StatesGroup):
    input = State()


class CollectionsSearchIdStatesGroup(StatesGroup):
    input = State()


class CollectionsAddWordStatesGroup(StatesGroup):
    input = State()


class CollectionsAddExistingTranslationWordStatesGroup(StatesGroup):
    input = State()


class CollectionsAddMultipleTranslationWordStatesGroup(StatesGroup):
    input = State()


class CollectionsRemoveWordStatesGroup(StatesGroup):
    input = State()


class CollectionsEditStatesGroup(StatesGroup):
    menu = State()
