from rest_framework import serializers

from .models import Resume


class ResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resume
        fields = [
            "id", "candidate", "file", "parsed_data", "parse_status",
            "parse_error", "is_primary", "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "candidate", "parsed_data", "parse_status",
            "parse_error", "created_at", "updated_at",
        ]
