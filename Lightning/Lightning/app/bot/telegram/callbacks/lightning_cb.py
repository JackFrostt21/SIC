from typing import Literal
from aiogram.filters.callback_data import CallbackData


# Фильтр периода списка молний
class PeriodFilterCB(CallbackData, prefix="period_filter"):
    period: Literal["week", "month", "three_months", "six_months"]


# Открыть конкретную молнию (показать контент + кнопки действий)
class OpenLightningCB(CallbackData, prefix="open_lightning"):
    lightning_id: int


# Отметить молнию как прочитанную (если без теста)
class MarkReadCB(CallbackData, prefix="lightning_read"):
    lightning_id: int


# Старт теста по молнии (можно использовать как “Ознакомился и к тесту”)
class StartTestCB(CallbackData, prefix="test_start"):
    lightning_id: int


# Выбор/переключение ответа на вопрос
class AnswerCB(CallbackData, prefix="answer"):
    lightning_id: int
    question_id: int
    answer_id: int


# Навигация по вопросам (вперёд/назад)
class NavCB(CallbackData, prefix="question_nav"):
    lightning_id: int
    current_question_index: int
    move: Literal["prev", "next"]


# Завершить тест и подсчитать результат
class FinishTestCB(CallbackData, prefix="test_finish"):
    lightning_id: int


# Повторить тест (после неудачи)
class RetryTestCB(CallbackData, prefix="test_retry"):
    lightning_id: int
