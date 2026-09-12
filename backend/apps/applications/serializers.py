from rest_framework import serializers

from .models import Application


class ApplicationSerializer(serializers.ModelSerializer):
    job_title = serializers.CharField(source="job.title", read_only=True)
    candidate_name = serializers.CharField(source="candidate.get_full_name", read_only=True)

    class Meta:
        model = Application
        fields = [
            "id", "job", "job_title", "candidate", "candidate_name", "resume",
            "stage", "match_score", "cover_note", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "candidate", "match_score", "created_at", "updated_at"]
