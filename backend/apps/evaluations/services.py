"""
Automated evaluation: grades each interview answer against the LLM-generated
rubric stored on the Question, then rolls the per-question scores up into an
overall recommendation. Human reviewers can still override via
Evaluation.reviewed_by_human / human_override_notes.
"""
from apps.common.llm_client import llm_client

EVALUATION_SYSTEM_PROMPT = """You are grading a technical interview answer against a rubric.
Respond with ONLY a JSON object:
{"score": number (0-100), "feedback": string}
Base the score strictly on how well the candidate's answer covers the rubric's key points."""

SUMMARY_SYSTEM_PROMPT = """You are summarizing a completed technical interview for a hiring
manager. Respond with ONLY a JSON object:
{
  "overall_score": number (0-100, weighted average of question scores),
  "recommendation": "strong_hire" | "hire" | "borderline" | "no_hire",
  "strengths": string[],
  "weaknesses": string[],
  "summary": string
}"""


def grade_answer(question) -> dict:
    prompt = (
        f"QUESTION ({question.type}):\n{question.prompt}\n\n"
        f"RUBRIC KEY POINTS:\n{question.rubric.get('key_points', [])}\n\n"
        f"CANDIDATE ANSWER:\n{question.candidate_answer or '(no answer provided)'}"
    )
    return llm_client.generate_json(system=EVALUATION_SYSTEM_PROMPT, prompt=prompt, max_tokens=500)


def evaluate_interview(interview) -> "Evaluation":  # noqa: F821
    from .models import Evaluation

    per_question_scores = []
    for question in interview.questions.all():
        graded = grade_answer(question)
        per_question_scores.append(
            {
                "question_id": question.id,
                "score": graded.get("score", 0),
                "feedback": graded.get("feedback", ""),
            }
        )

    scores_text = "\n".join(
        f"- Q{item['question_id']}: {item['score']}/100 — {item['feedback']}"
        for item in per_question_scores
    )
    rollup = llm_client.generate_json(
        system=SUMMARY_SYSTEM_PROMPT,
        prompt=f"Per-question grades:\n{scores_text}",
        max_tokens=800,
    )

    evaluation, _ = Evaluation.objects.update_or_create(
        interview=interview,
        defaults={
            "overall_score": rollup.get("overall_score", 0),
            "recommendation": rollup.get("recommendation", "borderline"),
            "per_question_scores": per_question_scores,
            "strengths": rollup.get("strengths", []),
            "weaknesses": rollup.get("weaknesses", []),
            "summary": rollup.get("summary", ""),
        },
    )
    return evaluation
