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

export const api = {
  health: () => request("/health"),
  login: (email, password) =>
    request("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),
  signup: (email, password) =>
    request("/api/auth/signup", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),
  profile: (email) => request(`/api/profile/${encodeURIComponent(email)}`),
  renderCv: (payload) =>
    request("/api/cv/render", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  matchBatch: (payload) =>
    request("/api/matching/batch", {
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
