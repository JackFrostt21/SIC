from django.utils.translation import gettext_lazy as _
from jet.dashboard import modules
from jet.dashboard.dashboard import Dashboard
from jet.dashboard.modules import ModelList, AppList, RecentActions

# from app.widgets import NumberOfCourseWidget, TotalUserInfoWidget, AverageScoreWidget


class CustomDashboard(Dashboard):
    """
    Custom dashboard for the Django Jet admin interface.
    """
    columns = 2

    def init_with_context(self, context):
        """
        Initialize the dashboard with the context.
        """

        # self.available_children.append(NumberOfCourseWidget)
        # self.available_children.append(AverageScoreWidget)
        # self.available_children.append(TotalUserInfoWidget)

        """
        Standard.
        """