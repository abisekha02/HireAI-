from django.contrib import admin

from .models import Interview, Question


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 0


@admin.register(Interview)
class InterviewAdmin(admin.ModelAdmin):
    list_display = ("application", "status", "difficulty", "created_at")
    list_filter = ("status", "difficulty")
    inlines = [QuestionInline]
