from django.contrib import admin
from django.urls import path, include, reverse_lazy
from django.conf import settings
from django.conf.urls.static import static
from app.lightning.views.statistics import (
    lightning_statistics_view,
    lightnings_vs_users_statistics_view,
    lightnings_summary_by_departments_view,
)
from app.lightning.views.multisend import lightning_multisend_view

# 123удалить!!!
from app.lightning.views.discrepancy_check import lightning_discrepancy_check_view

# 123удалить!!!
from django.views.generic.base import RedirectView

urlpatterns = [
    # редирект с корня на админку
    path("", RedirectView.as_view(url=reverse_lazy("admin:index"), permanent=False)),
    path(
        "admin/lightnings/multisend/",
        lightning_multisend_view,
        name="admin-lightning-multisend",
    ),
    path(
        "admin/statistics/",
        lightning_statistics_view,
        name="admin-statistics",
    ),
    path(
        "admin/lightnings_vs_users_statistics/",
        lightnings_vs_users_statistics_view,
        name="admin-lightnings-vs-users",
    ),
    path(
        "admin/lightnings_summary_by_departments/",
        lightnings_summary_by_departments_view,
        name="admin-lightnings-summary-by-departments",
    ),
    # 123удалить!!!
    path(
        "admin/lightnings/discrepancy-check/",
        lightning_discrepancy_check_view,
        name="admin-lightning-discrepancy-check",
    ),
    # 123удалить!!!
    path("admin/", admin.site.urls),
    path(
        "ckeditor5/", include("django_ckeditor_5.urls"), name="ck_editor_5_upload_file"
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
