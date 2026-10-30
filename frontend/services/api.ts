import {
  OverviewData, TrendData, GeographyData, SeverityData,
  PaginatedAccidents, DatasetItem, QualityProfile, SystemStatus,
  DataFreshness, FilterState
} from "@/types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "/api/v1";

function getAuthHeader(): Record<string, string> {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("traffictrend_token");
    if (token) {
      return { Authorization: `Bearer ${token}` };
    }
  }
  return {};
}

function buildQuery(filters?: Partial<FilterState>): string {
  if (!filters) return "";
  const params = new URLSearchParams();
  if (filters.state && filters.state !== "All") params.append("state", filters.state);
  if (filters.severity && filters.severity !== "All") params.append("severity", filters.severity);
  if (filters.year && filters.year > 0) params.append("year", filters.year.toString());
  if (filters.weather && filters.weather !== "All") params.append("weather", filters.weather);
  if (filters.road_type && filters.road_type !== "All") params.append("road_type", filters.road_type);
  if (filters.start_date) params.append("start_date", filters.start_date);
  if (filters.end_date) params.append("end_date", filters.end_date);
  const q = params.toString();
  return q ? `?${q}` : "";
}

export const api = {
  // Auth
  async login(formData: FormData) {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: "POST",
      body: formData,
    });
    if (!res.ok) throw new Error("Authentication failed");
    return res.json();
  },

  async jsonLogin(credentials: { email: string; password: string }) {
    const res = await fetch(`${API_BASE}/auth/json-login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(credentials),
    });
    if (!res.ok) throw new Error("Invalid credentials");
    return res.json();
  },

  async getMe() {
    const res = await fetch(`${API_BASE}/auth/me`, {
      headers: getAuthHeader(),
    });
    if (!res.ok) throw new Error("Unauthorized");
    return res.json();
  },

  // Dashboard
  async getOverview(filters?: Partial<FilterState>): Promise<OverviewData> {
    const res = await fetch(`${API_BASE}/dashboard/overview${buildQuery(filters)}`);
    if (!res.ok) throw new Error("Failed to fetch dashboard overview");
    return res.json();
  },

  async getTrends(filters?: Partial<FilterState>): Promise<TrendData> {
    const res = await fetch(`${API_BASE}/dashboard/trends${buildQuery(filters)}`);
    if (!res.ok) throw new Error("Failed to fetch trends data");
    return res.json();
  },

  async getGeography(filters?: Partial<FilterState>): Promise<GeographyData> {
    const res = await fetch(`${API_BASE}/dashboard/geography${buildQuery(filters)}`);
    if (!res.ok) throw new Error("Failed to fetch geographical intelligence");
    return res.json();
  },

  async getSeverity(filters?: Partial<FilterState>): Promise<SeverityData> {
    const res = await fetch(`${API_BASE}/dashboard/severity${buildQuery(filters)}`);
    if (!res.ok) throw new Error("Failed to fetch severity analytics");
    return res.json();
  },

  // Analytics
  async getAccidents(page = 1, pageSize = 25, search = "", filters?: Partial<FilterState>): Promise<PaginatedAccidents> {
    const params = new URLSearchParams();
    params.append("page", page.toString());
    params.append("page_size", pageSize.toString());
    if (search) params.append("search", search);
    if (filters?.state && filters.state !== "All") params.append("state", filters.state);
    if (filters?.severity && filters.severity !== "All") params.append("severity", filters.severity);
    if (filters?.year && filters.year > 0) params.append("year", filters.year.toString());

    const res = await fetch(`${API_BASE}/analytics/accidents?${params.toString()}`);
    if (!res.ok) throw new Error("Failed to fetch accident records");
    return res.json();
  },

  async getAnomalies() {
    const res = await fetch(`${API_BASE}/analytics/anomalies`);
    if (!res.ok) throw new Error("Failed to fetch anomalies");
    return res.json();
  },

  async getForecast(horizon = 6) {
    const res = await fetch(`${API_BASE}/analytics/forecast?horizon=${horizon}`);
    if (!res.ok) throw new Error("Failed to fetch accident forecast");
    return res.json();
  },

  async getCorrelations() {
    const res = await fetch(`${API_BASE}/analytics/correlation`);
    if (!res.ok) throw new Error("Failed to fetch correlations");
    return res.json();
  },

  // Datasets
  async getDatasets(): Promise<DatasetItem[]> {
    const res = await fetch(`${API_BASE}/datasets`);
    if (!res.ok) throw new Error("Failed to fetch datasets list");
    return res.json();
  },

  async uploadDataset(file: File, description?: string) {
    const formData = new FormData();
    formData.append("file", file);
    if (description) formData.append("description", description);

    const res = await fetch(`${API_BASE}/datasets/upload`, {
      method: "POST",
      headers: getAuthHeader(),
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Upload failed" }));
      throw new Error(err.detail || "Upload failed");
    }
    return res.json();
  },

  async activateDataset(id: number) {
    const res = await fetch(`${API_BASE}/datasets/${id}/activate`, {
      method: "POST",
      headers: getAuthHeader(),
    });
    if (!res.ok) throw new Error("Failed to activate dataset");
    return res.json();
  },

  async profileDataset(id: number): Promise<QualityProfile> {
    const res = await fetch(`${API_BASE}/datasets/${id}/profile`, {
      method: "POST",
    });
    if (!res.ok) throw new Error("Failed to profile dataset");
    return res.json();
  },

  async cleanDataset(id: number, options: any, applyToDb = false) {
    const res = await fetch(`${API_BASE}/datasets/${id}/clean?apply_to_db=${applyToDb}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...getAuthHeader(),
      },
      body: JSON.stringify(options),
    });
    if (!res.ok) throw new Error("Failed to clean dataset");
    return res.json();
  },

  async deleteDataset(id: number) {
    const res = await fetch(`${API_BASE}/datasets/${id}`, {
      method: "DELETE",
      headers: getAuthHeader(),
    });
    if (!res.ok) throw new Error("Failed to delete dataset");
    return res.json();
  },

  // Reports
  async getReports() {
    const res = await fetch(`${API_BASE}/reports`);
    if (!res.ok) throw new Error("Failed to fetch reports");
    return res.json();
  },

  async generateReport(payload: any) {
    const res = await fetch(`${API_BASE}/reports/generate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error("Report generation failed");
    return res.json();
  },

  getReportDownloadUrl(id: number) {
    return `${API_BASE}/reports/${id}/download`;
  },

  // System
  async getSystemStatus(): Promise<SystemStatus> {
    const res = await fetch(`${API_BASE}/system/status`);
    if (!res.ok) throw new Error("Failed to fetch system status");
    return res.json();
  },

  async getDataFreshness(): Promise<DataFreshness> {
    const res = await fetch(`${API_BASE}/system/data-freshness`);
    if (!res.ok) throw new Error("Failed to fetch data freshness");
    return res.json();
  },

  async getLogs(limit = 50) {
    const res = await fetch(`${API_BASE}/system/logs?limit=${limit}`);
    if (!res.ok) throw new Error("Failed to fetch system logs");
    return res.json();
  },
};
