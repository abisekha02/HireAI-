export type Role = "admin" | "recruiter" | "candidate" | "interviewer";

export interface User {
  id: number;
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  role: Role;
  company_name: string;
  phone: string;
  created_at: string;
}

export interface JobPosting {
  id: number;
  recruiter: number;
  recruiter_name: string;
  title: string;
  description: string;
  requirements: string;
  location: string;
  is_remote: boolean;
  employment_type: "full_time" | "part_time" | "contract" | "internship";
  salary_min: number | null;
  salary_max: number | null;
  status: "draft" | "open" | "closed";
  created_at: string;
  updated_at: string;
}

export interface ParsedResumeData {
  full_name: string | null;
  email: string | null;
  years_experience: number;
  skills: string[];
  education: { degree: string; institution: string; year: string }[];
  work_experience: {
    title: string;
    company: string;
    start: string;
    end: string;
    summary: string;
  }[];
  certifications: string[];
  summary: string;
}

export interface Resume {
  id: number;
  candidate: number;
  file: string;
  parsed_data: ParsedResumeData | null;
  parse_status: "pending" | "processing" | "parsed" | "failed";
  parse_error: string;
  is_primary: boolean;
  created_at: string;
  updated_at: string;
}

export type ApplicationStage =
  | "applied"
  | "screening"
  | "interview"
  | "offer"
  | "rejected"
  | "hired";

export interface Application {
  id: number;
  job: number;
  job_title: string;
  candidate: number;
  candidate_name: string;
  resume: number | null;
  stage: ApplicationStage;
  match_score: number | null;
  cover_note: string;
  created_at: string;
  updated_at: string;
}

export interface Question {
  id: number;
  order: number;
  type: "coding" | "system_design" | "conceptual" | "behavioral";
  prompt: string;
  candidate_answer: string;
  answered_at: string | null;
}

export interface Interview {
  id: number;
  application: number;
  status: "generated" | "in_progress" | "completed" | "evaluated";
  difficulty: "junior" | "mid" | "senior";
  focus_areas: string[];
  started_at: string | null;
  completed_at: string | null;
  created_at: string;
  questions: Question[];
}

export interface Evaluation {
  id: number;
  interview: number;
  overall_score: number;
  recommendation: "strong_hire" | "hire" | "borderline" | "no_hire";
  per_question_scores: { question_id: number; score: number; feedback: string }[];
  strengths: string[];
  weaknesses: string[];
  summary: string;
  reviewed_by_human: boolean;
  human_override_notes: string;
  created_at: string;
}

export interface JobMatch {
  job: JobPosting;
  score: number;
}

export interface CandidateMatch {
  resume: Resume;
  score: number;
}
