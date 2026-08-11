from django.db import models


class Vehicle(models.Model):
    plate_number = models.CharField("Госномер", max_length=20, unique=True)
    name = models.CharField("Наименование", max_length=255, blank=True)
    omnicomm_uuid = models.UUIDField("UUID Omnicomm", null=True, blank=True, unique=True)
    omnicomm_vehicle_id = models.BigIntegerField(
        "ID ТС Omnicomm",
        null=True,
        blank=True,
        unique=True,
        help_text=(
            "Числовой идентификатор ТС во внешней системе для отчётных "
            "запросов; при реальной интеграции требует подтверждения."
        ),
    )
    terminal_id = models.BigIntegerField("ID терминала", null=True, blank=True, unique=True)
    is_active = models.BooleanField("Активно", default=True)
    is_subject_to_inspection = models.BooleanField("Участвует в проверках", default=True)
    created_at = models.DateTimeField("Создано", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        verbose_name = "Транспортное средство"
        verbose_name_plural = "Транспортные средства"
        ordering = ("plate_number",)

    def __str__(self) -> str:
        return f"{self.plate_number} ({self.name})" if self.name else self.plate_number


class Geozone(models.Model):
    name = models.CharField("Название", max_length=255)
    omnicomm_id = models.BigIntegerField("ID Omnicomm", null=True, blank=True, unique=True)
    omnicomm_uuid = models.UUIDField("UUID Omnicomm", null=True, blank=True, unique=True)
    is_active = models.BooleanField("Активна", default=True)
    is_used_in_matrix = models.BooleanField("Используется в матрице", default=True)
    created_at = models.DateTimeField("Создано", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        verbose_name = "Геозона"
        verbose_name_plural = "Геозоны"
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name


class VehicleMorningGeozone(models.Model):
    class Status(models.TextChoices):
        DETECTED = "detected", "Геозона определена"
        OUTSIDE = "outside", "Вне геозон"
        NO_DATA = "no_data", "Нет данных"

    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name="morning_geozones",
        verbose_name="ТС",
    )
    date = models.DateField("Дата")
    geozone = models.ForeignKey(
        Geozone,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="vehicle_morning_locations",
        verbose_name="Геозона",
    )
    status = models.CharField("Статус", max_length=20, choices=Status.choices, default=Status.NO_DATA)
    duration_seconds = models.PositiveIntegerField("Время нахождения, сек.", null=True, blank=True)
    entered_at = models.DateTimeField("Время входа", null=True, blank=True)
    exited_at = models.DateTimeField("Время выхода", null=True, blank=True)
    source = models.CharField("Источник", max_length=30, default="omnicomm")
    synced_at = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        verbose_name = "Утренняя геозона ТС"
        verbose_name_plural = "Утренние геозоны ТС"
        ordering = ("-date", "vehicle__plate_number")
        constraints = [
            models.UniqueConstraint(
                fields=("vehicle", "date"),
                name="fleet_vehiclemorninggeozone_vehicle_date_unique",
            )
        ]

    def __str__(self) -> str:
        zone_label = (
            self.geozone.name
            if self.status == self.Status.DETECTED and self.geozone_id
            else self.get_status_display()
        )
        return f"{self.vehicle} — {self.date}: {zone_label}"
