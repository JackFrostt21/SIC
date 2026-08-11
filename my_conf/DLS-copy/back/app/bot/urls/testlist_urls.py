from django.urls import path
from ..views.testlist_views import UserTestListView

urlpatterns = [
    path(
        "users/<int:telegram_user_id>/tests/",
        UserTestListView.as_view(),
        name="user_test_list",
    ),
]