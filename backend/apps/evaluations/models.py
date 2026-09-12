from django.db import models

from apps.interviews.models import Interview


class Evaluation(models.Model):
    interview = models.OneToOneField(Interview, on_delete=models.CASCADE, related_name="evaluation")
    overall_score = models.FloatField(help_text="0-100 automated composite score")
    recommendation = models.CharField(
        max_length=20,
        choices=[
            ("strong_hire", "Strong hire"), ("hire", "Hire"),
            ("borderline", "Borderline"), ("no_hire", "No hire"),
        ],
    )
    per_question_scores = models.JSONField(default=list, help_text="[{question_id, score, feedback}]")
    strengths = models.JSONField(default=list)
    weaknesses = models.JSONField(default=list)
    summary = models.TextField(blank=True)
    reviewed_by_human = models.BooleanField(default=False)
    human_override_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Evaluation({self.interview_id}, {self.overall_score})"
