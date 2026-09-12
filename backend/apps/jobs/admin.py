from django.contrib import admin

from .models import JobPosting


@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    list_display = ("title", "recruiter", "status", "employment_type", "created_at")
    list_filter = ("status", "employment_type", "is_remote")
    search_fields = ("title", "description")
