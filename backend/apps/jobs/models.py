from django.conf import settings
from django.db import models
from pgvector.django import VectorField


class JobPosting(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        OPEN = "open", "Open"
        CLOSED = "closed", "Closed"

    recruiter = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="job_postings"
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    requirements = models.TextField(help_text="Plain-text list of required skills/experience")
    location = models.CharField(max_length=255, blank=True)
    is_remote = models.BooleanField(default=False)
    employment_type = models.CharField(
        max_length=32,
        choices=[
            ("full_time", "Full-time"), ("part_time", "Part-time"),
            ("contract", "Contract"), ("internship", "Internship"),
        ],
        default="full_time",
    )
    salary_min = models.PositiveIntegerField(null=True, blank=True)
    salary_max = models.PositiveIntegerField(null=True, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT)

    # Semantic search: embedding of title+description+requirements, kept in
    # sync via a signal / service call whenever the posting is saved.
    embedding = VectorField(dimensions=1536, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    @property
    def matching_text(self) -> str:
        return f"{self.title}\n{self.description}\n{self.requirements}"
