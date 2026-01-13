# 123удалить!!!
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.db.models import Q

from app.lightning.models.lightning_models import Lightning
from app.lightning.models.lightning_data_models import LightningRead, LightningTest
from app.bot.models import TelegramUser


@staff_member_required
def lightning_discrepancy_check_view(request):
    """
    Проверка расхождений: сотрудники, которые прошли тест (complete=True),
    но у них нет записи о чтении или is_read=False
    """

    # Фильтр по молнии
    selected_lightning_id = request.GET.get("lightning_id")
    selected_lightning = None
    discrepancies = []

    # Получаем все молнии для выбора
    lightnings = (
        Lightning.objects.filter(is_draft=False)
        .only("id", "name")
        .order_by("-created_at")
    )

    if selected_lightning_id and selected_lightning_id.isdigit():
        selected_lightning = lightnings.filter(id=int(selected_lightning_id)).first()

    if selected_lightning:
        # Получаем все успешно пройденные тесты для выбранной молнии
        completed_tests = LightningTest.objects.filter(
            lightning=selected_lightning,
            complete=True,
            user__state=TelegramUser.STATE_ACTIVE,
        ).select_related("user", "user__department", "user__job_title")

        for test in completed_tests:
            # Проверяем наличие записи о чтении
            try:
                read_record = LightningRead.objects.get(
                    user=test.user, lightning=test.lightning
                )
                # Если запись есть, но is_read=False - это расхождение
                if not read_record.is_read:
                    discrepancies.append(
                        {
                            "user": test.user,
                            "test": test,
                            "read_record": read_record,
                            "status": "not_read",
                            "status_text": 'Тест пройден, но отмечен как "не прочитано"',
                        }
                    )
            except LightningRead.DoesNotExist:
                # Если записи вообще нет - это расхождение
                discrepancies.append(
                    {
                        "user": test.user,
                        "test": test,
                        "read_record": None,
                        "status": "no_record",
                        "status_text": "Тест пройден, но нет записи о чтении",
                    }
                )

    # Пагинация
    paginator = Paginator(discrepancies, 25)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "lightning_discrepancy_check.html",
        {
            "lightnings": lightnings,
            "selected_lightning": selected_lightning,
            "discrepancies": page_obj.object_list,
            "page_obj": page_obj,
            "total_discrepancies": len(discrepancies),
        },
    )
