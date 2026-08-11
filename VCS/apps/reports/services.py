from __future__ import annotations

from calendar import monthrange
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date, timedelta

from django.db.models import Prefetch
from django.utils import timezone

from apps.fleet.models import Vehicle, VehicleMorningGeozone
from apps.inspections.models import Inspection, InspectionFile

MAX_MATRIX_DAYS = 92
DEFAULT_PROBLEM_DAYS = 90
MAX_PROBLEM_DAYS = 365


@dataclass(slots=True)
class MatrixCell:
    date: date
    label: str
    tone: str
    css_class: str
    has_inspection: bool
    file_url: str | None


@dataclass(slots=True)
class MatrixRow:
    vehicle: Vehicle
    cells: list[MatrixCell]


@dataclass(slots=True)
class ProblemVehicleRow:
    vehicle: Vehicle
    tone: str
    tone_label: str
    badge_class: str
    last_inspection_date: date | None
    days_without_inspection: int | None
    primary_geozone: str


def _today() -> date:
    return timezone.localdate()


def _parse_date(raw_value: str | None) -> date | None:
    if not raw_value:
        return None

    try:
        return date.fromisoformat(raw_value)
    except ValueError:
        return None


def _month_bounds(anchor: date) -> tuple[date, date]:
    month_start = anchor.replace(day=1)
    month_end = anchor.replace(day=monthrange(anchor.year, anchor.month)[1])
    return month_start, month_end


def _parse_matrix_range(
    date_from_raw: str | None,
    date_to_raw: str | None,
    *,
    today: date | None = None,
) -> tuple[date, date]:
    today = today or _today()
    default_from, default_to = _month_bounds(today)

    date_from = _parse_date(date_from_raw) or default_from
    date_to = _parse_date(date_to_raw) or default_to

    if date_from > date_to:
        date_from, date_to = date_to, date_from

    max_end = date_from + timedelta(days=MAX_MATRIX_DAYS - 1)
    if date_to > max_end:
        date_to = max_end

    return date_from, date_to


def _parse_problem_params(
    analysis_date_raw: str | None,
    days_raw: str | None,
    *,
    today: date | None = None,
) -> tuple[date, int]:
    today = today or _today()
    analysis_date = _parse_date(analysis_date_raw) or today

    try:
        days = int(days_raw) if days_raw else DEFAULT_PROBLEM_DAYS
    except ValueError:
        days = DEFAULT_PROBLEM_DAYS

    days = max(1, min(days, MAX_PROBLEM_DAYS))
    return analysis_date, days


def _date_range(date_from: date, date_to: date) -> list[date]:
    days = (date_to - date_from).days + 1
    return [date_from + timedelta(days=offset) for offset in range(days)]


def _inspection_tone(
    last_inspection_date: date | None,
    current_date: date,
) -> tuple[str, str]:
    if last_inspection_date is None:
        return "danger", "Красный"

    days_since = (current_date - last_inspection_date).days
    if days_since < 30:
        return "good", "Зелёный"
    if days_since <= 90:
        return "warning", "Жёлтый"
    return "danger", "Красный"


def _tone_css_class(tone: str) -> str:
    return {
        "good": "cell-good",
        "warning": "cell-warning",
        "danger": "cell-danger",
    }[tone]


def _tone_badge_class(tone: str) -> str:
    return {
        "good": "badge-good",
        "warning": "badge-warning",
        "danger": "badge-danger",
    }[tone]


def _tone_label(tone: str) -> str:
    return {
        "good": "Актуально",
        "warning": "Требует внимания",
        "danger": "Просрочено",
    }[tone]


def _morning_geozone_label(record: VehicleMorningGeozone | None) -> str:
    if record is None or record.status == VehicleMorningGeozone.Status.NO_DATA:
        return "—"
    if record.status == VehicleMorningGeozone.Status.OUTSIDE:
        return "Вне геозон"
    if record.geozone_id:
        return record.geozone.name
    return "—"


