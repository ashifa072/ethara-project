"use client";

import { useEffect, useState } from "react";
import PageLayout from "@/components/PageLayout";
import StatCard from "@/components/StatCard";
import {
  api,
  DashboardSummary,
  FloorUtilization,
  ProjectUtilization,
} from "@/lib/api";

export default function DashboardPage() {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [projectUtil, setProjectUtil] = useState<ProjectUtilization[]>([]);
  const [floorUtil, setFloorUtil] = useState<FloorUtilization[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([
      api.getDashboardSummary(),
      api.getProjectUtilization(),
      api.getFloorUtilization(),
    ])
      .then(([s, p, f]) => {
        setSummary(s);
        setProjectUtil(p);
        setFloorUtil(f);
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <PageLayout title="Dashboard" subtitle="Overview of seat allocation and utilization">
        <div className="flex items-center justify-center py-20">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-indigo-600 border-t-transparent" />
        </div>
      </PageLayout>
    );
  }

  if (error) {
    return (
      <PageLayout title="Dashboard">
        <div className="rounded-lg bg-red-50 p-4 text-red-700">
          Failed to load dashboard: {error}. Ensure the backend is running on port 8000.
        </div>
      </PageLayout>
    );
  }

  const occupancyRate = summary
    ? ((summary.occupied_seats / summary.total_seats) * 100).toFixed(1)
    : "0";

  return (
    <PageLayout
      title="Dashboard"
      subtitle="Real-time overview of Ethara seat allocation and project mapping"
    >
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard title="Total Employees" value={summary!.total_employees} color="indigo" />
        <StatCard title="Total Seats" value={summary!.total_seats} color="blue" />
        <StatCard title="Occupied Seats" value={summary!.occupied_seats} subtitle={`${occupancyRate}% utilization`} color="green" />
        <StatCard title="Available Seats" value={summary!.available_seats} color="yellow" />
        <StatCard title="Reserved Seats" value={summary!.reserved_seats} color="purple" />
        <StatCard title="Maintenance" value={summary!.maintenance_seats} color="red" />
        <StatCard title="Pending Allocation" value={summary!.pending_allocation} subtitle="New joiners awaiting seats" color="red" />
      </div>

      <div className="mt-8 grid grid-cols-1 gap-8 lg:grid-cols-2">
        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="mb-4 text-lg font-semibold text-slate-900">Project-wise Seat Allocation</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-200 text-left text-slate-500">
                  <th className="pb-3 pr-4 font-medium">Project</th>
                  <th className="pb-3 pr-4 font-medium">Employees</th>
                  <th className="pb-3 font-medium">Occupied Seats</th>
                </tr>
              </thead>
              <tbody>
                {projectUtil.map((p) => (
                  <tr key={p.project_id} className="border-b border-slate-100">
                    <td className="py-3 pr-4 font-medium text-slate-900">{p.project_name}</td>
                    <td className="py-3 pr-4 text-slate-600">{p.employee_count}</td>
                    <td className="py-3 text-slate-600">{p.occupied_seats}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="mb-4 text-lg font-semibold text-slate-900">Floor-wise Occupancy</h2>
          <div className="space-y-4">
            {floorUtil.map((f) => (
              <div key={f.floor}>
                <div className="mb-1 flex justify-between text-sm">
                  <span className="font-medium text-slate-700">Floor {f.floor}</span>
                  <span className="text-slate-500">{f.occupancy_rate}% occupied</span>
                </div>
                <div className="h-3 overflow-hidden rounded-full bg-slate-100">
                  <div
                    className="h-full rounded-full bg-indigo-500 transition-all"
                    style={{ width: `${f.occupancy_rate}%` }}
                  />
                </div>
                <div className="mt-1 flex gap-4 text-xs text-slate-400">
                  <span>{f.occupied_seats} occupied</span>
                  <span>{f.available_seats} available</span>
                  <span>{f.reserved_seats} reserved</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </PageLayout>
  );
}
