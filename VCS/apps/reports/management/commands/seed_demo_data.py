from __future__ import annotations

from datetime import datetime, time, timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.fleet.models import Geozone, Vehicle, VehicleMorningGeozone
from apps.inspections.models import Inspection, InspectionFile

User = get_user_model()

GEOZONE_NAMES = [
    "Арктикгаз",
    "Роспан",
    "БПО",
    "ГПН-3",
    "ГПН-4",
]

VEHICLE_SEED = [
    ("А505МХ89", "Вахтовый автобус 01"),
    ("С473МЕ89", "Вахтовый автобус 02"),
    ("0350СК89", "Тягач 01"),
    ("0380СК89", "Тягач 02"),
    ("0482СК89", "Тягач 03"),
    ("0562СК89", "Самосвал 01"),
    ("0624СК89", "Самосвал 02"),
    ("0694СК89", "Самосвал 03"),
    ("0736СК89", "Самосвал 04"),
    ("0803СК89", "Самосвал 05"),
    ("0811СК89", "Автокран 01"),
    ("0837СК89", "Автокран 02"),
    ("0967СК89", "Топливозаправщик 01"),
    ("0994СК89", "Топливозаправщик 02"),
    ("0995СК89", "Топливозаправщик 03"),
    ("0996СК89", "Бортовой 01"),
    ("0997СК89", "Бортовой 02"),
    ("1161СМ89", "Бортовой 03"),
    ("1203СМ89", "Манипулятор 01"),
    ("1205СМ89", "Манипулятор 02"),
]


class Command(BaseCommand):
    help = "Создаёт демонстрационные данные для ЭНГС."

    @transaction.atomic
    def handle(self, *args, **options):
        today = timezone.localdate()
        geozones = self._seed_geozones()
        vehicles = self._seed_vehicles()
        self._seed_morning_geozones(vehicles, geozones, today)

        superuser = User.objects.filter(is_superuser=True).order_by("id").first()
        if superuser is None:
            self.stdout.write(
                self.style.WARNING(
                    "Суперпользователь не найден: проверки и файлы не созданы, "
                    "остальные демо-данные загружены."
                )
            )
            return

        self._seed_inspections(vehicles, superuser, today)
        self.stdout.write(self.style.SUCCESS("Демо-данные успешно обновлены."))

    def _seed_geozones(self) -> list[Geozone]:
        geozones = []
        for index, name in enumerate(GEOZONE_NAMES, start=1):
            geozone, _ = Geozone.objects.update_or_create(
                name=name,
                defaults={
                    "omnicomm_id": 1000 + index,
                    "is_active": True,
                    "is_used_in_matrix": True,
                },
            )
            geozones.append(geozone)

        self.stdout.write(self.style.SUCCESS(f"Геозоны: {len(geozones)}"))
        return geozones

    def _seed_vehicles(self) -> list[Vehicle]:
        vehicles = []
        for index, (plate_number, name) in enumerate(VEHICLE_SEED, start=1):
            vehicle, _ = Vehicle.objects.update_or_create(
                plate_number=plate_number,
                defaults={
                    "name": name,
                    "omnicomm_vehicle_id": 5000 + index,
                    "terminal_id": 8000 + index,
                    "is_active": True,
                    "is_subject_to_inspection": True,
                },
            )
            vehicles.append(vehicle)

        self.stdout.write(self.style.SUCCESS(f"ТС: {len(vehicles)}"))
        return vehicles

    def _seed_morning_geozones(
        self,
        vehicles: list[Vehicle],
        geozones: list[Geozone],
        today,
    ) -> None:
        for vehicle_index, vehicle in enumerate(vehicles):
            preferred_zone = geozones[vehicle_index % len(geozones)]

            for days_ago in range(60):
                current_date = today - timedelta(days=days_ago)
                selector = (vehicle_index + days_ago) % 17

                if selector == 0:
                    status = VehicleMorningGeozone.Status.NO_DATA
                    geozone = None
                    duration_seconds = None
                    entered_at = None
                    exited_at = None
                elif selector in {5, 11}:
                    status = VehicleMorningGeozone.Status.OUTSIDE
                    geozone = None
                    duration_seconds = 0
                    entered_at = None
                    exited_at = None
                else:
                    status = VehicleMorningGeozone.Status.DETECTED
                    geozone = preferred_zone if selector % 3 else geozones[(vehicle_index + days_ago) % len(geozones)]
                    start_hour = 6 + ((vehicle_index + days_ago) % 3)
                    enter_dt = timezone.make_aware(datetime.combine(current_date, time(hour=start_hour)))
                    duration_seconds = 1800 + ((vehicle_index * 97 + days_ago * 41) % 5400)
                    exit_dt = enter_dt + timedelta(seconds=duration_seconds)
                    entered_at = enter_dt
                    exited_at = exit_dt

                VehicleMorningGeozone.objects.update_or_create(
                    vehicle=vehicle,
                    date=current_date,
                    defaults={
                        "geozone": geozone,
                        "status": status,
                        "duration_seconds": duration_seconds,
                        "entered_at": entered_at,
                        "exited_at": exited_at,
                        "source": "omnicomm",
                    },
                )

        self.stdout.write(self.style.SUCCESS("Утренние геозоны: обновлены за 60 дней"))

    def _seed_inspections(self, vehicles: list[Vehicle], superuser: User, today) -> None:
        inspection_plan = {
            0: [7, 40],
            1: [1],
            2: [15],
            3: [29],
            4: [5],
            5: [30],
            6: [45],
            7: [60],
            8: [75],
            9: [90],
            10: [91],
            11: [120],
            12: [150],
            13: [200],
        }
        file_linked_slots = {(0, 7), (1, 1), (5, 30), (7, 60), (10, 91)}

        created_or_updated = 0
        created_files = 0

        for index, vehicle in enumerate(vehicles):
            for days_ago in inspection_plan.get(index, []):
                inspection_date = today - timedelta(days=days_ago)
                inspection, _ = Inspection.objects.update_or_create(
                    vehicle=vehicle,
                    inspection_date=inspection_date,
                    created_by=superuser,
                    defaults={
                        "notes": f"Демо-проверка для {vehicle.plate_number}",
                        "deleted_at": None,
                    },
                )
                created_or_updated += 1

                if (index, days_ago) in file_linked_slots:
                    InspectionFile.objects.update_or_create(
                        inspection=inspection,
                        file_name=f"{vehicle.plate_number}_{inspection_date:%Y%m%d}.mp4",
                        defaults={
                            "file_url": f"https://demo.engs.local/files/{vehicle.plate_number}_{inspection_date:%Y%m%d}.mp4",
                            "mime_type": "video/mp4",
                            "size_bytes": 157_286_400,
                            "uploaded_by": superuser,
                        },
                    )
                    created_files += 1

        self.stdout.write(self.style.SUCCESS(f"Проверки: {created_or_updated}"))
        self.stdout.write(self.style.SUCCESS(f"Файлы проверок: {created_files}"))
