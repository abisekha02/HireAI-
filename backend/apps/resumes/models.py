from django.conf import settings
from django.db import models
from pgvector.django import VectorField


def resume_upload_path(instance, filename):
    return f"resumes/{instance.candidate_id}/{filename}"


class Resume(models.Model):
    class ParseStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        PARSED = "parsed", "Parsed"
        FAILED = "failed", "Failed"

    candidate = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="resumes"
    )
    file = models.FileField(upload_to=resume_upload_path)
    raw_text = models.TextField(blank=True)

    # Structured data extracted by the LLM (skills, experience, education, etc.)
    parsed_data = models.JSONField(null=True, blank=True)
    parse_status = models.CharField(max_length=16, choices=ParseStatus.choices, default=ParseStatus.PENDING)
    parse_error = models.TextField(blank=True)

    # Embedding of the resume content for semantic job matching / RAG.
    embedding = VectorField(dimensions=1536, null=True, blank=True)

    is_primary = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Resume({self.candidate_id}, {self.parse_status})"
