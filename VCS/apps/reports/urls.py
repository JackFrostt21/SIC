from django.urls import path

from apps.reports.views import matrix_view, problems_view



app_name = "reports"

urlpatterns = [
    path("matrix/", matrix_view, name="matrix"),
    path("problems/", problems_view, name="problems"),
]
