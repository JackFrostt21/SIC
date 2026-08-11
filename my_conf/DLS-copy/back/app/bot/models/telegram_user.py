from django.db import models
from django.contrib.auth.models import AbstractUser

from app.core.abstract_models import BaseModel, BaseRowStateModel
from app.organization.models import Company, Department, JobTitle

# TODO: Добавить в модели индексы

class TelegramUser(BaseModel, BaseRowStateModel):
    """
    Модель пользователя Telegram
    """

    telegram_id = models.BigIntegerField(verbose_name="Telegram ID", unique=True)
    guid_1c = models.CharField(max_length=50, null=True, blank=True, verbose_name="Код 1С")
    user_name = models.CharField(
        max_length=100, verbose_name="Username", blank=True, null=True
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        verbose_name="Компания",
        null=True,
        blank=True,
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Подразделение",
    )
    job_title = models.ForeignKey(
        JobTitle,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Должность",
    )
    full_name = models.CharField(
        max_length=100, verbose_name="ФИО", blank=True, null=True
    )
    last_name = models.CharField(
        max_length=100, verbose_name="Фамилия", blank=True, null=True
    )
    first_name = models.CharField(
        max_length=100, verbose_name="Имя", blank=True, null=True
    )
    middle_name = models.CharField(
        max_length=100, verbose_name="Отчество", blank=True, null=True
    )
    date_of_birth = models.CharField(
        max_length=10, verbose_name="Дата рождения", blank=True, null=True
    )
    phone = models.CharField(
        max_length=20, verbose_name="Телефон", blank=True, null=True
    )
    email = models.EmailField(
        max_length=50, verbose_name="Email", blank=True, null=True
    )
    language = models.CharField(
        max_length=20, verbose_name="Язык", blank=True, null=True, default="ru"
    )
    image = models.ImageField(
        upload_to="telegramuser",
        null=True,
        blank=True,
        verbose_name="Фото пользователя",
    )
    personal_data_consent = models.BooleanField(
        verbose_name="Согласие на обработку персональных данных", default=False
    )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.assign_obligatory_courses()

    def assign_obligatory_courses(self):
        """
        Проверяет и назначает обязательные курсы при сохранении пользователя.
        """
        from django.db.models import Q
        from app.learning_app.models.additional import ObligatoryList

        # Если нет ни должности, ни подразделения - выходим
        if not self.department and not self.job_title:
            return

        query = Q()
        if self.department:
            query |= Q(department=self.department)

        if self.job_title:
            query |= Q(jobtitle=self.job_title)

        # Находим записи ObligatoryList, соответствующие критериям
        obligatory_lists = ObligatoryList.objects.filter(query).select_related(
            "training_course"
        )

        for item in obligatory_lists:
            if item.training_course:
                item.training_course.user.add(self)

    class Meta:
        verbose_name = "Студент"
        verbose_name_plural = "Студенты"
        ordering = ["id"]

    def __str__(self):
        return f'{self.full_name or self.user_name or f"ID: {self.telegram_id}"}'


class CustomUser(AbstractUser):
    """
    Кастомная модель пользователя для веб-аутентификации.
    Связана с TelegramUser через OneToOneField.
    """

    telegram_user = models.OneToOneField(
        TelegramUser,
        on_delete=models.SET_NULL,
        verbose_name="Telegram пользователь",
        null=True,
        blank=True,
        related_name="custom_user",
    )

    # TODO Добавил метод для хеширования пароля, если менять/создавать в админке, для фронта получается получить токен, но для входа в админку НЕ РАБОТАЕТ!!!
    def save(self, *args, **kwargs):
        if self.password and not self.password.startswith(
            ("pbkdf2_sha256$", "bcrypt$", "argon2$")
        ):
            self.set_password(self.password)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        if self.telegram_user:
            return f"{self.username} ({self.telegram_user.full_name or self.telegram_user.user_name})"
        return self.username


class TelegramGroup(BaseModel):
    """
    Модель группы пользователей Telegram
    """

    name = models.CharField(max_length=100, verbose_name="Наименование группы")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")
    users = models.ManyToManyField(
        TelegramUser, blank=True, verbose_name="Пользователи", related_name="groups"
    )

    class Meta:
        verbose_name = "Группа студентов"
        verbose_name_plural = "Группы студентов"
        ordering = ["name"]

    def __str__(self):
        return self.name


class SubscriptionUser(BaseModel):
    """
    Модель подписки пользователя
    """
    user = models.ForeignKey(
        TelegramUser,
        on_delete=models.CASCADE,
        verbose_name="Пользователь"
    )
    telegram_id = models.BigIntegerField(verbose_name="Telegram ID", unique=True)

    class Meta:
        verbose_name = "Подписка пользователя"
        verbose_name_plural = "Подписки пользователей"
        ordering = ["user"]

    def __str__(self):
        return self.user.full_name or self.user.user_name
