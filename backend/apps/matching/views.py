from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.jobs.models import JobPosting
from apps.jobs.serializers import JobPostingSerializer
from apps.resumes.models import Resume
from apps.resumes.serializers import ResumeSerializer

from .services import (
    build_match_explanation,
    match_candidates_to_job,
    match_jobs_to_candidate,
    match_score,
)


class JobCandidateMatchesView(APIView):
    """GET /api/matching/jobs/<job_id>/candidates/ - top candidates for a job."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, job_id):
        job = JobPosting.objects.get(id=job_id, recruiter=request.user)
        resumes = match_candidates_to_job(job)
        results = [
            {
                "resume": ResumeSerializer(r).data,
                "score": match_score(r.distance),
            }
            for r in resumes
        ]
        return Response({"job": job.title, "matches": results})


class CandidateJobMatchesView(APIView):
    """GET /api/matching/candidates/me/jobs/ - top job recommendations for the current candidate."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        resume = Resume.objects.filter(candidate=request.user, is_primary=True).first()
        if not resume:
            return Response({"matches": []})
        jobs = match_jobs_to_candidate(resume)
        results = [
            {"job": JobPostingSerializer(j).data, "score": match_score(j.distance)}
            for j in jobs
        ]
        return Response({"matches": results})


class MatchExplanationView(APIView):
    """GET /api/matching/explain/?job_id=&resume_id= - RAG-grounded fit explanation."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        job = JobPosting.objects.get(id=request.query_params["job_id"])
        resume = Resume.objects.get(id=request.query_params["resume_id"])
        explanation = build_match_explanation(job, resume)
        return Response({"explanation": explanation})
