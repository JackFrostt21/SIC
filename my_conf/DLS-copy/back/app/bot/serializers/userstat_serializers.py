from rest_framework import serializers


class CourseStatSerializer(serializers.Serializer):
    """
    Сериализатор для детальной статистики по одному курсу.
    """

    course_id = serializers.IntegerField()
    course_title = serializers.CharField()
    total_topics = serializers.IntegerField()
    read_topics = serializers.IntegerField()
    reading_progress_percent = serializers.FloatField()
    test_status = serializers.CharField()
    is_completed = serializers.BooleanField()


class UserProgressSerializer(serializers.Serializer):
    """
    Сериализатор для общей и детальной статистики пользователя.
    """

    total_courses = serializers.IntegerField()
    completed_courses = serializers.IntegerField()
    total_topics = serializers.IntegerField()
    read_topics = serializers.IntegerField()
    overall_progress_topics = serializers.FloatField()
    total_tests = serializers.IntegerField()
    passed_tests = serializers.IntegerField()
    failed_tests = serializers.IntegerField()
    overall_progress = serializers.FloatField()
    place = serializers.IntegerField()
    points = serializers.IntegerField()


class UserOverallStatSerializer(serializers.Serializer):
    summary = UserProgressSerializer()
    courses_details = CourseStatSerializer(many=True)
