import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { jobsApi } from "../api/endpoints";
import { useAuth } from "../context/AuthContext";
import type { JobPosting } from "../types";

export function JobsPage() {
  const { user } = useAuth();
  const [jobs, setJobs] = useState<JobPosting[]>([]);
  const [loading, setLoading] = useState(true);
  const isRecruiter = user?.role === "recruiter" || user?.role === "admin";

  useEffect(() => {
    jobsApi
      .list()
      .then((data) => setJobs(data.results))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <div className="row" style={{ justifyContent: "space-between", alignItems: "center" }}>
        <h1>{isRecruiter ? "Your job postings" : "Open roles"}</h1>
        {isRecruiter && (
          <Link to="/jobs/new">
            <button>New job posting</button>
          </Link>
        )}
      </div>

      {loading && <p className="muted">Loading jobs...</p>}
      {!loading && jobs.length === 0 && <p className="muted">No job postings yet.</p>}

      <div className="panel-list">
        {jobs.map((job) => (
          <Link key={job.id} to={`/jobs/${job.id}`} style={{ textDecoration: "none", color: "inherit" }}>
            <div className="panel">
              <div className="row" style={{ justifyContent: "space-between" }}>
                <h3>{job.title}</h3>
                <span className={`badge ${job.status}`}>{job.status}</span>
              </div>
              <p className="muted">
                {job.location || "Remote-friendly"} · {job.employment_type.replace("_", "-")}
                {job.salary_min && job.salary_max
                  ? ` · $${job.salary_min.toLocaleString()}–$${job.salary_max.toLocaleString()}`
                  : ""}
              </p>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
