import { useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { jobsApi } from "../api/endpoints";

export function JobFormPage() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    title: "",
    description: "",
    requirements: "",
    location: "",
    is_remote: false,
    employment_type: "full_time" as const,
    salary_min: "",
    salary_max: "",
    status: "open" as const,
  });
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  function update<K extends keyof typeof form>(key: K, value: (typeof form)[K]) {
    setForm((f) => ({ ...f, [key]: value }));
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      const job = await jobsApi.create({
        ...form,
        salary_min: form.salary_min ? Number(form.salary_min) : null,
        salary_max: form.salary_max ? Number(form.salary_max) : null,
      });
      navigate(`/jobs/${job.id}`);
    } catch {
      setError("Could not create job posting.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div>
      <h1>New job posting</h1>
      <form onSubmit={handleSubmit} className="panel">
        <div className="field">
          <label>Title</label>
          <input required value={form.title} onChange={(e) => update("title", e.target.value)} />
        </div>
        <div className="field">
          <label>Description</label>
          <textarea
            required
            value={form.description}
            onChange={(e) => update("description", e.target.value)}
          />
        </div>
        <div className="field">
          <label>Requirements (skills, experience — used for AI matching)</label>
          <textarea
            required
            value={form.requirements}
            onChange={(e) => update("requirements", e.target.value)}
          />
        </div>
        <div className="row">
          <div className="field" style={{ flex: 1 }}>
            <label>Location</label>
            <input value={form.location} onChange={(e) => update("location", e.target.value)} />
          </div>
          <div className="field" style={{ flex: 1 }}>
            <label>Employment type</label>
            <select
              value={form.employment_type}
              onChange={(e) => update("employment_type", e.target.value as typeof form.employment_type)}
            >
              <option value="full_time">Full-time</option>
              <option value="part_time">Part-time</option>
              <option value="contract">Contract</option>
              <option value="internship">Internship</option>
            </select>
          </div>
        </div>
        <div className="row">
          <div className="field" style={{ flex: 1 }}>
            <label>Salary min (USD)</label>
            <input
              type="number"
              value={form.salary_min}
              onChange={(e) => update("salary_min", e.target.value)}
            />
          </div>
          <div className="field" style={{ flex: 1 }}>
            <label>Salary max (USD)</label>
            <input
              type="number"
              value={form.salary_max}
              onChange={(e) => update("salary_max", e.target.value)}
            />
          </div>
        </div>
        {error && <p className="error-text">{error}</p>}
        <button type="submit" disabled={submitting}>
          {submitting ? "Publishing..." : "Publish job"}
        </button>
      </form>
    </div>
  );
}
