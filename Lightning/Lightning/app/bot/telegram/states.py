from aiogram.fsm.state import StatesGroup, State


class RegistrationStates(StatesGroup):
    waiting_for_surname = State()
    waiting_for_name = State()
    waiting_for_birth_date = State()
    waiting_for_precheck = State()
    waiting_for_phone = State()
    waiting_for_company = State()
    # waiting_for_department = State() убрал - много элементов
    # waiting_for_job_title = State() убрал - много элементов
    waiting_for_patronymic = State()
    waiting_for_email = State()
    waiting_for_confirmation = State()
    waiting_for_final_confirm = State()