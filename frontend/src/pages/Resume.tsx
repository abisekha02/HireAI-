import { useEffect, useRef, useState } from "react";
import { resumesApi } from "../api/endpoints";
import type { Resume } from "../types";

export function ResumePage() {
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");
  const fileInput = useRef<HTMLInputElement>(null);

  function load() {
    resumesApi.list().then(setResumes);
  }

  useEffect(load, []);

  async function handleUpload() {
    const file = fileInput.current?.files?.[0];
    if (!file) return;
    setUploading(true);
    setError("");
    try {
      await resumesApi.upload(file);
      load();
      if (fileInput.current) fileInput.current.value = "";
    } catch {
      setError("Upload failed. Please try a PDF or DOCX file.");
    } finally {
      setUploading(false);
    }
  }

  return (
    <div>
      <h1>Your resume</h1>
      <div className="panel">
        <div className="field">
          <label>Upload a PDF or DOCX resume</label>
          <input ref={fileInput} type="file" accept=".pdf,.docx" />
        </div>
        {error && <p className="error-text">{error}</p>}
        <button onClick={handleUpload} disabled={uploading}>
          {uploading ? "Uploading..." : "Upload & analyze"}
        </button>
      </div>

      <div className="panel-list">
        {resumes.map((r) => (
          <div className="panel" key={r.id}>
            <div className="row" style={{ justifyContent: "space-between" }}>
              <h3>{r.parsed_data?.full_name ?? "Resume"}</h3>
              <span className={`badge ${r.parse_status}`}>{r.parse_status}</span>
            </div>
            {r.parse_status === "parsed" && r.parsed_data && (
              <>
                <p className="muted">{r.parsed_data.summary}</p>
                <div className="row">
                  {r.parsed_data.skills.map((s) => (
                    <span className="badge" key={s}>
                      {s}
                    </span>
                  ))}
                </div>
              </>
            )}
            {r.parse_status === "failed" && <p className="error-text">{r.parse_error}</p>}
          </div>
        ))}
      </div>
    </div>
  );
}
