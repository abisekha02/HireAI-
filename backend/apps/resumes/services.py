"""
Resume ingestion pipeline:
  1. extract_text        -> pull raw text out of the uploaded PDF/DOCX
  2. analyze_resume       -> ask the LLM to turn raw text into structured JSON
  3. embed_and_store      -> compute + persist the embedding for matching/RAG

`process_resume` runs all three and is what the upload view / Celery task calls.
"""
from apps.common.llm_client import llm_client

RESUME_ANALYSIS_SYSTEM_PROMPT = """You are an expert technical recruiter assistant.
Extract structured information from the resume text you are given.
Respond with ONLY a JSON object (no prose, no markdown fences) matching this shape:
{
  "full_name": string | null,
  "email": string | null,
  "years_experience": number,
  "skills": string[],
  "education": [{"degree": string, "institution": string, "year": string}],
  "work_experience": [
    {"title": string, "company": string, "start": string, "end": string, "summary": string}
  ],
  "certifications": string[],
  "summary": string  // 2-3 sentence recruiter-facing summary
}
If a field is unknown, use null, an empty string, or an empty array as appropriate."""


def extract_text(file_field) -> str:
    """Extract raw text from an uploaded resume file (PDF or DOCX)."""
    name = file_field.name.lower()
    file_field.open("rb")
    try:
        if name.endswith(".pdf"):
            from pypdf import PdfReader

            reader = PdfReader(file_field)
            return "\n".join(page.extract_text() or "" for page in reader.pages)
        if name.endswith(".docx"):
            import docx

            document = docx.Document(file_field)
            return "\n".join(p.text for p in document.paragraphs)
        # Fallback: plain text
        return file_field.read().decode("utf-8", errors="ignore")
    finally:
        file_field.close()


def analyze_resume(raw_text: str) -> dict:
    """Send resume text to the LLM and return structured candidate data."""
    truncated = raw_text[:15000]  # keep prompts bounded
    return llm_client.generate_json(
        system=RESUME_ANALYSIS_SYSTEM_PROMPT,
        prompt=f"Resume text:\n\n{truncated}",
    )


def process_resume(resume) -> None:
    """Full pipeline: extract -> analyze -> embed -> save. Mutates + saves `resume`."""
    from .models import Resume

    resume.parse_status = Resume.ParseStatus.PROCESSING
    resume.save(update_fields=["parse_status"])

    try:
        raw_text = extract_text(resume.file)
        resume.raw_text = raw_text

        parsed = analyze_resume(raw_text)
        resume.parsed_data = parsed

        embedding_source = parsed.get("summary") or raw_text[:4000]
        resume.embedding = llm_client.embed(embedding_source)

        resume.parse_status = Resume.ParseStatus.PARSED
        resume.parse_error = ""
    except Exception as exc:  # noqa: BLE001 - persist any failure for visibility
        resume.parse_status = Resume.ParseStatus.FAILED
        resume.parse_error = str(exc)
    finally:
        resume.save()
