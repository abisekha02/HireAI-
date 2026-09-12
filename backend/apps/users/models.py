from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user with a role used for RBAC across the platform."""

    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        RECRUITER = "recruiter", "Recruiter"
        CANDIDATE = "candidate", "Candidate"
        INTERVIEWER = "interviewer", "Interviewer"

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CANDIDATE)
    company_name = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=32, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return f"{self.email} ({self.role})"

    @property
    def is_recruiter(self):
        return self.role in (self.Role.RECRUITER, self.Role.ADMIN)

    @property
    def is_candidate(self):
        return self.role == self.Role.CANDIDATE
