"use client";

import { useEffect, useState } from "react";
import { TopNav } from "@/components/layout/TopNav";
import { GlobalFilterBar } from "@/components/layout/GlobalFilterBar";
import { TrafficLoadingAnimation } from "@/components/shared/TrafficLoadingAnimation";
import { api } from "@/services/api";
import { FilterState, FilterOptions, PaginatedAccidents } from "@/types";
import {
  Search,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";

export default function AccidentsPage() {
  const [data, setData] = useState<PaginatedAccidents | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const pageSize = 20;

  const [filterOptions, setFilterOptions] = useState<FilterOptions>({
    states: [],
    severities: [],
    years: [],
    weather: [],
    road_types: [],
  });

  const [filters, setFilters] = useState<FilterState>({
    state: "All",
    severity: "All",
    year: 0,
    weather: "All",
    road_type: "All",
  });

  // Load filter options from overview
  useEffect(() => {
    api.getOverview().then((res) => {
      if (res.filter_options) setFilterOptions(res.filter_options);
    }).catch(() => {});
  }, []);

  const fetchAccidents = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await api.getAccidents(page, pageSize, search, filters);
      setData(res);
    } catch (err: any) {
      setError(err.message || "Failed to load accidents data");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAccidents();
  }, [page, filters]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchAccidents();
  };

  const getSeverityBadge = (severity?: string) => {
    const s = severity?.toLowerCase() || "";
    if (s.includes("fatal")) {
      return (
        <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-semibold bg-red-50 text-red-700 border border-red-200">
          Fatal Crash
        </span>
      );
    }
    if (s.includes("grievous")) {
      return (
        <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-amber-50 text-amber-700 border border-amber-200">
          Grievous Injury
        </span>
      );
    }
    if (s.includes("minor")) {
      return (
        <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-teal-50 text-brand-teal border border-teal-200">
          Minor Injury
        </span>
      );
    }
    return (
      <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-slate-100 text-slate-700 border border-slate-200">
        Property Damage
      </span>
    );
  };

  return (
    <div className="flex-1 flex flex-col min-h-screen bg-[#f4f6f8]">
      <TopNav onRefresh={fetchAccidents} />

      <div className="p-6 max-w-[1600px] mx-auto w-full">
        {/* Filter Bar */}
        <GlobalFilterBar
          options={filterOptions}
          filters={filters}
          onChange={(newF) => {
            setFilters(newF);
            setPage(1);
          }}
          onReset={() => {
            setFilters({ state: "All", severity: "All", year: 0, weather: "All", road_type: "All" });
            setSearch("");
            setPage(1);
          }}
        />

        {/* Search Header */}
        <div className="bg-white border border-slate-200 rounded-xl p-4 mb-6 flex flex-col md:flex-row items-center justify-between gap-4 shadow-xs">
          <form onSubmit={handleSearchSubmit} className="flex-1 w-full max-w-lg relative">
            <Search className="w-4 h-4 absolute left-3 top-3 text-slate-400" />
            <input
              type="text"
              placeholder="Search by ID, State, District, Collision Type, Vehicle or Cause..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-9 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-lg text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:border-brand-teal focus:bg-white transition shadow-2xs font-medium"
            />
          </form>

          <div className="text-xs text-slate-500 flex items-center gap-2 font-medium">
            <span>Showing</span>
            <span className="font-mono text-slate-900 font-bold">{data?.total?.toLocaleString() || 0}</span>
            <span>total records across filters</span>
          </div>
        </div>

        {/* Error message */}
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 text-red-700 p-4 rounded-xl text-sm flex items-center justify-between shadow-xs">
            <span className="font-medium">{error}</span>
            <button onClick={fetchAccidents} className="px-3 py-1 bg-red-100 hover:bg-red-200 text-red-800 rounded text-xs font-semibold">
              Retry
            </button>
          </div>
        )}

        {/* Loading State with Bike Animation */}
        {loading && !data && (
          <div className="bg-white border border-slate-200 rounded-xl p-8 mb-6 shadow-xs">
            <TrafficLoadingAnimation
              message="Indexing & Filtering 3,500 Accident Records..."
              subtext="Retrieving collision telemetry, vehicle categories, and casualty tallies"
            />
          </div>
        )}

        {/* Records Table */}
        <div className="bg-white border border-slate-200 rounded-xl shadow-xs overflow-hidden mb-6">
          <div className="overflow-x-auto">
            <table className="w-full text-xs text-left">
              <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 uppercase font-mono text-[10px]">
                <tr>
                  <th className="py-3 px-4">Accident ID</th>
                  <th className="py-3 px-4">Date</th>
                  <th className="py-3 px-4">Location</th>
                  <th className="py-3 px-4">Severity</th>
                  <th className="py-3 px-4 text-center">Casualties</th>
                  <th className="py-3 px-4">Collision Type</th>
                  <th className="py-3 px-4">Vehicle Category</th>
                  <th className="py-3 px-4">Contributing Factor</th>
                  <th className="py-3 px-4">Road / Weather</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {data?.records?.map((r) => (
                  <tr key={r.id} className="hover:bg-slate-50 transition">
                    <td className="py-3 px-4 font-mono text-brand-teal font-semibold">{r.accident_id}</td>
                    <td className="py-3 px-4 text-slate-600 font-mono">{r.accident_date}</td>
                    <td className="py-3 px-4">
                      <div className="font-semibold text-slate-800">{r.district || "N/A"}</div>
                      <div className="text-[10px] text-slate-500">{r.state || ""}</div>
                    </td>
                    <td className="py-3 px-4">{getSeverityBadge(r.accident_severity)}</td>
                    <td className="py-3 px-4 text-center">
                      <span className="font-mono text-red-600 font-bold">{r.fatalities_count} dead</span>
                      <span className="text-slate-400 mx-1">/</span>
                      <span className="font-mono text-amber-600 font-medium">{r.injured_count} injured</span>
                    </td>
                    <td className="py-3 px-4 text-slate-700 font-medium">{r.collision_type || "N/A"}</td>
                    <td className="py-3 px-4 text-slate-700">{r.primary_vehicle_type || "N/A"}</td>
                    <td className="py-3 px-4 text-slate-600 max-w-[200px] truncate" title={r.contributing_factor}>
                      {r.contributing_factor || "N/A"}
                    </td>
                    <td className="py-3 px-4 text-slate-600 text-[11px]">
                      <div className="font-medium text-slate-800">{r.road_type || "Standard Road"}</div>
                      <div className="text-[10px] text-slate-500">{r.weather || "Clear"}</div>
                    </td>
                  </tr>
                ))}
                {(!data?.records || data.records.length === 0) && (
                  <tr>
                    <td colSpan={9} className="py-12 text-center text-slate-500 font-medium">
                      {loading ? "Loading accident records..." : "No accident records found matching criteria."}
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          {data && data.total_pages > 1 && (
            <div className="p-4 border-t border-slate-100 flex items-center justify-between bg-slate-50/50 text-xs">
              <span className="text-slate-600 font-medium">
                Page <span className="font-bold text-slate-900">{data.page}</span> of{" "}
                <span className="font-bold text-slate-900">{data.total_pages}</span>
              </span>

              <div className="flex items-center gap-2">
                <button
                  disabled={data.page <= 1}
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  className="px-3 py-1.5 rounded-lg border border-slate-200 bg-white text-slate-700 hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed flex items-center gap-1 transition shadow-2xs font-medium"
                >
                  <ChevronLeft className="w-3.5 h-3.5" />
                  <span>Previous</span>
                </button>
                <button
                  disabled={data.page >= data.total_pages}
                  onClick={() => setPage((p) => Math.min(data.total_pages, p + 1))}
                  className="px-3 py-1.5 rounded-lg border border-slate-200 bg-white text-slate-700 hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed flex items-center gap-1 transition shadow-2xs font-medium"
                >
                  <span>Next</span>
                  <ChevronRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
