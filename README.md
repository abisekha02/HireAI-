# HireAI — AI-Powered Recruitment & Interview Platform

A full-stack recruitment platform: React + TypeScript on the frontend, Django REST
Framework + PostgreSQL on the backend, with LLM-based resume analysis, semantic job
matching (pgvector + embeddings), RAG-grounded AI interview generation, and automated
candidate evaluation. JWT auth, role-based access control, Docker Compose, and CI included.

## Stack

| Layer          | Tech |
|----------------|------|
| Frontend       | React 18, TypeScript, Vite, React Router, Axios |
| Backend        | Django 5, Django REST Framework, SimpleJWT |
| Database       | PostgreSQL 16 + `pgvector` (embeddings for semantic search) |
| Async jobs     | Celery + Redis (resume parsing) |
| LLM            | Provider-agnostic client — Anthropic or OpenAI for generation, OpenAI embeddings for vector search |
| Infra          | Docker Compose, GitHub Actions CI |

## What it does

- **Resume analysis**: candidates upload a PDF/DOCX resume; a background job extracts
  text and asks an LLM to return structured data (skills, experience, education, a
  recruiter-facing summary), then embeds it for search.
- **Semantic job matching**: job postings and resumes are embedded into the same vector
  space. Recruiters see ranked candidate matches per job; candidates see ranked job
  recommendations — both via cosine similarity in Postgres (`pgvector`).
- **RAG-grounded interview generation**: when a recruiter moves a candidate to the
  interview stage, the LLM generates 5 tailored questions (coding, system design,
  conceptual, behavioral) using the *actual* job requirements and the *actual* parsed
  resume as context, plus a grading rubric per question.
- **Automated evaluation**: once a candidate submits answers, each answer is graded
  against its rubric, then rolled up into an overall score and hire recommendation
  (`strong_hire` / `hire` / `borderline` / `no_hire`), with a field for human override.
- **Auth & RBAC**: JWT access/refresh tokens; roles are `admin`, `recruiter`,
  `candidate`, `interviewer`, enforced both by DRF permission classes and by the
  frontend's route guards.

## Project layout

```
hireai/
├── backend/                 # Django REST Framework API
│   ├── config/               # settings, urls, celery app
│   └── apps/
│       ├── users/             # custom User model, JWT auth views
│       ├── common/            # RBAC permissions, LLMClient wrapper
│       ├── jobs/               # JobPosting + embeddings
│       ├── resumes/            # Resume upload, parsing, embeddings
│       ├── matching/           # semantic search + RAG explanation
│       ├── applications/       # candidate <-> job pipeline
│       ├── interviews/         # AI interview generation + answers
│       └── evaluations/        # automated grading + recommendation
├── frontend/                 # React + TypeScript app
│   └── src/
│       ├── api/                # axios client (JWT refresh) + typed endpoints
│       ├── context/            # auth context
│       ├── components/         # layout, protected route
│       ├── types/               # shared TS types mirroring the API
│       └── pages/               # login, register, dashboard, jobs, resume,
│                                  applications, interview-taking
├── docker-compose.yml
└── .github/workflows/ci.yml
```

## Running locally with Docker

1. Copy environment files and fill in your LLM API key(s):
   ```bash
   cp backend/.env.example backend/.env
   cp frontend/.env.example frontend/.env
   # edit backend/.env — set ANTHROPIC_API_KEY and/or OPENAI_API_KEY
   # (embeddings always use OPENAI_API_KEY; LLM_PROVIDER picks the generation model)
   ```
2. Start everything:
   ```bash
   docker compose up --build
   ```
   This brings up Postgres (with the `vector` extension), Redis, the Django API on
   `:8000`, a Celery worker for async resume parsing, and the Vite dev server on `:5173`.
3. Create an admin user (optional, for `/admin/`):
   ```bash
   docker compose exec backend python manage.py createsuperuser
   ```
4. Visit `http://localhost:5173`. Register as a recruiter to post jobs, or as a
   candidate to upload a resume and apply.

API docs (OpenAPI/Swagger) are served at `http://localhost:8000/api/docs/`.

## Running without Docker

**Backend**
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # point POSTGRES_HOST at a local Postgres with pgvector installed
python manage.py migrate
python manage.py runserver
```

**Frontend**
```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

## Notes on the AI integration

- All LLM calls go through `apps/common/llm_client.py`. Swapping providers for chat
  generation is a one-line env var change (`LLM_PROVIDER=anthropic|openai`); embeddings
  currently always use OpenAI's embeddings endpoint since Anthropic doesn't expose a
  first-party one.
- Prompts are written to return strict JSON, parsed defensively, and grounded in
  retrieved context (the specific job's requirements, the specific candidate's parsed
  resume) rather than letting the model free-associate — this is the RAG piece.
- Resume parsing runs asynchronously via Celery so uploads don't block the request;
  if no worker/broker is available (e.g. quick local testing without Redis), the view
  falls back to a synchronous call.

## What's stubbed vs. production-ready

This is a working scaffold, not a finished product. Before shipping you'd want to add:
tests (a CI job is wired up to run `manage.py test`, but no test cases are written yet),
rate limiting on LLM-backed endpoints, resume file validation/virus scanning, pagination
tuning, a production frontend build served via nginx (the included frontend Dockerfile
runs the Vite dev server, which is fine for local dev but not production), and
structured logging/observability around the LLM calls.
