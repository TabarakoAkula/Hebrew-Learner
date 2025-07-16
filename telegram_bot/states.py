from aiogram.fsm.state import State, StatesGroup


class SearchStatesGroup(StatesGroup):
    menu = State()
    result = State()
