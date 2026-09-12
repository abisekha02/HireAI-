from django.contrib import admin

from .models import Evaluation


@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    list_display = ("interview", "overall_score", "recommendation", "reviewed_by_human")
    list_filter = ("recommendation", "reviewed_by_human")
