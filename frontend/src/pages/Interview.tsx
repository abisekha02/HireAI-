import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { interviewsApi } from "../api/endpoints";
import type { Evaluation, Interview } from "../types";

export function InterviewPage() {
  const { applicationId } = useParams();
  const [interview, setInterview] = useState<Interview | null>(null);
  const [answers, setAnswers] = useState<Record<number, string>>({});
  const [evaluation, setEvaluation] = useState<Evaluation | null>(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!applicationId) return;
    interviewsApi.byApplication(Number(applicationId)).then(async (found) => {
      if (!found) return;
      if (found.status === "generated") {
        found = await interviewsApi.start(found.id);
      }
      setInterview(found);
      const initial: Record<number, string> = {};
      found.questions.forEach((q) => (initial[q.id] = q.candidate_answer));
      setAnswers(initial);
    });
  }, [applicationId]);

  async function saveAnswer(questionId: number) {
    if (!interview) return;
    await interviewsApi.answer(interview.id, questionId, answers[questionId] ?? "");
  }

  async function handleSubmit() {
    if (!interview) return;
    setSubmitting(true);
    try {
      // Persist any unsaved edits first.
      await Promise.all(interview.questions.map((q) => saveAnswer(q.id)));
      const result = await interviewsApi.complete(interview.id);
      setInterview(result.interview);
      setEvaluation(result.evaluation);
    } finally {
      setSubmitting(false);
    }
  }

  if (!interview) return <p className="muted">Loading interview...</p>;

  if (evaluation) {
    return (
      <div>
        <h1>Interview complete</h1>
        <div className="panel">
          <div className="row" style={{ justifyContent: "space-between" }}>
            <h2>Overall score</h2>
            <span className="score">{evaluation.overall_score}/100</span>
          </div>
          <span className={`badge ${evaluation.recommendation}`}>
            {evaluation.recommendation.replace("_", " ")}
          </span>
          <p style={{ marginTop: 14 }}>{evaluation.summary}</p>
        </div>
        <p className="muted">
          Thanks for completing the interview — the hiring team will follow up with next steps.
        </p>
      </div>
    );
  }

  return (
    <div>
      <h1>Technical interview</h1>
      <p className="muted">
        {interview.difficulty} level · focus areas: {interview.focus_areas.join(", ")}
      </p>

      {interview.questions.map((q) => (
        <div className="question-card" key={q.id}>
          <div className="row" style={{ justifyContent: "space-between" }}>
            <h3>Question {q.order}</h3>
            <span className="badge">{q.type.replace("_", " ")}</span>
          </div>
          <p>{q.prompt}</p>
          <textarea
            value={answers[q.id] ?? ""}
            onChange={(e) => setAnswers((a) => ({ ...a, [q.id]: e.target.value }))}
            onBlur={() => saveAnswer(q.id)}
            rows={5}
            placeholder="Type your answer..."
          />
        </div>
      ))}

      <button onClick={handleSubmit} disabled={submitting}>
        {submitting ? "Submitting for evaluation..." : "Submit interview"}
      </button>
    </div>
  );
}
