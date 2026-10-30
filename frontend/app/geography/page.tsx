"use client";

import { useEffect, useState } from "react";
import { TopNav } from "@/components/layout/TopNav";
import { GlobalFilterBar } from "@/components/layout/GlobalFilterBar";
import { MapLibreMap } from "@/components/maps/MapLibreMap";
import { TrafficLoadingAnimation } from "@/components/shared/TrafficLoadingAnimation";
import { api } from "@/services/api";
import { GeographyData, FilterState, FilterOptions } from "@/types";
import { MapPin, ShieldAlert } from "lucide-react";

export default function GeographyPage() {
  const [data, setData] = useState<GeographyData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

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

  useEffect(() => {
    api.getOverview().then((res) => {
      if (res.filter_options) setFilterOptions(res.filter_options);
    }).catch(() => {});
  }, []);

  const fetchGeoData = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await api.getGeography(filters);
      setData(res);
    } catch (err: any) {
      setError(err.message || "Failed to load geographical intelligence");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchGeoData();
  }, [filters]);

  return (
    <div className="flex-1 flex flex-col min-h-screen bg-[#f4f6f8]">
      <TopNav onRefresh={fetchGeoData} />

      <div className="p-3 sm:p-5 md:p-6 max-w-[1600px] mx-auto w-full">
        <GlobalFilterBar
          options={filterOptions}
          filters={filters}
          onChange={setFilters}
          onReset={() => setFilters({ state: "All", severity: "All", year: 0, weather: "All", road_type: "All" })}
        />

        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 text-red-700 p-4 rounded-xl text-sm flex items-center justify-between shadow-xs">
            <span className="font-medium">{error}</span>
            <button onClick={fetchGeoData} className="px-3 py-1 bg-red-100 hover:bg-red-200 text-red-800 rounded text-xs font-semibold">
              Retry
            </button>
          </div>
        )}

        {/* Loading State with Custom Bike Animation */}
        {loading && !data && (
          <div className="bg-white border border-slate-200/90 rounded-xl p-8 mb-6 shadow-xs">
            <TrafficLoadingAnimation
              message="Plotting Georeferenced Collision Points & Spatial Clusters..."
              subtext="Loading verified latitude/longitude coordinates & highway corridor blackspots"
            />
          </div>
        )}

        {/* Map Section */}
        <div className="bg-white border border-slate-200 rounded-xl p-3 sm:p-5 mb-6 shadow-xs">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-4">
            <div>
              <div className="flex items-center gap-2">
                <MapPin className="w-4 h-4 text-brand-teal" />
                <h3 className="text-sm font-bold text-slate-900 tracking-wide">
                  Geographical Hotspot & Incident Mapping
                </h3>
              </div>
              <p className="text-xs text-slate-500 mt-0.5 font-medium">
                Interactive spatial visualization of verified accident coordinates and severity distributions
              </p>
            </div>
            <div className="text-xs text-slate-600 font-mono font-semibold bg-slate-50 px-2.5 py-1 rounded-md border border-slate-200 self-start sm:self-auto">
              Plotting {data?.map_points?.length || 0} spatial incidents
            </div>
          </div>

          <MapLibreMap points={data?.map_points || []} className="w-full h-[380px] sm:h-[520px]" />
        </div>

        {/* Hotspot Corridors Cards */}
        {data?.hotspots && data.hotspots.length > 0 && (
          <div className="mb-6">
            <div className="flex items-center gap-2 mb-3">
              <ShieldAlert className="w-4 h-4 text-red-600" />
              <h3 className="text-sm font-bold text-slate-900 tracking-wide">
                Identified High-Risk Corridors & Blackspots
              </h3>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {data.hotspots.slice(0, 4).map((h, i) => (
                <div key={i} className="bg-white border border-slate-200 rounded-xl p-4 shadow-xs hover:border-red-300 transition">
                  <div className="flex items-start justify-between">
                    <span className="text-xs font-bold text-slate-800">{h.corridor}</span>
                    <span className="px-1.5 py-0.5 rounded text-[10px] font-mono font-semibold bg-red-50 text-red-700 border border-red-200">
                      {h.risk_level}
                    </span>
                  </div>
                  <div className="text-[11px] text-slate-500 mt-1 font-medium">{h.state}</div>
                  <div className="mt-3 pt-2 border-t border-slate-100 flex items-center justify-between text-xs font-mono">
                    <span className="text-slate-600">Crashes: <strong className="text-slate-900">{h.accidents}</strong></span>
                    <span className="text-red-600 font-bold">{h.fatalities} Fatalities</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* State Rankings Table & District Table */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* State Rankings */}
          <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs">
            <h3 className="text-sm font-bold text-slate-900 tracking-wide mb-1">State Risk Index Rankings</h3>
            <p className="text-xs text-slate-500 mb-4">Composite risk calculation (Accidents × 0.4 + Fatalities × 2.5 + Injuries × 0.8)</p>
            <div className="overflow-x-auto">
              <table className="w-full text-xs text-left">
                <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 uppercase font-mono text-[10px]">
                  <tr>
                    <th className="py-2.5 px-3">State</th>
                    <th className="py-2.5 px-3 text-right">Crashes</th>
                    <th className="py-2.5 px-3 text-right">Fatalities</th>
                    <th className="py-2.5 px-3 text-right">Fatality Rate</th>
                    <th className="py-2.5 px-3 text-right">Risk Score</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {data?.states?.slice(0, 10).map((s: any) => (
                    <tr key={s.state} className="hover:bg-slate-50 transition">
                      <td className="py-2 px-3 font-semibold text-slate-800">{s.state}</td>
                      <td className="py-2 px-3 text-right font-mono text-slate-700">{s.total_accidents?.toLocaleString()}</td>
                      <td className="py-2 px-3 text-right font-mono text-red-600 font-bold">{s.fatalities?.toLocaleString()}</td>
                      <td className="py-2 px-3 text-right font-mono text-slate-600">{s.fatality_rate_pct?.toFixed(1)}%</td>
                      <td className="py-2 px-3 text-right font-mono font-bold text-brand-teal">{s.risk_score}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* District Rankings */}
          <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs">
            <h3 className="text-sm font-bold text-slate-900 tracking-wide mb-1">District / Urban Densities</h3>
            <p className="text-xs text-slate-500 mb-4">Top districts ranked by recorded accident volume</p>
            <div className="overflow-x-auto">
              <table className="w-full text-xs text-left">
                <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 uppercase font-mono text-[10px]">
                  <tr>
                    <th className="py-2.5 px-3">District</th>
                    <th className="py-2.5 px-3">State</th>
                    <th className="py-2.5 px-3 text-right">Crashes</th>
                    <th className="py-2.5 px-3 text-right">Fatalities</th>
                    <th className="py-2.5 px-3 text-right">Fatality Rate</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {data?.districts?.slice(0, 10).map((d: any) => (
                    <tr key={`${d.district}-${d.state}`} className="hover:bg-slate-50 transition">
                      <td className="py-2 px-3 font-semibold text-slate-800">{d.district}</td>
                      <td className="py-2 px-3 text-slate-500 font-medium">{d.state || ""}</td>
                      <td className="py-2 px-3 text-right font-mono text-slate-700">{d.total_accidents?.toLocaleString()}</td>
                      <td className="py-2 px-3 text-right font-mono text-red-600 font-bold">{d.fatalities?.toLocaleString()}</td>
                      <td className="py-2 px-3 text-right font-mono text-slate-600">{d.fatality_rate_pct?.toFixed(1)}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
