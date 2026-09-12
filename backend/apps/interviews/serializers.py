from rest_framework import serializers

from .models import Interview, Question


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ["id", "order", "type", "prompt", "candidate_answer", "answered_at"]
        # rubric intentionally excluded from candidate-facing responses


class QuestionAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ["candidate_answer"]


class InterviewSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Interview
        fields = [
            "id", "application", "status", "difficulty", "focus_areas",
            "started_at", "completed_at", "created_at", "questions",
        ]
        read_only_fields = fields
