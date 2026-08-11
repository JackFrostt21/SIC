from django.conf import settings
from django.db import models

from apps.fleet.models import Vehicle


class Inspection(models.Model):
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.PROTECT,
        related_name="inspections",
        verbose_name="ТС",
    )
    inspection_date = models.DateField("Дата проверки")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_inspections",
        verbose_name="Создал запись",
    )
    notes = models.TextField("Комментарий", blank=True)
    created_at = models.DateTimeField("Создано", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)
    deleted_at = models.DateTimeField("Удалено", null=True, blank=True)

    class Meta:
        verbose_name = "Проверка ТС"
        verbose_name_plural = "Проверки ТС"
        ordering = ("-inspection_date", "-created_at")

    def __str__(self) -> str:
        return f"{self.vehicle} — {self.inspection_date}"


class InspectionFile(models.Model):
    inspection = models.ForeignKey(
        Inspection,
        on_delete=models.CASCADE,
        related_name="files",
        verbose_name="Проверка",
    )
    file_name = models.CharField("Имя файла", max_length=255)
    file_url = models.URLField("Ссылка на файл")
    mime_type = models.CharField("MIME-тип", max_length=100, blank=True)
    size_bytes = models.PositiveBigIntegerField("Размер, байт", null=True, blank=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="uploaded_inspection_files",
        verbose_name="Загрузил",
    )
    uploaded_at = models.DateTimeField("Загружено", auto_now_add=True)

    class Meta:
        verbose_name = "Файл проверки"
        verbose_name_plural = "Файлы проверок"
        ordering = ("-uploaded_at", "file_name")

    def __str__(self) -> str:
        return self.file_name
