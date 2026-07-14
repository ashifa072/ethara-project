const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

async function fetchAPI<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(error.detail || `API error: ${res.status}`);
  }
  return res.json();
}

export interface Project {
  id: number;
  name: string;
  description?: string;
  manager_name?: string;
  status: string;
}

export interface SeatBrief {
  id: number;
  floor: number;
  zone: string;
  bay: string;
  seat_number: string;
  status: string;
}

export interface Employee {
  id: number;
  employee_code: string;
  name: string;
  email: string;
  department: string;
  role: string;
  joining_date: string;
  status: string;
  project_id?: number;
  project?: { id: number; name: string };
  active_seat?: SeatBrief;
}

export interface Seat {
  id: number;
  floor: number;
  zone: string;
  bay: string;
  seat_number: string;
  status: string;
  allocated_employee?: { id: number; name: string; email: string };
  allocated_project?: { id: number; name: string };
}

export interface DashboardSummary {
  total_employees: number;
  total_seats: number;
  occupied_seats: number;
  available_seats: number;
  reserved_seats: number;
  maintenance_seats: number;
  pending_allocation: number;
}

export interface ProjectUtilization {
  project_id: number;
  project_name: string;
  employee_count: number;
  occupied_seats: number;
}

export interface FloorUtilization {
  floor: number;
  total_seats: number;
  occupied_seats: number;
  available_seats: number;
  reserved_seats: number;
  occupancy_rate: number;
}

export interface PaginatedEmployees {
  total: number;
  page: number;
  page_size: number;
  items: Employee[];
}

export interface PaginatedSeats {
  total: number;
  page: number;
  page_size: number;
  items: Seat[];
}

export interface SeatSuggestion {
  seat: SeatBrief;
  reason: string;
  proximity_score: number;
}

export const api = {
  getDashboardSummary: () => fetchAPI<DashboardSummary>("/dashboard/summary"),
  getProjectUtilization: () => fetchAPI<ProjectUtilization[]>("/dashboard/project-utilization"),
  getFloorUtilization: () => fetchAPI<FloorUtilization[]>("/dashboard/floor-utilization"),

  getEmployees: (params?: Record<string, string | number>) => {
    const query = params ? "?" + new URLSearchParams(params as Record<string, string>).toString() : "";
    return fetchAPI<PaginatedEmployees>(`/employees${query}`);
  },
  getEmployee: (id: number) => fetchAPI<Employee>(`/employees/${id}`),
  createEmployee: (data: Partial<Employee>) =>
    fetchAPI<Employee>("/employees", { method: "POST", body: JSON.stringify(data) }),
  updateEmployee: (id: number, data: Partial<Employee>) =>
    fetchAPI<Employee>(`/employees/${id}`, { method: "PUT", body: JSON.stringify(data) }),
  deactivateEmployee: (id: number) =>
    fetchAPI<Employee>(`/employees/${id}`, { method: "DELETE" }),
  getSeatSuggestions: (employeeId: number) =>
    fetchAPI<SeatSuggestion[]>(`/employees/${employeeId}/seat-suggestions`),

  getProjects: () => fetchAPI<Project[]>("/projects"),
  getProjectEmployees: (projectId: number) => fetchAPI<Employee[]>(`/projects/${projectId}/employees`),

  getSeats: (params?: Record<string, string | number>) => {
    const query = params ? "?" + new URLSearchParams(params as Record<string, string>).toString() : "";
    return fetchAPI<PaginatedSeats>(`/seats${query}`);
  },
  getAvailableSeats: (params?: Record<string, string | number>) => {
    const query = params ? "?" + new URLSearchParams(params as Record<string, string>).toString() : "";
    return fetchAPI<Seat[]>(`/seats/available${query}`);
  },
  allocateSeat: (employeeId: number, seatId: number, projectId?: number) =>
    fetchAPI<{ message: string }>("/seats/allocate", {
      method: "POST",
      body: JSON.stringify({ employee_id: employeeId, seat_id: seatId, project_id: projectId }),
    }),
  releaseSeat: (employeeId: number) =>
    fetchAPI<{ message: string }>("/seats/release", {
      method: "POST",
      body: JSON.stringify({ employee_id: employeeId }),
    }),

  aiQuery: (query: string) =>
    fetchAPI<{ answer: string; intent?: string }>("/ai/query", {
      method: "POST",
      body: JSON.stringify({ query }),
    }),
};
