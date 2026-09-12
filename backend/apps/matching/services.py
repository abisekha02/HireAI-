"""
Semantic matching between candidates and job postings, plus a small RAG
(retrieval-augmented generation) helper used by the interview-generation and
evaluation services to ground LLM output in the candidate's actual resume
and the job's actual requirements instead of letting the model hallucinate.

Storage: pgvector `VectorField` columns on JobPosting.embedding and
Resume.embedding, queried with cosine distance via `.order_by()` +
`CosineDistance` from pgvector.django.
"""
from pgvector.django import CosineDistance

from apps.common.llm_client import llm_client


def embed_and_store_job(job) -> None:
    """Compute and persist the embedding for a job posting."""
    job.embedding = llm_client.embed(job.matching_text)
    job.save(update_fields=["embedding"])


def match_candidates_to_job(job, limit: int = 20):
    """Return the resumes best matching a job posting, ranked by cosine distance."""
    from apps.resumes.models import Resume

    if job.embedding is None:
        embed_and_store_job(job)

    return (
        Resume.objects.filter(embedding__isnull=False, parse_status="parsed")
        .annotate(distance=CosineDistance("embedding", job.embedding))
        .order_by("distance")[:limit]
    )


def match_jobs_to_candidate(resume, limit: int = 20):
    """Return the job postings best matching a candidate's resume."""
    from apps.jobs.models import JobPosting

    if resume.embedding is None:
        return JobPosting.objects.none()

    return (
        JobPosting.objects.filter(embedding__isnull=False, status=JobPosting.Status.OPEN)
        .annotate(distance=CosineDistance("embedding", resume.embedding))
        .order_by("distance")[:limit]
    )


def match_score(distance: float) -> float:
    """Convert a cosine distance (0 = identical, 2 = opposite) into a 0-100 score."""
    similarity = max(0.0, 1.0 - distance)
    return round(similarity * 100, 1)


# ---------------------------------------------------------------------------
# RAG: retrieve the most relevant chunks of context to ground LLM generations
# ---------------------------------------------------------------------------
def build_match_explanation(job, resume) -> str:
    """Ask the LLM to explain *why* a candidate matches a job, grounded in
    the actual job requirements + resume summary retrieved above (RAG)."""
    system = (
        "You are a recruiting assistant. Given a job posting and a candidate "
        "resume summary, explain in 2-3 concise sentences why the candidate "
        "is or isn't a strong fit. Be specific about overlapping and missing "
        "skills. Do not invent details not present in the provided context."
    )
    prompt = (
        f"JOB REQUIREMENTS:\n{job.requirements}\n\n"
        f"CANDIDATE SUMMARY:\n{(resume.parsed_data or {}).get('summary', resume.raw_text[:1500])}\n\n"
        f"CANDIDATE SKILLS:\n{', '.join((resume.parsed_data or {}).get('skills', []))}"
    )
    return llm_client._complete(system=system, prompt=prompt, max_tokens=300)  # noqa: SLF001
