import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export function DashboardPage() {
  const { user } = useAuth();
  if (!user) return null;

  const isRecruiter = user.role === "recruiter" || user.role === "admin";

  return (
    <div>
      <h1>Welcome back, {user.first_name || user.username}</h1>
      {isRecruiter ? (
        <div className="panel-list">
          <div className="panel">
            <h2>Post a role</h2>
            <p className="muted">
              Create a job posting. HireAI embeds it automatically for semantic candidate matching.
            </p>
            <Link to="/jobs/new">
              <button>New job posting</button>
            </Link>
          </div>
          <div className="panel">
            <h2>Review your pipeline</h2>
            <p className="muted">See applications, AI-generated interviews, and evaluations in one place.</p>
            <Link to="/applications">
              <button className="secondary">Go to pipeline</button>
            </Link>
          </div>
        </div>
      ) : (
        <div className="panel-list">
          <div className="panel">
            <h2>Upload your resume</h2>
            <p className="muted">
              HireAI parses it with an LLM and uses the result for semantic job matching.
            </p>
            <Link to="/resume">
              <button>Manage resume</button>
            </Link>
          </div>
          <div className="panel">
            <h2>Browse open roles</h2>
            <p className="muted">Apply directly, then take an AI-generated technical interview.</p>
            <Link to="/jobs">
              <button className="secondary">Browse jobs</button>
            </Link>
          </div>
        </div>
      )}
    </div>
  );
}
