from django.db import models
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from rest_framework.response import Response

from app.core.abstract_models import BaseModel


class TrainingCourse(BaseModel):
    title = models.CharField(max_length=400, null=True, blank=True, verbose_name=_("title"))
    description = models.TextField(null=True, blank=True, verbose_name=_("description"))

    user = models.ManyToManyField("bot.TelegramUser", null=True, blank=True)

    def __str__(self):
        if self.title:
            name = self.title
        else:
            name = self.id
        return name

    class Meta:
        verbose_name = _("TrainingCourse")
        verbose_name_plural = _("TrainingCourses")
        ordering = ['id']


class CourseTopic(BaseModel):
    title = models.CharField(max_length=500, null=True, blank=True, verbose_name=_('title'))
    description = models.TextField(null=True, blank=True, verbose_name=_('description'))
    main_text = models.TextField(null=True, blank=True, verbose_name=_('main_text'))
    training_course = models.ForeignKey(TrainingCourse, related_name='course_topics', on_delete=models.DO_NOTHING,
                                        null=True,
                                        blank=True, verbose_name=_("training_course"))


    class Meta:
        verbose_name = _("CourseTopic")
        verbose_name_plural = _("CourseTopics")
        ordering = ['training_course', 'id']

    def __str__(self):
        if self.title:
            name = f'{self.training_course} | {self.title}'
        else:
            name = self.id
        return name

    def more_info(self):
        return mark_safe(f'''                                                   
<a href='/educational_module/coursetopic/{self.id}/change/'> Перейти для редактирования: {self.id} </a>
    ''')

    more_info.short_description = _('more_info')


class Subtopic(BaseModel):
    title = models.CharField(max_length=500, null=True, blank=True, verbose_name=_('title'))
    description = models.TextField(null=True, blank=True, verbose_name=_('description'))
    main_text = models.TextField(null=True, blank=True, verbose_name=_('main_text'))
    course_topic = models.ForeignKey(CourseTopic, related_name='topic_subtopic', on_delete=models.DO_NOTHING,
                                     null=True,
                                     blank=True, verbose_name=_("course_topic"))

    class Meta:
        verbose_name = _("Subtopic")
        verbose_name_plural = _("Subtopics")
        ordering = ['course_topic', 'id']

    def __str__(self):
        if self.title:
            name = f'{self.course_topic} | {self.title}'
        else:
            name = self.id
        return name


class TopicQuestion(BaseModel):
    title = models.CharField(max_length=500, null=True, blank=True, verbose_name=_("title"))
    topic = models.ForeignKey(CourseTopic, on_delete=models.DO_NOTHING, null=True, blank=True,
                              related_name="topic_questions", verbose_name=_("topic"))
    training = models.ForeignKey(TrainingCourse, on_delete=models.DO_NOTHING, null=True, blank=True,
                               verbose_name=_("course"))
    order = models.PositiveSmallIntegerField(default=1)

    class Meta:
        verbose_name = _("TopicQuestion")
        verbose_name_plural = _("TopicQuestions")
        ordering = ["topic"]

    def __str__(self):
        if self.title:
            name = f'{self.topic} | {self.title}'
        else:
            name = self.id
        return name

    def more_info(self):
        return mark_safe(f'''                                                   
<a href='/educational_module/topicquestion/{self.id}/change/'> Перейти для редактирования: {self.id} </a>
        ''')

    more_info.short_description = _('more_info')


class AnswerOption(BaseModel):
    topic_question = models.ForeignKey(TopicQuestion, on_delete=models.DO_NOTHING, null=True, blank=True,
                                       verbose_name=_("topic_question"),
                                       related_name="answer_options")
    number = models.CharField(max_length=5, null=True, blank=True, verbose_name=_("number"))
    text = models.TextField(null=True, blank=True, verbose_name=_("text"))
    is_correct = models.BooleanField(default=False, verbose_name=_("is_correct"))

    class Meta:
        verbose_name = _("AnswerOption")
        verbose_name_plural = _("AnswerOptions")
        ordering = ["id", 'number']

    def __str__(self):
        if self.topic_question:
            name = f'{self.topic_question} | {self.number}'
        else:
            name = self.id
        return name
