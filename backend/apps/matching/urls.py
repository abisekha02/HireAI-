from django.urls import path

from .views import (
    CandidateJobMatchesView,
    JobCandidateMatchesView,
    MatchExplanationView,
)

urlpatterns = [
    path("jobs/<int:job_id>/candidates/", JobCandidateMatchesView.as_view(), name="job-candidates"),
    path("candidates/me/jobs/", CandidateJobMatchesView.as_view(), name="candidate-jobs"),
    path("explain/", MatchExplanationView.as_view(), name="match-explain"),
]
