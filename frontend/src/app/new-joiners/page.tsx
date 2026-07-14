"use client";

import { useCallback, useEffect, useState } from "react";
import PageLayout from "@/components/PageLayout";
import { api, Employee, Project, SeatSuggestion } from "@/lib/api";

export default function NewJoinersPage() {
  const [pendingEmployees, setPendingEmployees] = useState<Employee[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedEmployee, setSelectedEmployee] = useState<Employee | null>(null);
  const [suggestions, setSuggestions] = useState<SeatSuggestion[]>([]);
  const [loading, setLoading] = useState(true);
  const [allocating, setAllocating] = useState(false);
  const [message, setMessage] = useState("");
  const [showAddForm, setShowAddForm] = useState(false);
  const [formData, setFormData] = useState({
    employee_code: "",
    name: "",
    email: "",
    department: "Engineering",
    role: "Software Engineer",
    joining_date: new Date().toISOString().split("T")[0],
    project_id: "",
  });

  const loadPending = useCallback(async () => {
    setLoading(true);
    try {
      const data = await api.getEmployees({ status: "pending_allocation", page_size: 100 });
      setPendingEmployees(data.items);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    api.getProjects().then(setProjects).catch(console.error);
    loadPending();
  }, [loadPending]);

  const handleSelectEmployee = async (emp: Employee) => {
    setSelectedEmployee(emp);
    setMessage("");
    try {
      const sug = await api.getSeatSuggestions(emp.id);
      setSuggestions(sug);
    } catch (e) {
      setSuggestions([]);
      setMessage("Failed to load seat suggestions");
    }
  };

  const handleAllocate = async (seatId: number) => {
    if (!selectedEmployee) return;
    setAllocating(true);
    setMessage("");
    try {
      await api.allocateSeat(selectedEmployee.id, seatId, selectedEmployee.project_id);
      setMessage(`Seat allocated successfully for ${selectedEmployee.name}!`);
      setSelectedEmployee(null);
      setSuggestions([]);
      loadPending();
    } catch (e: unknown) {
      setMessage(e instanceof Error ? e.message : "Allocation failed");
    } finally {
      setAllocating(false);
    }
  };

  const handleAddEmployee = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.createEmployee({
        ...formData,
        project_id: formData.project_id ? Number(formData.project_id) : undefined,
        status: "pending_allocation",
      });
      setMessage("New employee added successfully!");
      setShowAddForm(false);
      setFormData({
        employee_code: "",
        name: "",
        email: "",
        department: "Engineering",
        role: "Software Engineer",
        joining_date: new Date().toISOString().split("T")[0],
        project_id: "",
      });
      loadPending();
    } catch (e: unknown) {
      setMessage(e instanceof Error ? e.message : "Failed to add employee");
    }
  };

  return (
    <PageLayout
      title="New Joiner Allocation"
      subtitle="Add new employees and allocate seats based on project proximity"
    >
      {message && (
        <div className={`mb-4 rounded-lg p-3 text-sm ${message.includes("success") ? "bg-green-50 text-green-700" : "bg-red-50 text-red-700"}`}>
          {message}
        </div>
      )}

      <div className="mb-6">
        <button
          onClick={() => setShowAddForm(!showAddForm)}
          className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700"
        >
          {showAddForm ? "Cancel" : "+ Add New Employee"}
        </button>
      </div>

      {showAddForm && (
        <form onSubmit={handleAddEmployee} className="mb-8 rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <h3 className="mb-4 text-lg font-semibold">Add New Employee</h3>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <input required placeholder="Employee Code" value={formData.employee_code} onChange={(e) => setFormData({ ...formData, employee_code: e.target.value })} className="rounded-lg border px-3 py-2 text-sm" />
            <input required placeholder="Full Name" value={formData.name} onChange={(e) => setFormData({ ...formData, name: e.target.value })} className="rounded-lg border px-3 py-2 text-sm" />
            <input required type="email" placeholder="Email" value={formData.email} onChange={(e) => setFormData({ ...formData, email: e.target.value })} className="rounded-lg border px-3 py-2 text-sm" />
            <select value={formData.department} onChange={(e) => setFormData({ ...formData, department: e.target.value })} className="rounded-lg border px-3 py-2 text-sm">
              {["Engineering", "Product", "Design", "HR", "Finance", "Operations", "Growth"].map((d) => (
                <option key={d} value={d}>{d}</option>
              ))}
            </select>
            <input placeholder="Role" value={formData.role} onChange={(e) => setFormData({ ...formData, role: e.target.value })} className="rounded-lg border px-3 py-2 text-sm" />
            <input required type="date" value={formData.joining_date} onChange={(e) => setFormData({ ...formData, joining_date: e.target.value })} className="rounded-lg border px-3 py-2 text-sm" />
            <select value={formData.project_id} onChange={(e) => setFormData({ ...formData, project_id: e.target.value })} className="rounded-lg border px-3 py-2 text-sm">
              <option value="">Select Project</option>
              {projects.map((p) => (
                <option key={p.id} value={p.id}>{p.name}</option>
              ))}
            </select>
          </div>
          <button type="submit" className="mt-4 rounded-lg bg-green-600 px-4 py-2 text-sm font-medium text-white hover:bg-green-700">
            Add Employee
          </button>
        </form>
      )}

      <div className="grid grid-cols-1 gap-8 lg:grid-cols-2">
        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <h3 className="mb-4 text-lg font-semibold">Pending Allocation ({pendingEmployees.length})</h3>
          {loading ? (
            <p className="text-slate-400">Loading...</p>
          ) : pendingEmployees.length === 0 ? (
            <p className="text-slate-400">No employees pending allocation</p>
          ) : (
            <div className="max-h-96 space-y-2 overflow-y-auto">
              {pendingEmployees.map((emp) => (
                <button
                  key={emp.id}
                  onClick={() => handleSelectEmployee(emp)}
                  className={`w-full rounded-lg border p-3 text-left transition-colors ${
                    selectedEmployee?.id === emp.id
                      ? "border-indigo-500 bg-indigo-50"
                      : "border-slate-200 hover:bg-slate-50"
                  }`}
                >
                  <p className="font-medium text-slate-900">{emp.name}</p>
                  <p className="text-xs text-slate-500">{emp.email} · {emp.project?.name || "No project"}</p>
                </button>
              ))}
            </div>
          )}
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <h3 className="mb-4 text-lg font-semibold">Seat Suggestions</h3>
          {!selectedEmployee ? (
            <p className="text-slate-400">Select an employee to see seat suggestions</p>
          ) : suggestions.length === 0 ? (
            <p className="text-slate-400">No suggestions available</p>
          ) : (
            <div className="space-y-3">
              <p className="text-sm text-slate-600">
                Suggestions for <strong>{selectedEmployee.name}</strong>:
              </p>
              {suggestions.map((s, i) => (
                <div key={s.seat.id} className="flex items-center justify-between rounded-lg border border-slate-200 p-3">
                  <div>
                    <p className="font-medium text-slate-900">
                      Floor {s.seat.floor}, Zone {s.seat.zone}, Bay {s.seat.bay}, Seat {s.seat.seat_number}
                    </p>
                    <p className="text-xs text-slate-500">{s.reason}</p>
                    {i === 0 && (
                      <span className="mt-1 inline-block rounded bg-green-100 px-2 py-0.5 text-xs text-green-700">
                        Recommended
                      </span>
                    )}
                  </div>
                  <button
                    onClick={() => handleAllocate(s.seat.id)}
                    disabled={allocating}
                    className="rounded-lg bg-indigo-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-indigo-700 disabled:opacity-50"
                  >
                    Allocate
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </PageLayout>
  );
}
