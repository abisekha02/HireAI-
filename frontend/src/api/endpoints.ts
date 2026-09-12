import { api, tokenStorage } from "./client";
import type {
  Application,
  CandidateMatch,
  Evaluation,
  Interview,
  JobMatch,
  JobPosting,
  Resume,
  User,
} from "../types";

export const authApi = {
  async login(email: string, password: string) {
    const { data } = await api.post<{ access: string; refresh: string; user: User }>(
      "/auth/login/",
      { email, password }
    );
    tokenStorage.set(data.access, data.refresh);
    return data.user;
  },
  async register(payload: {
    email: string;
    username: string;
    password: string;
    first_name?: string;
    last_name?: string;
    role: "recruiter" | "candidate";
    company_name?: string;
  }) {
    const { data } = await api.post<User>("/auth/register/", payload);
    return data;
  },
  async me() {
    const { data } = await api.get<User>("/auth/me/");
    return data;
  },
  logout() {
    tokenStorage.clear();
  },
};

export const jobsApi = {
  list: async (params?: Record<string, string>) => {
    const { data } = await api.get<{ results: JobPosting[]; count: number }>("/jobs/", { params });
    return data;
  },
  get: async (id: number) => (await api.get<JobPosting>(`/jobs/${id}/`)).data,
  create: async (payload: Partial<JobPosting>) => (await api.post<JobPosting>("/jobs/", payload)).data,
  update: async (id: number, payload: Partial<JobPosting>) =>
    (await api.patch<JobPosting>(`/jobs/${id}/`, payload)).data,
  remove: async (id: number) => api.delete(`/jobs/${id}/`),
};

export const resumesApi = {
  list: async () => (await api.get<{ results: Resume[] }>("/resumes/")).data.results,
  upload: async (file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    const { data } = await api.post<Resume>("/resumes/", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return data;
  },
};

export const applicationsApi = {
  list: async () => (await api.get<{ results: Application[] }>("/applications/")).data.results,
  create: async (payload: { job: number; resume: number; cover_note?: string }) =>
    (await api.post<Application>("/applications/", payload)).data,
  updateStage: async (id: number, stage: Application["stage"]) =>
    (await api.patch<Application>(`/applications/${id}/`, { stage })).data,
};

export const interviewsApi = {
  generate: async (applicationId: number) =>
    (await api.post<Interview>("/interviews/", { application: applicationId })).data,
  get: async (id: number) => (await api.get<Interview>(`/interviews/${id}/`)).data,
  byApplication: async (applicationId: number) => {
    const { data } = await api.get<{ results: Interview[] }>("/interviews/", {
      params: { application: applicationId },
    });
    return data.results[0] ?? null;
  },
  start: async (id: number) => (await api.post<Interview>(`/interviews/${id}/start/`)).data,
  answer: async (interviewId: number, questionId: number, answer: string) =>
    api.post(`/interviews/${interviewId}/questions/${questionId}/answer/`, {
      candidate_answer: answer,
    }),
  complete: async (id: number) =>
    (await api.post<{ interview: Interview; evaluation: Evaluation }>(`/interviews/${id}/complete/`))
      .data,
};

export const matchingApi = {
  candidatesForJob: async (jobId: number) =>
    (await api.get<{ job: string; matches: CandidateMatch[] }>(`/matching/jobs/${jobId}/candidates/`))
      .data,
  jobsForMe: async () =>
    (await api.get<{ matches: JobMatch[] }>("/matching/candidates/me/jobs/")).data,
  explain: async (jobId: number, resumeId: number) =>
    (
      await api.get<{ explanation: string }>("/matching/explain/", {
        params: { job_id: jobId, resume_id: resumeId },
      })
    ).data,
};
