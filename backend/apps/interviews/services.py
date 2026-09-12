"""
AI-generated technical interviews.

`generate_interview` is RAG-grounded: it pulls the job's actual requirements
and the candidate's actual parsed resume (skills, experience) into the
prompt so questions are tailored rather than generic.
"""
from apps.common.llm_client import llm_client

INTERVIEW_GENERATION_SYSTEM_PROMPT = """You are a senior technical interviewer designing a
structured interview for a specific candidate applying to a specific job. Generate
questions tailored to the overlap and gaps between the candidate's background and the
job's requirements. Respond with ONLY a JSON object of this shape:
{
  "focus_areas": string[],
  "questions": [
    {
      "order": number,
      "type": "coding" | "system_design" | "conceptual" | "behavioral",
      "prompt": string,
      "rubric": {"key_points": string[], "ideal_answer_summary": string}
    }
  ]
}
Generate exactly 5 questions: 2 coding, 1 system_design, 1 conceptual, 1 behavioral,
calibrated to the requested difficulty level."""


def generate_interview_content(job, resume, difficulty: str = "mid") -> dict:
    prompt = (
        f"DIFFICULTY: {difficulty}\n\n"
        f"JOB TITLE: {job.title}\n"
        f"JOB REQUIREMENTS:\n{job.requirements}\n\n"
        f"CANDIDATE SKILLS: {', '.join((resume.parsed_data or {}).get('skills', []))}\n"
        f"CANDIDATE EXPERIENCE SUMMARY: {(resume.parsed_data or {}).get('summary', '')}"
    )
    return llm_client.generate_json(
        system=INTERVIEW_GENERATION_SYSTEM_PROMPT, prompt=prompt, max_tokens=3000
    )


def generate_interview(application) -> "Interview":  # noqa: F821 - avoid circular import at module load
    from .models import Interview, Question

    content = generate_interview_content(
        job=application.job, resume=application.resume, difficulty="mid"
    )

    interview = Interview.objects.create(
        application=application,
        focus_areas=content.get("focus_areas", []),
    )
    Question.objects.bulk_create(
        [
            Question(
                interview=interview,
                order=q["order"],
                type=q["type"],
                prompt=q["prompt"],
                rubric=q.get("rubric", {}),
            )
            for q in content["questions"]
        ]
    )
    return interview
