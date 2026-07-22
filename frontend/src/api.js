const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

async function request(path, options = {}) {
  const response = await fetch(`${API_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
    ...options,
  });

  const contentType = response.headers.get("content-type") || "";
  const data = contentType.includes("application/json") ? await response.json() : await response.text();

  if (!response.ok) {
    throw new Error(data?.detail || data?.error || "Request failed");
  }

  return data;
}

async function upload(path, formData) {
  const response = await fetch(`${API_URL}${path}`, {
    method: "POST",
    body: formData,
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data?.detail || data?.error || "Upload failed");
  }

  return data;
}

async function download(path, payload) {
  const response = await fetch(`${API_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    throw new Error(data?.detail || "Download generation failed");
  }
  return { blob: await response.blob(), matchScore: Number(response.headers.get("X-TrueFit-Match-Score") || 0) };
}

export const api = {
  health: () => request("/api/health"),
  login: (email, password, otpCode = null) =>
    request("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password, otp_code: otpCode }),
    }),
  signup: (email, password) =>
    request("/api/auth/signup", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),
  changePassword: (email, currentPassword, newPassword) => request("/api/security/password/change", { method: "POST", body: JSON.stringify({ email, current_password: currentPassword, new_password: newPassword }) }),
  requestPasswordReset: (email) => request("/api/security/password/reset/request", { method: "POST", body: JSON.stringify({ email }) }),
  confirmPasswordReset: (email, token, newPassword) => request("/api/security/password/reset/confirm", { method: "POST", body: JSON.stringify({ email, token, new_password: newPassword }) }),
  twoFactorStatus: (email) => request(`/api/security/2fa/status/${encodeURIComponent(email)}`),
  setupTwoFactor: (email) => request(`/api/security/2fa/setup/${encodeURIComponent(email)}`, { method: "POST" }),
  confirmTwoFactor: (email, code) => request("/api/security/2fa/confirm", { method: "POST", body: JSON.stringify({ email, code }) }),
  disableTwoFactor: (email, password, code) => request("/api/security/2fa/disable", { method: "POST", body: JSON.stringify({ email, password, code }) }),
  privacySummary: () => request("/api/security/privacy"),
  exportPersonalData: (email) => request(`/api/security/data/${encodeURIComponent(email)}`),
  deleteAccount: (email, password, confirmation) => request("/api/security/account/delete", { method: "POST", body: JSON.stringify({ email, password, confirmation }) }),
  recruiterWorkspace: (email) => request(`/api/recruiter/workspace/${encodeURIComponent(email)}`),
  saveRecruiterWorkspace: (email, workspace) => request(`/api/recruiter/workspace/${encodeURIComponent(email)}`, { method: "PUT", body: JSON.stringify({ workspace }) }),
  deleteRecruiterWorkspace: (email) => request(`/api/recruiter/workspace/${encodeURIComponent(email)}`, { method: "DELETE" }),
  sendEmail: (payload) => request("/api/communications/email/send", { method: "POST", body: JSON.stringify(payload) }),
  profile: (email) => request(`/api/profile/${encodeURIComponent(email)}`),
  createProfile: (email, fullName = "") => request(`/api/profile/${encodeURIComponent(email)}?full_name=${encodeURIComponent(fullName)}`, { method: "POST" }),
  updateProfile: (email, data) => request(`/api/profile/${encodeURIComponent(email)}`, { method: "PUT", body: JSON.stringify({ data }) }),
  addExperience: (email, data) => request(`/api/profile/${encodeURIComponent(email)}/experiences`, { method: "POST", body: JSON.stringify(data) }),
  updateExperience: (email, id, data) => request(`/api/profile/${encodeURIComponent(email)}/experiences/${encodeURIComponent(id)}`, { method: "PUT", body: JSON.stringify({ data }) }),
  deleteExperience: (email, id) => request(`/api/profile/${encodeURIComponent(email)}/experiences/${encodeURIComponent(id)}`, { method: "DELETE" }),
  addSkill: (email, data) => request(`/api/profile/${encodeURIComponent(email)}/skills`, { method: "POST", body: JSON.stringify(data) }),
  updateSkill: (email, id, data) => request(`/api/profile/${encodeURIComponent(email)}/skills/${encodeURIComponent(id)}`, { method: "PUT", body: JSON.stringify({ data }) }),
  deleteSkill: (email, id) => request(`/api/profile/${encodeURIComponent(email)}/skills/${encodeURIComponent(id)}`, { method: "DELETE" }),
  addAchievement: (email, experienceId, data) => request(`/api/profile/${encodeURIComponent(email)}/experiences/${encodeURIComponent(experienceId)}/achievements`, { method: "POST", body: JSON.stringify(data) }),
  deleteAchievement: (email, experienceId, achievementId) => request(`/api/profile/${encodeURIComponent(email)}/experiences/${encodeURIComponent(experienceId)}/achievements/${encodeURIComponent(achievementId)}`, { method: "DELETE" }),
  cvHistory: (email) => request(`/api/cv/history/${encodeURIComponent(email)}`),
  updateCvStatus: (email, id, status) => request(`/api/cv/history/${encodeURIComponent(email)}/${encodeURIComponent(id)}`, { method: "PUT", body: JSON.stringify({ status }) }),
  deleteCv: (email, id) => request(`/api/cv/history/${encodeURIComponent(email)}/${encodeURIComponent(id)}`, { method: "DELETE" }),
  saveCv: (email, data) => request(`/api/cv/history/${encodeURIComponent(email)}`, { method: "POST", body: JSON.stringify(data) }),
  renderCv: (payload) =>
    request("/api/cv/render", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  downloadCvPdf: (payload) => download("/api/cv/pdf", payload),
  downloadCvDocx: (payload) => download("/api/cv/docx", payload),
  matchBatch: (payload) =>
    request("/api/matching/batch", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  analyseMatch: (payload) =>
    request("/api/matching/analysis", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  extractResume: (file) => {
    const formData = new FormData();
    formData.append("file", file);
    return upload("/api/matching/resume/extract", formData);
  },
  feedback: (payload) =>
    request("/api/matching/feedback", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  invite: (payload) =>
    request("/api/matching/invite", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
};
