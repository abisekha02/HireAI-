import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { applicationsApi, interviewsApi } from "../api/endpoints";
import { useAuth } from "../context/AuthContext";
import type { Application } from "../types";

const STAGES: Application["stage"][] = [
  "applied",
  "screening",
  "interview",
  "offer",
  "hired",
  "rejected",
];

export function ApplicationsPage() {
  const { user } = useAuth();
  const [applications, setApplications] = useState<Application[]>([]);
  const [generatingFor, setGeneratingFor] = useState<number | null>(null);
  const isRecruiter = user?.role === "recruiter" || user?.role === "admin";

  function load() {
    applicationsApi.list().then(setApplications);
  }

  useEffect(load, []);

  async function generateInterview(applicationId: number) {
    setGeneratingFor(applicationId);
    try {
      await interviewsApi.generate(applicationId);
      await applicationsApi.updateStage(applicationId, "interview");
      load();
    } finally {
      setGeneratingFor(null);
    }
  }

  return (
    <div>
      <h1>{isRecruiter ? "Hiring pipeline" : "My applications"}</h1>
      {applications.length === 0 && <p className="muted">Nothing here yet.</p>}
      <div className="panel-list">
        {applications.map((app) => (
          <div className="panel" key={app.id}>
            <div className="row" style={{ justifyContent: "space-between" }}>
              <div>
                <h3>{app.job_title}</h3>
                {isRecruiter && <p className="muted">{app.candidate_name}</p>}
              </div>
              <div style={{ textAlign: "right" }}>
                {app.match_score !== null && <div className="score">{app.match_score}%</div>}
                <span className={`badge ${app.stage}`}>{app.stage}</span>
              </div>
            </div>

            {isRecruiter ? (
              <div className="row" style={{ marginTop: 10 }}>
                <select
                  value={app.stage}
                  onChange={(e) =>
                    applicationsApi
                      .updateStage(app.id, e.target.value as Application["stage"])
                      .then(load)
                  }
                >
                  {STAGES.map((s) => (
                    <option key={s} value={s}>
                      {s}
                    </option>
                  ))}
                </select>
                <button
                  className="secondary"
                  onClick={() => generateInterview(app.id)}
                  disabled={generatingFor === app.id}
                >
                  {generatingFor === app.id ? "Generating..." : "Generate AI interview"}
                </button>
              </div>
            ) : (
              app.stage === "interview" && (
                <Link to={`/applications/${app.id}/interview`}>
                  <button style={{ marginTop: 10 }}>Take interview</button>
                </Link>
              )
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
