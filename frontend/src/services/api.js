// FailSafe — API Service Layer

const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

function getToken() {
  return localStorage.getItem("failsafe_token");
}

async function request(path, options = {}) {
  const token = getToken();
  const headers = {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  };

  const res = await fetch(`${BASE_URL}${path}`, { ...options, headers });

  if (res.status === 401) {
    localStorage.removeItem("failsafe_token");
    localStorage.removeItem("failsafe_user");
    window.location.href = "/login";
    return;
  }

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Unknown error" }));
    throw new Error(err.detail || "Request failed");
  }

  return res.json();
}

// ─── Auth ─────────────────────────────────────────────────────────────────────

export const auth = {
  login: (email, password) =>
    request("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),

  register: (data) =>
    request("/api/auth/register", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  me: () => request("/api/auth/me"),
};

// ─── Predict ──────────────────────────────────────────────────────────────────

export const predict = {
  students: (students) =>
    request("/api/predict/", {
      method: "POST",
      body: JSON.stringify({ students }),
    }),

  uploadCSV: async (file) => {
    const token = getToken();
    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch(`${BASE_URL}/api/predict/upload-csv`, {
      method: "POST",
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      body: formData,
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Upload failed" }));
      throw new Error(err.detail);
    }
    return res.json();
  },
};

// ─── Dashboard ────────────────────────────────────────────────────────────────

export const dashboard = {
  stats: () => request("/api/dashboard/stats"),

  students: (riskLevel) =>
    request(`/api/dashboard/students${riskLevel ? `?risk_level=${riskLevel}` : ""}`),

  studentDetail: (id) => request(`/api/dashboard/student/${id}`),
};

// ─── Interventions ────────────────────────────────────────────────────────────

export const interventions = {
  list: (status) =>
    request(`/api/interventions/${status ? `?status=${status}` : ""}`),

  update: (id, data) =>
    request(`/api/interventions/${id}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),
};
