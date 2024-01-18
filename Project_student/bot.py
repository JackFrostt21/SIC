from aiogram import Bot, Dispatcher, executor, types
from aiohttp import ClientSession


API_TOKEN = "6686307025:AAFz1tjuBXs3_4m6eAUBII2B5I5j3GPj4uE"

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=["start"])
async def send_welcome(message: types.Message):
    # обработчик вызывается при активации start
    await message.reply(
        "Привет! Я бот для записи на курсы. Нажмите /courses чтобы увидеть список доступных курсов."
    )


@dp.message_handler(commands=["courses"])
async def list_courses(message: types.Message):
    courses = await get_active_courses()
    if courses:
        markup = types.InlineKeyboardMarkup()
        for course in courses:
            button_text = f"{course['course_name']} с {course['data_start']} по {course['data_end']}"
            callback_data = f"choose_course:{course['id']}"
            markup.add(
                types.InlineKeyboardButton(button_text, callback_data=callback_data)
            )
        await message.reply("Выберите курс:", reply_markup=markup)
    else:
        await message.reply(
            "Извините, не удалось получить список курсов, попробуйте выполнить запрос позже"
        )


async def get_active_courses():
    url = "http://localhost:8000/courses/"
    async with ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                courses = await response.json()
                return courses
            else:
                print("Ошибка при получении данных с сервера:", response.status)
                return []


@dp.callback_query_handler(lambda c: c.data and c.data.startswith("choose_course:"))
async def process_callback_choose_course(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    course_id = callback_query.data.split(":")[1]

    #  НУЖНО еще добавить аутентификацию пользователя и
    #  отправку данных в модель class Student(models.Model):


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
