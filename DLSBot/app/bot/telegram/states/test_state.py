from aiogram.fsm.state import State, StatesGroup


class TestState(StatesGroup):
    in_progress = State()  # Состояние, когда пользователь проходит тест
    # user_answers = State() # Возможно, не нужно отдельное состояние, если хранить в data FSM
