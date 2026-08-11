from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from apps.reports.services import build_matrix_report, build_problems_report


@login_required
def matrix_view(request):
    context = build_matrix_report(
        date_from_raw=request.GET.get("date_from"),
        date_to_raw=request.GET.get("date_to"),
    )
    context["active_page"] = "matrix"
    return render(request, "reports/matrix.html", context)


@login_required
def problems_view(request):
    context = build_problems_report(
        analysis_date_raw=request.GET.get("analysis_date"),
        days_raw=request.GET.get("days"),
    )
    context["active_page"] = "problems"
    return render(request, "reports/problems.html", context)