def build_matrix_report(
    *,
    date_from_raw: str | None,
    date_to_raw: str | None,
    today: date | None = None,
) -> dict:
    today = today or _today()
    date_from, date_to = _parse_matrix_range(date_from_raw, date_to_raw, today=today)
    dates = _date_range(date_from, date_to)

    vehicles = list(
        Vehicle.objects.filter(
            is_active=True,
            is_subject_to_inspection=True,
        ).order_by("plate_number")
    )
    vehicle_ids = [vehicle.id for vehicle in vehicles]

    inspections = list(
        Inspection.objects.filter(
            vehicle_id__in=vehicle_ids,
            inspection_date__lte=date_to,
            deleted_at__isnull=True,
        )
        .select_related("vehicle", "created_by")
        .prefetch_related(Prefetch("files", queryset=InspectionFile.objects.order_by("id")))
        .order_by("vehicle_id", "inspection_date", "created_at", "id")
    )

    morning_geozones = list(
        VehicleMorningGeozone.objects.filter(
            vehicle_id__in=vehicle_ids,
            date__range=(date_from, date_to),
        )
        .select_related("geozone", "vehicle")
        .order_by("vehicle_id", "date")
    )

    inspections_by_vehicle: dict[int, list[Inspection]] = defaultdict(list)
    inspection_links_by_day: dict[tuple[int, date], str | None] = {}
    for inspection in inspections:
        inspections_by_vehicle[inspection.vehicle_id].append(inspection)

        day_key = (inspection.vehicle_id, inspection.inspection_date)
        link = next((file.file_url for file in inspection.files.all() if file.file_url), None)
        if day_key not in inspection_links_by_day or (
            inspection_links_by_day[day_key] is None and link
        ):
            inspection_links_by_day[day_key] = link

    morning_by_vehicle_day = {
        (record.vehicle_id, record.date): record
        for record in morning_geozones
    }

    rows: list[MatrixRow] = []
    summary = {"good": 0, "warning": 0, "danger": 0}

    for vehicle in vehicles:
        vehicle_inspections = inspections_by_vehicle.get(vehicle.id, [])
        pointer = 0
        last_inspection_date: date | None = None
        cells: list[MatrixCell] = []

        for current_date in dates:
            while (
                pointer < len(vehicle_inspections)
                and vehicle_inspections[pointer].inspection_date <= current_date
            ):
                last_inspection_date = vehicle_inspections[pointer].inspection_date
                pointer += 1

            tone, _ = _inspection_tone(last_inspection_date, current_date)
            morning_record = morning_by_vehicle_day.get((vehicle.id, current_date))
            day_key = (vehicle.id, current_date)
            file_url = inspection_links_by_day.get(day_key)

            cells.append(
                MatrixCell(
                    date=current_date,
                    label=_morning_geozone_label(morning_record),
                    tone=tone,
                    css_class=_tone_css_class(tone),
                    has_inspection=day_key in inspection_links_by_day,
                    file_url=file_url,
                )
            )

        final_tone = cells[-1].tone if cells else "danger"
        summary[final_tone] += 1
        rows.append(MatrixRow(vehicle=vehicle, cells=cells))

    return {
        "date_from": date_from,
        "date_to": date_to,
        "dates": dates,
        "rows": rows,
        "summary_total": len(vehicles),
        "summary_good": summary["good"],
        "summary_warning": summary["warning"],
        "summary_danger": summary["danger"],
        "max_matrix_days": MAX_MATRIX_DAYS,
    }


def build_problems_report(
    *,
    analysis_date_raw: str | None,
    days_raw: str | None,
    today: date | None = None,
) -> dict:
    today = today or _today()
    analysis_date, days = _parse_problem_params(
        analysis_date_raw,
        days_raw,
        today=today,
    )
    period_start = analysis_date - timedelta(days=days - 1)

    vehicles = list(
        Vehicle.objects.filter(
            is_active=True,
            is_subject_to_inspection=True,
        ).order_by("plate_number")
    )
    vehicle_ids = [vehicle.id for vehicle in vehicles]

    inspections = list(
        Inspection.objects.filter(
            vehicle_id__in=vehicle_ids,
            inspection_date__lte=analysis_date,
            deleted_at__isnull=True,
        )
        .select_related("vehicle")
        .order_by("vehicle_id", "inspection_date", "created_at", "id")
    )

    geozone_records = list(
        VehicleMorningGeozone.objects.filter(
            vehicle_id__in=vehicle_ids,
            date__range=(period_start, analysis_date),
            status=VehicleMorningGeozone.Status.DETECTED,
            geozone__isnull=False,
        )
        .select_related("geozone")
        .order_by("vehicle_id", "date")
    )

    latest_inspection_by_vehicle: dict[int, date] = {}
    for inspection in inspections:
        latest_inspection_by_vehicle[inspection.vehicle_id] = inspection.inspection_date

    geozone_counter_by_vehicle: dict[int, Counter[str]] = defaultdict(Counter)
    for record in geozone_records:
        geozone_counter_by_vehicle[record.vehicle_id][record.geozone.name] += 1

    grouped_rows: dict[str, list[ProblemVehicleRow]] = defaultdict(list)

    for vehicle in vehicles:
        last_inspection_date = latest_inspection_by_vehicle.get(vehicle.id)
        tone, tone_label = _inspection_tone(last_inspection_date, analysis_date)
        if tone == "good":
            continue

        primary_geozone = "Не определена"
        zone_counter = geozone_counter_by_vehicle.get(vehicle.id)
        if zone_counter:
            primary_geozone = zone_counter.most_common(1)[0][0]

        grouped_rows[primary_geozone].append(
            ProblemVehicleRow(
                vehicle=vehicle,
                tone=tone,
                tone_label=tone_label,
                badge_class=_tone_badge_class(tone),
                last_inspection_date=last_inspection_date,
                days_without_inspection=(
                    (analysis_date - last_inspection_date).days
                    if last_inspection_date is not None
                    else None
                ),
                primary_geozone=primary_geozone,
            )
        )

    groups = []
    for geozone_name in sorted(grouped_rows):
        rows = sorted(
            grouped_rows[geozone_name],
            key=lambda row: (row.tone != "danger", row.vehicle.plate_number),
        )
        groups.append(
            {
                "name": geozone_name,
                "count": len(rows),
                "rows": rows,
            }
        )

    return {
        "analysis_date": analysis_date,
        "days": days,
        "period_start": period_start,
        "groups": groups,
        "problem_count": sum(group["count"] for group in groups),
    }
