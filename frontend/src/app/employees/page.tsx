"use client";

import { useCallback, useEffect, useState } from "react";
import PageLayout from "@/components/PageLayout";
import { api, Employee, Project } from "@/lib/api";

export default function EmployeesPage() {
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [projectFilter, setProjectFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [floorFilter, setFloorFilter] = useState("");

  const loadEmployees = useCallback(async () => {
    setLoading(true);
    try {
      const params: Record<string, string | number> = { page, page_size: 20 };
      if (search) params.search = search;
      if (projectFilter) params.project_id = projectFilter;
      if (statusFilter) params.status = statusFilter;
      if (floorFilter) params.floor = floorFilter;

      const data = await api.getEmployees(params);
      setEmployees(data.items);
      setTotal(data.total);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }, [page, search, projectFilter, statusFilter, floorFilter]);

  useEffect(() => {
    api.getProjects().then(setProjects).catch(console.error);
  }, []);

  useEffect(() => {
    const timer = setTimeout(loadEmployees, 300);
    return () => clearTimeout(timer);
  }, [loadEmployees]);

  const statusBadge = (status: string) => {
    const colors: Record<string, string> = {
      active: "bg-green-100 text-green-800",
      inactive: "bg-gray-100 text-gray-800",
      pending_allocation: "bg-yellow-100 text-yellow-800",
    };
    return (
      <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${colors[status] || "bg-gray-100"}`}>
        {status.replace("_", " ")}
      </span>
    );
  };

  return (
    <PageLayout title="Employees" subtitle="Search and manage employee records and seat assignments">
      <div className="mb-6 flex flex-wrap gap-3">
        <input
          type="text"
          placeholder="Search by name, email, or ID..."
          value={search}
          onChange={(e) => { setSearch(e.target.value); setPage(1); }}
          className="rounded-lg border border-slate-300 px-4 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
        />
        <select
          value={projectFilter}
          onChange={(e) => { setProjectFilter(e.target.value); setPage(1); }}
          className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
        >
          <option value="">All Projects</option>
          {projects.map((p) => (
            <option key={p.id} value={p.id}>{p.name}</option>
          ))}
        </select>
        <select
          value={statusFilter}
          onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }}
          className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
        >
          <option value="">All Statuses</option>
          <option value="active">Active</option>
          <option value="pending_allocation">Pending Allocation</option>
          <option value="inactive">Inactive</option>
        </select>
        <select
          value={floorFilter}
          onChange={(e) => { setFloorFilter(e.target.value); setPage(1); }}
          className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
        >
          <option value="">All Floors</option>
          {[1, 2, 3, 4, 5].map((f) => (
            <option key={f} value={f}>Floor {f}</option>
          ))}
        </select>
      </div>

      <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
        <table className="w-full text-sm">
          <thead className="bg-slate-50">
            <tr className="text-left text-slate-500">
              <th className="px-4 py-3 font-medium">Employee ID</th>
              <th className="px-4 py-3 font-medium">Name</th>
              <th className="px-4 py-3 font-medium">Email</th>
              <th className="px-4 py-3 font-medium">Department</th>
              <th className="px-4 py-3 font-medium">Project</th>
              <th className="px-4 py-3 font-medium">Seat</th>
              <th className="px-4 py-3 font-medium">Status</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={7} className="px-4 py-8 text-center text-slate-400">Loading...</td>
              </tr>
            ) : employees.length === 0 ? (
              <tr>
                <td colSpan={7} className="px-4 py-8 text-center text-slate-400">No employees found</td>
              </tr>
            ) : (
              employees.map((emp) => (
                <tr key={emp.id} className="border-t border-slate-100 hover:bg-slate-50">
                  <td className="px-4 py-3 font-mono text-xs">{emp.employee_code}</td>
                  <td className="px-4 py-3 font-medium text-slate-900">{emp.name}</td>
                  <td className="px-4 py-3 text-slate-600">{emp.email}</td>
                  <td className="px-4 py-3 text-slate-600">{emp.department}</td>
                  <td className="px-4 py-3 text-slate-600">{emp.project?.name || "—"}</td>
                  <td className="px-4 py-3 text-slate-600">
                    {emp.active_seat
                      ? `F${emp.active_seat.floor} ${emp.active_seat.zone}-${emp.active_seat.seat_number}`
                      : "—"}
                  </td>
                  <td className="px-4 py-3">{statusBadge(emp.status)}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      <div className="mt-4 flex items-center justify-between">
        <p className="text-sm text-slate-500">{total.toLocaleString()} employees total</p>
        <div className="flex gap-2">
          <button
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page === 1}
            className="rounded-lg border border-slate-300 px-3 py-1 text-sm disabled:opacity-50"
          >
            Previous
          </button>
          <span className="px-3 py-1 text-sm text-slate-600">Page {page}</span>
          <button
            onClick={() => setPage((p) => p + 1)}
            disabled={employees.length < 20}
            className="rounded-lg border border-slate-300 px-3 py-1 text-sm disabled:opacity-50"
          >
            Next
          </button>
        </div>
      </div>
    </PageLayout>
  );
}
