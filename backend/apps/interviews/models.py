from django.db import models

from apps.applications.models import Application


class Interview(models.Model):
    class Status(models.TextChoices):
        GENERATED = "generated", "Generated"
        IN_PROGRESS = "in_progress", "In progress"
        COMPLETED = "completed", "Completed"
        EVALUATED = "evaluated", "Evaluated"

    application = models.OneToOneField(
        Application, on_delete=models.CASCADE, related_name="interview"
    )
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.GENERATED)
    difficulty = models.CharField(
        max_length=16,
        choices=[("junior", "Junior"), ("mid", "Mid"), ("senior", "Senior")],
        default="mid",
    )
    focus_areas = models.JSONField(default=list, blank=True, help_text="Skills this interview targets")
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Interview({self.application_id}, {self.status})"


class Question(models.Model):
    class Type(models.TextChoices):
        CODING = "coding", "Coding"
        SYSTEM_DESIGN = "system_design", "System design"
        CONCEPTUAL = "conceptual", "Conceptual"
        BEHAVIORAL = "behavioral", "Behavioral"

    interview = models.ForeignKey(Interview, on_delete=models.CASCADE, related_name="questions")
    order = models.PositiveSmallIntegerField()
    type = models.CharField(max_length=16, choices=Type.choices)
    prompt = models.TextField()
    rubric = models.JSONField(
        default=dict, blank=True, help_text="LLM-generated grading rubric: key points, ideal answer"
    )
    candidate_answer = models.TextField(blank=True)
    answered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"Q{self.order} ({self.type})"
