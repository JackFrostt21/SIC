from jet.dashboard.modules import DashboardModule
from django.template.loader import render_to_string
from django.utils.translation import gettext as _


def fixed_digits(num_obj, digits=0):
    return f"{num_obj:.{digits}f}"


class TotalUserWidget(DashboardModule):
    title = _('Total Users')

    collapsible = True

    contrast = False

    # def render(self, request=None):
    #     try:
    #         total_result = []
    #         total = AnswerOption.objects.all().annotate(quantity_is_correct=Count("is_correct")).filter(
    #             is_correct=True).annotate(
    #             quantity_is_not_correct=Count("is_correct") - AnswerOption.objects.filter(is_correct=False).count()
    #         )
    #
    #         for t in total:
    #             total_result.append(t)
    #
    #         context = {
    #             'total_orders': total_result,
    #
    #         }
    #         return render_to_string('widgets/total_orders.html', context)
    #     except Exception as e:
    #         print(e)

    user_count = []  # Общее число пользователей прошедших тесты.
    total_users = []  # Количество пользователей в зависимости от оценок.

    def render(self, request=None):
        try:
            context = {
                'user_count': 123,
                'total_users': [
                    {'users': 119, 'rang': 'Оценка 1'},
                    {'users': 12, 'rang': 'Оценка 2'},
                    {'users': 133, 'rang': 'Оценка 3'},
                    {'users': 50, 'rang': 'Оценка 4'},
                    {'users': 44, 'rang': 'Оценка 5'},
                    {'users': 156, 'rang': 'Оценка 6'}]
            }
            return render_to_string('widgets/total_user.html', context)
        except Exception as e:
            print(e)


class TotalUserInfoWidget(DashboardModule):
    title = _('Total User Info')
    collapsible = True
    contrast = False

    user_count = []  # Общее число пользователей прошедших тесты.
    total_users = []  # Количество пользователей в зависимости от оценок.

    def render(self, request=None):
        try:
            context = {
                'item_quantity': [
                    {'users': 119, 'rang': 'Оценка 1'},
                    {'users': 12, 'rang': 'Оценка 2'},
                    {'users': 133, 'rang': 'Оценка 3'},
                    {'users': 50, 'rang': 'Оценка 4'},
                    {'users': 44, 'rang': 'Оценка 5'},
                    {'users': 156, 'rang': 'Оценка 6'}],
                'item_weight': [
                    {'users': 119, 'rang': 'Оценка 1'},
                    {'users': 12, 'rang': 'Оценка 2'},
                    {'users': 133, 'rang': 'Оценка 3'},
                    {'users': 50, 'rang': 'Оценка 4'},
                    {'users': 44, 'rang': 'Оценка 5'},
                    {'users': 156, 'rang': 'Оценка 6'}]
            }
            return render_to_string('widgets/total_user_info.html', context)
        except Exception as e:
            print(e)
