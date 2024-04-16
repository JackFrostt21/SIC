from aiogram.dispatcher.filters.state import StatesGroup, State


'''-------------------------------------------States----------------------------------------------'''


class Address(StatesGroup):
    text_location = State()
    location = State()
    landmark = State()
    title = State()
    end = State()


class AddressInOrder(StatesGroup):
    text_location = State()
    location = State()
    landmark = State()
    title = State()
    end = State()


class LocaleRegSteps(StatesGroup):
    enter_name = State()
    enter_full_name = State()
    enter_photo = State()
    enter_date_birth = State()
    enter_region = State()
    enter_education = State()
    enter_speciality = State()
    enter_experience = State()
    enter_knowledge_of_languages = State()
    enter_phone = State()
    set_language = State()
    set_entity = State()
    enter_organization = State()
    enter_email = State()
    registration_finish = State()


class FeedbackSave(StatesGroup):
    set_order = State
    set_items = State()
    set_theme = State()
    set_description = State()
    set_photo = State()
    feedback_finish = State()


class ChangePersonalData(StatesGroup):
    enter_change = State()
