import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { authApi } from "../api/endpoints";
import { useAuth } from "../context/AuthContext";

export function RegisterPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({
    email: "",
    username: "",
    password: "",
    first_name: "",
    last_name: "",
    role: "candidate" as "candidate" | "recruiter",
    company_name: "",
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
      await authApi.register(form);
      await login(form.email, form.password);
      navigate("/");
    } catch {
      setError("Could not register. Check your details and try again.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="auth-wrap">
      <h1>Create account</h1>
      <form onSubmit={handleSubmit} className="panel">
        <div className="field">
          <label>I am a</label>
          <select value={form.role} onChange={(e) => update("role", e.target.value as typeof form.role)}>
            <option value="candidate">Candidate</option>
            <option value="recruiter">Recruiter</option>
          </select>
        </div>
        <div className="row">
          <div className="field" style={{ flex: 1 }}>
            <label>First name</label>
            <input value={form.first_name} onChange={(e) => update("first_name", e.target.value)} />
          </div>
          <div className="field" style={{ flex: 1 }}>
            <label>Last name</label>
            <input value={form.last_name} onChange={(e) => update("last_name", e.target.value)} />
          </div>
        </div>
        {form.role === "recruiter" && (
          <div className="field">
            <label>Company</label>
            <input value={form.company_name} onChange={(e) => update("company_name", e.target.value)} />
          </div>
        )}
        <div className="field">
          <label>Username</label>
          <input required value={form.username} onChange={(e) => update("username", e.target.value)} />
        </div>
        <div className="field">
          <label>Email</label>
          <input
            type="email"
            required
            value={form.email}
            onChange={(e) => update("email", e.target.value)}
          />
        </div>
        <div className="field">
          <label>Password</label>
          <input
            type="password"
            required
            minLength={8}
            value={form.password}
            onChange={(e) => update("password", e.target.value)}
          />
        </div>
        {error && <p className="error-text">{error}</p>}
        <button type="submit" disabled={submitting}>
          {submitting ? "Creating..." : "Create account"}
        </button>
      </form>
      <p className="muted">
        Already have an account? <Link to="/login">Log in</Link>
      </p>
    </div>
  );
}
