from django.db import models


class JobTitle(models.Model):
    title = models.CharField(max_length=30, verbose_name='Название должности')
    description = models.TextField(blank=True, null=True, verbose_name='Описание должности')

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = 'Должность'
        verbose_name_plural = 'Должности'
        ordering = ['title']


class Lightning(models.Model):
    title = models.CharField(max_length=100, verbose_name='Молния')
    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=True, verbose_name='Дата')
    description_of_consequences = models.TextField(blank=True, null=True, verbose_name='Описание последствий')
    incident_location = models.CharField(max_length=100, blank=True, null=True, verbose_name='Место происшествия')
    incident_coordinates = models.CharField(max_length=100, blank=True, null=True, verbose_name='Координаты происшествия')
    plan_of_action = models.TextField(blank=True, null=True, verbose_name='План мероприятий по ликвидации происшествия')
    responsible_persons = models.TextField(blank=True, null=True, verbose_name='Ответственные')
    min_test_percent_course = models.IntegerField(default=90, verbose_name='Минимальный процент для прохождения теста')
    user = models.ManyToManyField('bot.TelegramUser', blank=True, verbose_name='Пользователь')
    group = models.ManyToManyField('bot.TelegramGroup', blank=True, verbose_name='Группа пользователей')
    job_titles = models.ManyToManyField(JobTitle, blank=True, verbose_name='Должности')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Молния'
        verbose_name_plural = 'Молнии'
        ordering = ['title']

class LightningMessage(models.Model):
    lightning = models.ForeignKey(Lightning, related_name='messages', verbose_name='Молния', on_delete=models.CASCADE)
    content = models.TextField(max_length=2000, verbose_name='Сообщение')
    button_text = models.CharField(max_length=25, default='Далее', verbose_name='Текст для кнопки')
    order = models.PositiveSmallIntegerField(default=1, verbose_name='Порядок')
    image_lightning = models.ImageField(upload_to='image_lightning/', blank=True, null=True, verbose_name='Изображение')
    file_lightning = models.FileField(upload_to='file_lightning', null=True, blank=True, verbose_name="Файл для сообщения")
    send_text = models.BooleanField(default=False, verbose_name='Отправлять текст')
    send_file = models.BooleanField(default=False, verbose_name='Отправлять файл')

    def __str__(self):
        return f"{self.lightning.title}: {self.content[:50]}"

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
        ordering = ['lightning__title']


class LightningQuestion(models.Model):
    lightning = models.ForeignKey(Lightning, related_name='questions', verbose_name='Молния', on_delete=models.CASCADE)
    title = models.TextField(verbose_name='Вопрос')
    is_multiple_choice = models.BooleanField(default=False, verbose_name='Несколько ответов')
    order = models.PositiveSmallIntegerField(default=1)
    is_display_question = models.BooleanField(default=False, verbose_name='Отобразить')

    def __str__(self):
        return self.title or f"Вопрос {self.id}"

    class Meta:
        verbose_name = 'Вопрос молнии'
        verbose_name_plural = 'Вопросы молнии'
        ordering = ['order']


class LightningAnswer(models.Model):
    question = models.ForeignKey(LightningQuestion, related_name='answer', on_delete=models.CASCADE, verbose_name='Вопрос')
    number = models.CharField(max_length=5, null=True, blank=True, verbose_name='Номер')
    text = models.TextField(verbose_name='Текст ответа')
    is_correct = models.BooleanField(default=False, verbose_name='Правильный ответ')
    is_display_answer = models.BooleanField(default=False, verbose_name='Отобразить')

    def __str__(self):
        return f"Ответ {self.number} для {self.question}"

    class Meta:
        verbose_name = 'Вариант ответа молнии'
        verbose_name_plural = 'Варианты ответов молнии'
        ordering = ['number']


class LightningRead(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, editable=False, verbose_name='Прочитано')
    updated_at = models.DateTimeField(auto_now=True, editable=False, verbose_name='Обновлено')
    user = models.ForeignKey("bot.TelegramUser", on_delete=models.CASCADE, verbose_name='Пользователь')
    lightning = models.ForeignKey(Lightning, on_delete=models.CASCADE, verbose_name='Молния')
    is_read = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Статус чтения молнии'
        verbose_name_plural = 'Статусы чтения молний'
        ordering = ['created_at']
        unique_together = ('user', 'lightning')


def default_user_answer():
    return {"results": []}

class LightningTest(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, editable=False, verbose_name='Дата записи теста')
    updated_at = models.DateTimeField(auto_now=True, editable=False, verbose_name='Обновление записи теста')
    user = models.ForeignKey("bot.TelegramUser", on_delete=models.CASCADE, verbose_name='Пользователь')
    lightning = models.ForeignKey(Lightning, on_delete=models.CASCADE, verbose_name='Молния')
    question = models.ForeignKey(LightningQuestion, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Вопрос')
    user_answer = models.JSONField(verbose_name="Ответы пользователя", default=default_user_answer)
    complete = models.BooleanField(default=False, verbose_name="Успешно")
    quantity_correct = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="Процент правильных ответов")
    quantity_not_correct = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="Процент не правильных ответов")

    class Meta:
        verbose_name = 'Результат тестирования'
        verbose_name_plural = 'Результаты тестирования'
        ordering = ['created_at']
        unique_together = ('user', 'lightning')

    def __str__(self):
        return f"{self.user} |{self.lightning} | {self.question} | {self.complete} |"