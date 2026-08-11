from aiogram.fsm.state import State, StatesGroup


class RegistrationStates(StatesGroup):
    # Ожидание согласия на обработку ПД
    waiting_for_consent = State()

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

    # Ожидание ввода пароля
    waiting_for_password = State()
    # Ожидание подтверждения пароля
    waiting_for_password_confirmation = State()

    waiting_for_confirmation = State()
    waiting_for_final_confirm = State()


# class RegistrationStates(StatesGroup):
#     # Ожидание ввода телефона (первый шаг)
#     waiting_for_phone = State()

#     # Ожидание выбора компании
#     waiting_for_company = State()

#     # Ожидание выбора департамента
#     waiting_for_department = State()

#     # Ожидание выбора должности
#     waiting_for_job_title = State()

#     # Ожидание ввода ФИО
#     waiting_for_full_name = State()

#     # Ожидание ввода email
#     waiting_for_email = State()

#     # Ожидание ввода даты рождения
#     waiting_for_birth_date = State()

#     # Ожидание ввода пароля
#     waiting_for_password = State()

#     # Ожидание подтверждения пароля
#     waiting_for_password_confirmation = State()

#     # Ожидание согласия на обработку ПД
#     waiting_for_consent = State()

#     # Ожидание подтверждения данных
#     waiting_for_confirmation = State()
