from django.conf import settings
from django.db import models

from apps.jobs.models import JobPosting
from apps.resumes.models import Resume


class Application(models.Model):
    class Stage(models.TextChoices):
        APPLIED = "applied", "Applied"
        SCREENING = "screening", "Screening"
        INTERVIEW = "interview", "Interview"
        OFFER = "offer", "Offer"
        REJECTED = "rejected", "Rejected"
        HIRED = "hired", "Hired"

    job = models.ForeignKey(JobPosting, on_delete=models.CASCADE, related_name="applications")
    candidate = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="applications"
    )
    resume = models.ForeignKey(Resume, on_delete=models.SET_NULL, null=True, related_name="applications")
    stage = models.CharField(max_length=16, choices=Stage.choices, default=Stage.APPLIED)
    match_score = models.FloatField(null=True, blank=True, help_text="Cached semantic match score 0-100")
    cover_note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ["job", "candidate"]

    def __str__(self):
        return f"{self.candidate} -> {self.job} [{self.stage}]"
