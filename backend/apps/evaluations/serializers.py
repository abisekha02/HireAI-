from rest_framework import serializers

from .models import Evaluation


class EvaluationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evaluation
        fields = [
            "id", "interview", "overall_score", "recommendation",
            "per_question_scores", "strengths", "weaknesses", "summary",
            "reviewed_by_human", "human_override_notes", "created_at",
        ]
        read_only_fields = [
            "id", "interview", "overall_score", "recommendation",
            "per_question_scores", "strengths", "weaknesses", "summary", "created_at",
        ]
