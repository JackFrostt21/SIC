from aiogram.fsm.state import State, StatesGroup


class RegistrationStates(StatesGroup):
    # Ожидание ввода телефона (первый шаг)
    waiting_for_phone = State()

    # Ожидание выбора компании
    waiting_for_company = State()

    # Ожидание выбора департамента
    waiting_for_department = State()

    # Ожидание выбора должности
    waiting_for_job_title = State()

    # Ожидание ввода ФИО
    waiting_for_full_name = State()

    # Ожидание ввода email
    waiting_for_email = State()

    # Ожидание ввода даты рождения
    waiting_for_birth_date = State()

    # Ожидание подтверждения данных
    waiting_for_confirmation = State()