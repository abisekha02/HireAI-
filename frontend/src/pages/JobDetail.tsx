import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { applicationsApi, jobsApi, matchingApi, resumesApi } from "../api/endpoints";
import { useAuth } from "../context/AuthContext";
import type { CandidateMatch, JobPosting, Resume } from "../types";

export function JobDetailPage() {
  const { id } = useParams();
  const { user } = useAuth();
  const [job, setJob] = useState<JobPosting | null>(null);
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [matches, setMatches] = useState<CandidateMatch[]>([]);
  const [applied, setApplied] = useState(false);
  const [status, setStatus] = useState("");

  const isRecruiter = user?.role === "recruiter" || user?.role === "admin";

  useEffect(() => {
    if (!id) return;
    jobsApi.get(Number(id)).then(setJob);
    if (isRecruiter) {
      matchingApi.candidatesForJob(Number(id)).then((data) => setMatches(data.matches));
    } else {
      resumesApi.list().then(setResumes);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  async function handleApply() {
    const primary = resumes.find((r) => r.is_primary) ?? resumes[0];
    if (!primary) {
      setStatus("Upload a resume before applying.");
      return;
    }
    try {
      await applicationsApi.create({ job: Number(id), resume: primary.id });
      setApplied(true);
      setStatus("Application submitted!");
    } catch {
      setStatus("Could not submit application (you may have already applied).");
    }
  }

  if (!job) return <p className="muted">Loading...</p>;

  return (
    <div>
      <div className="row" style={{ justifyContent: "space-between" }}>
        <h1>{job.title}</h1>
        <span className={`badge ${job.status}`}>{job.status}</span>
      </div>
      <p className="muted">
        {job.location || "Remote-friendly"} · {job.employment_type.replace("_", "-")}
      </p>

      <div className="panel">
        <h3>Description</h3>
        <p>{job.description}</p>
        <h3>Requirements</h3>
        <p>{job.requirements}</p>
      </div>

      {!isRecruiter && (
        <div className="panel">
          <h3>Apply</h3>
          <p className="muted">Applying uses your primary resume for AI-based matching.</p>
          <button onClick={handleApply} disabled={applied}>
            {applied ? "Applied" : "Apply now"}
          </button>
          {status && <p className="muted">{status}</p>}
        </div>
      )}

      {isRecruiter && (
        <div>
          <h2>AI-matched candidates</h2>
          {matches.length === 0 && <p className="muted">No parsed resumes matched yet.</p>}
          <div className="panel-list">
            {matches.map((m) => (
              <div className="panel" key={m.resume.id}>
                <div className="row" style={{ justifyContent: "space-between" }}>
                  <h3>{m.resume.parsed_data?.full_name ?? "Candidate"}</h3>
                  <span className="score">{m.score}%</span>
                </div>
                <p className="muted">{m.resume.parsed_data?.summary}</p>
                <div className="row">
                  {(m.resume.parsed_data?.skills ?? []).slice(0, 8).map((s) => (
                    <span className="badge" key={s}>
                      {s}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
