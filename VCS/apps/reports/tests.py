from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.fleet.models import Vehicle
from apps.inspections.models import Inspection
from apps.reports.services import build_matrix_report

User = get_user_model()


class MatrixReportServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester")

    def _create_vehicle(self, plate_number: str) -> Vehicle:
        return Vehicle.objects.create(
            plate_number=plate_number,
            is_active=True,
            is_subject_to_inspection=True,
        )

    def _cell_tone_for(self, vehicle: Vehicle, target_date: date) -> str:
        report = build_matrix_report(
            date_from_raw=target_date.isoformat(),
            date_to_raw=target_date.isoformat(),
            today=target_date,
        )
        row = next(row for row in report["rows"] if row.vehicle.id == vehicle.id)
        return row.cells[0].tone

    def test_status_becomes_warning_on_day_30(self):
        vehicle = self._create_vehicle("А001АА89")
        Inspection.objects.create(
            vehicle=vehicle,
            inspection_date=date(2026, 1, 1),
            created_by=self.user,
        )

        tone = self._cell_tone_for(vehicle, date(2026, 1, 31))

        self.assertEqual(tone, "warning")

    def test_status_becomes_danger_after_90_days(self):
        vehicle = self._create_vehicle("А002АА89")
        Inspection.objects.create(
            vehicle=vehicle,
            inspection_date=date(2026, 1, 1),
            created_by=self.user,
        )

        tone = self._cell_tone_for(vehicle, date(2026, 4, 2))

        self.assertEqual(tone, "danger")

    def test_future_inspection_does_not_make_past_cell_green(self):
        vehicle = self._create_vehicle("А003АА89")
        Inspection.objects.create(
            vehicle=vehicle,
            inspection_date=date(2026, 2, 1),
            created_by=self.user,
        )

        tone = self._cell_tone_for(vehicle, date(2026, 1, 15))

        self.assertEqual(tone, "danger")

    def test_vehicle_without_inspections_is_danger(self):
        vehicle = self._create_vehicle("А004АА89")

        tone = self._cell_tone_for(vehicle, date(2026, 1, 15))

        self.assertEqual(tone, "danger")
