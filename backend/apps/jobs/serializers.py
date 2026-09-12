from rest_framework import serializers

from .models import JobPosting


class JobPostingSerializer(serializers.ModelSerializer):
    recruiter_name = serializers.CharField(source="recruiter.get_full_name", read_only=True)

    class Meta:
        model = JobPosting
        fields = [
            "id", "recruiter", "recruiter_name", "title", "description",
            "requirements", "location", "is_remote", "employment_type",
            "salary_min", "salary_max", "status", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "recruiter", "created_at", "updated_at"]
