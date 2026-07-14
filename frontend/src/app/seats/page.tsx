"use client";

import { useCallback, useEffect, useState } from "react";
import PageLayout from "@/components/PageLayout";
import { api, Seat } from "@/lib/api";

export default function SeatsPage() {
  const [seats, setSeats] = useState<Seat[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [floorFilter, setFloorFilter] = useState("");
  const [zoneFilter, setZoneFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");

  const loadSeats = useCallback(async () => {
    setLoading(true);
    try {
      const params: Record<string, string | number> = { page, page_size: 25 };
      if (floorFilter) params.floor = floorFilter;
      if (zoneFilter) params.zone = zoneFilter;
      if (statusFilter) params.status = statusFilter;

      const data = await api.getSeats(params);
      setSeats(data.items);
      setTotal(data.total);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }, [page, floorFilter, zoneFilter, statusFilter]);

  useEffect(() => {
    loadSeats();
  }, [loadSeats]);

  const statusBadge = (status: string) => {
    const colors: Record<string, string> = {
      available: "bg-green-100 text-green-800",
      occupied: "bg-blue-100 text-blue-800",
      reserved: "bg-yellow-100 text-yellow-800",
      maintenance: "bg-red-100 text-red-800",
    };
    return (
      <span className={`rounded-full px-2 py-0.5 text-xs font-medium capitalize ${colors[status] || ""}`}>
        {status}
      </span>
    );
  };

  return (
    <PageLayout title="Seats" subtitle="Browse and filter seat inventory across all floors">
      <div className="mb-6 flex flex-wrap gap-3">
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
        <select
          value={zoneFilter}
          onChange={(e) => { setZoneFilter(e.target.value); setPage(1); }}
          className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
        >
          <option value="">All Zones</option>
          {["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"].map((z) => (
            <option key={z} value={z}>Zone {z}</option>
          ))}
        </select>
        <select
          value={statusFilter}
          onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }}
          className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
        >
          <option value="">All Statuses</option>
          <option value="available">Available</option>
          <option value="occupied">Occupied</option>
          <option value="reserved">Reserved</option>
          <option value="maintenance">Maintenance</option>
        </select>
      </div>

      <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
        <table className="w-full text-sm">
          <thead className="bg-slate-50">
            <tr className="text-left text-slate-500">
              <th className="px-4 py-3 font-medium">Floor</th>
              <th className="px-4 py-3 font-medium">Zone</th>
              <th className="px-4 py-3 font-medium">Bay</th>
              <th className="px-4 py-3 font-medium">Seat #</th>
              <th className="px-4 py-3 font-medium">Status</th>
              <th className="px-4 py-3 font-medium">Employee</th>
              <th className="px-4 py-3 font-medium">Project</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={7} className="px-4 py-8 text-center text-slate-400">Loading...</td>
              </tr>
            ) : seats.length === 0 ? (
              <tr>
                <td colSpan={7} className="px-4 py-8 text-center text-slate-400">No seats found</td>
              </tr>
            ) : (
              seats.map((seat) => (
                <tr key={seat.id} className="border-t border-slate-100 hover:bg-slate-50">
                  <td className="px-4 py-3">{seat.floor}</td>
                  <td className="px-4 py-3">{seat.zone}</td>
                  <td className="px-4 py-3">{seat.bay}</td>
                  <td className="px-4 py-3 font-mono text-xs">{seat.seat_number}</td>
                  <td className="px-4 py-3">{statusBadge(seat.status)}</td>
                  <td className="px-4 py-3 text-slate-600">{seat.allocated_employee?.name || "—"}</td>
                  <td className="px-4 py-3 text-slate-600">{seat.allocated_project?.name || "—"}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      <div className="mt-4 flex items-center justify-between">
        <p className="text-sm text-slate-500">{total.toLocaleString()} seats total</p>
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
            disabled={seats.length < 25}
            className="rounded-lg border border-slate-300 px-3 py-1 text-sm disabled:opacity-50"
          >
            Next
          </button>
        </div>
      </div>
    </PageLayout>
  );
}
