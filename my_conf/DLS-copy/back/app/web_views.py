from app.learning_app.views import (
    TrainingCourseViewSet,
    CourseTopicViewSet,
    CourseDirectionViewSet,
    TopicQuestionViewSet,
    AnswerOptionViewSet,
    NewsBlockViewSet,
    TagCourseViewSet,
    CertificateViewSet,
    RatingTrainingCourseViewSet,
    CourseDeadlineViewSet,
)
from app.bot.views import (
    TelegramUserViewSet,
    TelegramGroupViewSet,
    CustomUserViewSet,
    UserReadViewSet,
    UserTestViewSet,
    UserRatingViewSet,
)
from app.organization.views import (
    JobTitleViewSet,
    DepartmentViewSet,
    CompanyViewSet,
    SettingsBotViewSet,
)


class ReadOnlyMixin:
    """Миксин для ограничения методов только до GET."""

    http_method_names = ["get"]


class WebTelegramUserViewSet(ReadOnlyMixin, TelegramUserViewSet):
    pass


class WebTelegramGroupViewSet(ReadOnlyMixin, TelegramGroupViewSet):
    pass


class WebCustomUserViewSet(ReadOnlyMixin, CustomUserViewSet):
    pass


class WebUserReadViewSet(ReadOnlyMixin, UserReadViewSet):
    pass


class WebUserTestViewSet(ReadOnlyMixin, UserTestViewSet):
    pass


class WebTrainingCourseViewSet(ReadOnlyMixin, TrainingCourseViewSet):
    pass


class WebCourseTopicViewSet(ReadOnlyMixin, CourseTopicViewSet):
    pass


class WebCourseDirectionViewSet(ReadOnlyMixin, CourseDirectionViewSet):
    pass


class WebTopicQuestionViewSet(ReadOnlyMixin, TopicQuestionViewSet):
    pass


class WebAnswerOptionViewSet(ReadOnlyMixin, AnswerOptionViewSet):
    pass


class WebNewsBlockViewSet(ReadOnlyMixin, NewsBlockViewSet):
    pass


class WebTagCourseViewSet(ReadOnlyMixin, TagCourseViewSet):
    pass


class WebCertificateViewSet(ReadOnlyMixin, CertificateViewSet):
    pass


class WebRatingTrainingCourseViewSet(ReadOnlyMixin, RatingTrainingCourseViewSet):
    pass


class WebCourseDeadlineViewSet(ReadOnlyMixin, CourseDeadlineViewSet):
    pass


class WebJobTitleViewSet(ReadOnlyMixin, JobTitleViewSet):
    pass


class WebDepartmentViewSet(ReadOnlyMixin, DepartmentViewSet):
    pass


class WebCompanyViewSet(ReadOnlyMixin, CompanyViewSet):
    pass


class WebSettingsBotViewSet(ReadOnlyMixin, SettingsBotViewSet):
    pass


class WebUserRatingViewSet(ReadOnlyMixin, UserRatingViewSet):
    pass
