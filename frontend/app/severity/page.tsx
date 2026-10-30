"use client";

import { useEffect, useState } from "react";
import { TopNav } from "@/components/layout/TopNav";
import { GlobalFilterBar } from "@/components/layout/GlobalFilterBar";
import { EChartComponent } from "@/components/charts/EChartComponent";
import { TrafficLoadingAnimation } from "@/components/shared/TrafficLoadingAnimation";
import { api } from "@/services/api";
import { SeverityData, FilterState, FilterOptions } from "@/types";
import { AlertTriangle, ShieldCheck, Car, CloudRain } from "lucide-react";

export default function SeverityPage() {
  const [data, setData] = useState<SeverityData | null>(null);
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

  const fetchSeverity = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await api.getSeverity(filters);
      setData(res);
    } catch (err: any) {
      setError(err.message || "Failed to load severity analytics");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSeverity();
  }, [filters]);

  // Vehicle Fatality Rate Option (Light Theme)
  const getVehicleOption = () => {
    if (!data?.by_vehicle || data.by_vehicle.length === 0) return {};
    const vehicles = data.by_vehicle.map((v: any) => v.primary_vehicle_type);
    const accidents = data.by_vehicle.map((v: any) => v.total_accidents);
    const rates = data.by_vehicle.map((v: any) => v.fatality_rate_pct);

    return {
      backgroundColor: "transparent",
      tooltip: {
        trigger: "axis",
        backgroundColor: "#ffffff",
        borderColor: "#e2e8f0",
        borderWidth: 1,
        textStyle: { color: "#0f172a", fontSize: 12 },
        extraCssText: "box-shadow: 0 4px 12px rgba(15, 23, 42, 0.08); border-radius: 8px;",
      },
      legend: { data: ["Total Crashes", "Fatality Rate (%)"], textStyle: { color: "#475569", fontSize: 11 }, top: 0, right: 10 },
      grid: { left: "3%", right: "4%", bottom: "14%", top: "15%", containLabel: true },
      xAxis: {
        type: "category",
        data: vehicles,
        axisLine: { lineStyle: { color: "#cbd5e1" } },
        axisLabel: { color: "#64748b", interval: 0, rotate: 20, fontSize: 10 },
      },
      yAxis: [
        { type: "value", splitLine: { lineStyle: { color: "#f1f5f9" } }, axisLabel: { color: "#64748b", fontSize: 11 } },
        { type: "value", splitLine: { show: false }, axisLabel: { color: "#dc2626", formatter: "{value}%", fontSize: 11 } },
      ],
      series: [
        {
          name: "Total Crashes",
          type: "bar",
          data: accidents,
          itemStyle: { color: "#0a545c", borderRadius: [4, 4, 0, 0] },
        },
        {
          name: "Fatality Rate (%)",
          type: "line",
          yAxisIndex: 1,
          data: rates,
          itemStyle: { color: "#dc2626" },
          lineStyle: { width: 3, color: "#dc2626" },
          symbolSize: 6,
        },
      ],
    };
  };

  // Road Type Fatality Rate Option (Light Theme)
  const getRoadTypeOption = () => {
    if (!data?.by_road_type || data.by_road_type.length === 0) return {};
    const roads = data.by_road_type.map((r: any) => r.road_type);
    const accidents = data.by_road_type.map((r: any) => r.total_accidents);
    const fatalities = data.by_road_type.map((r: any) => r.fatalities);

    return {
      backgroundColor: "transparent",
      tooltip: {
        trigger: "axis",
        backgroundColor: "#ffffff",
        borderColor: "#e2e8f0",
        borderWidth: 1,
        textStyle: { color: "#0f172a", fontSize: 12 },
        extraCssText: "box-shadow: 0 4px 12px rgba(15, 23, 42, 0.08); border-radius: 8px;",
      },
      legend: { data: ["Crashes", "Fatalities"], textStyle: { color: "#475569", fontSize: 11 }, top: 0, right: 10 },
      grid: { left: "3%", right: "4%", bottom: "10%", top: "15%", containLabel: true },
      xAxis: {
        type: "category",
        data: roads,
        axisLine: { lineStyle: { color: "#cbd5e1" } },
        axisLabel: { color: "#64748b", fontSize: 11 },
      },
      yAxis: {
        type: "value",
        splitLine: { lineStyle: { color: "#f1f5f9" } },
        axisLabel: { color: "#64748b", fontSize: 11 },
      },
      series: [
        {
          name: "Crashes",
          type: "bar",
          data: accidents,
          itemStyle: { color: "#0891b2", borderRadius: [4, 4, 0, 0] },
        },
        {
          name: "Fatalities",
          type: "bar",
          data: fatalities,
          itemStyle: { color: "#dc2626", borderRadius: [4, 4, 0, 0] },
        },
      ],
    };
  };

  return (
    <div className="flex-1 flex flex-col min-h-screen bg-[#f4f6f8]">
      <TopNav onRefresh={fetchSeverity} />

      <div className="p-6 max-w-[1600px] mx-auto w-full">
        <GlobalFilterBar
          options={filterOptions}
          filters={filters}
          onChange={setFilters}
          onReset={() => setFilters({ state: "All", severity: "All", year: 0, weather: "All", road_type: "All" })}
        />

        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 text-red-700 p-4 rounded-xl text-sm flex items-center justify-between shadow-xs">
            <span className="font-medium">{error}</span>
            <button onClick={fetchSeverity} className="px-3 py-1 bg-red-100 hover:bg-red-200 text-red-800 rounded text-xs font-semibold">
              Retry
            </button>
          </div>
        )}

        {/* Loading State with Custom Bike Animation */}
        {loading && !data && (
          <div className="bg-white border border-slate-200/90 rounded-xl p-8 mb-6 shadow-xs">
            <TrafficLoadingAnimation
              message="Computing Crash Lethality & Vulnerable Road User Shares..."
              subtext="Decoupling collision event totals from human casualty tallies"
            />
          </div>
        )}

        {/* Rigor Notice */}
        <div className="bg-teal-50/70 border border-teal-200/80 rounded-xl p-4 mb-6 flex items-start gap-3 shadow-xs">
          <ShieldCheck className="w-5 h-5 text-brand-teal shrink-0 mt-0.5" />
          <div className="text-xs text-slate-700 leading-relaxed font-medium">
            <strong className="text-slate-900 block mb-0.5 font-bold">Statistical Integrity Rule:</strong>
            Crash frequency measures incident occurrences, whereas casualty counts quantify human injury and fatality impact. 
            Never conflate the number of accidents with the number of casualties.
          </div>
        </div>

        {/* Severity Summary Cards */}
        {data?.distribution && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            {data.distribution.map((d: any) => {
              const isFatal = d.accident_severity === "Fatal";
              const isGrievous = d.accident_severity === "Grievous Injury";
              return (
                <div
                  key={d.accident_severity}
                  className={`bg-white border rounded-xl p-4 shadow-xs ${
                    isFatal
                      ? "border-red-200 bg-red-50/40"
                      : isGrievous
                      ? "border-amber-200 bg-amber-50/40"
                      : "border-slate-200"
                  }`}
                >
                  <span className="text-xs text-slate-500 block uppercase font-mono font-semibold">{d.accident_severity}</span>
                  <div className="text-2xl font-extrabold font-mono text-slate-900 mt-1">
                    {d.accident_count?.toLocaleString()}
                  </div>
                  <div className="text-xs text-slate-600 mt-2 flex items-center justify-between border-t border-slate-100 pt-2 font-medium">
                    <span>{d.pct_of_total_crashes}% of total crashes</span>
                    <span className="font-bold text-red-600">{d.fatalities} deaths</span>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* Charts: By Vehicle & Road Type */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-sm font-bold text-slate-900 tracking-wide">
                  Severity & Fatality Rate by Primary Vehicle Type
                </h3>
                <p className="text-xs text-slate-500 mt-0.5">
                  Assessing which vehicle categories produce disproportionately fatal outcomes
                </p>
              </div>
              <Car className="w-4 h-4 text-brand-teal" />
            </div>
            <EChartComponent option={getVehicleOption()} style={{ height: "320px", width: "100%" }} />
          </div>

          <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-sm font-bold text-slate-900 tracking-wide">
                  Crash Volume vs Fatalities by Road Classification
                </h3>
                <p className="text-xs text-slate-500 mt-0.5">
                  Highways, expressways, and urban arterial comparisons
                </p>
              </div>
              <AlertTriangle className="w-4 h-4 text-amber-600" />
            </div>
            <EChartComponent option={getRoadTypeOption()} style={{ height: "320px", width: "100%" }} />
          </div>
        </div>

        {/* Weather Conditions Table */}
        {data?.by_weather && (
          <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs">
            <div className="flex items-center justify-between mb-3">
              <div>
                <h3 className="text-sm font-bold text-slate-900 tracking-wide">
                  Crash Severity by Weather & Atmospheric Conditions
                </h3>
                <p className="text-xs text-slate-500 mt-0.5">
                  Evaluating atmospheric hazards on crash casualty proportions
                </p>
              </div>
              <CloudRain className="w-4 h-4 text-brand-teal" />
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-xs text-left">
                <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 uppercase font-mono text-[10px]">
                  <tr>
                    <th className="py-2.5 px-3">Weather Condition</th>
                    <th className="py-2.5 px-3 text-right">Crashes</th>
                    <th className="py-2.5 px-3 text-right">Fatalities</th>
                    <th className="py-2.5 px-3 text-right">Injuries</th>
                    <th className="py-2.5 px-3 text-right">Fatality Rate (%)</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {data.by_weather.map((w: any) => (
                    <tr key={w.weather} className="hover:bg-slate-50 transition">
                      <td className="py-2 px-3 font-semibold text-slate-800">{w.weather}</td>
                      <td className="py-2 px-3 text-right font-mono text-slate-700">{w.total_accidents?.toLocaleString()}</td>
                      <td className="py-2 px-3 text-right font-mono text-red-600 font-bold">{w.fatalities?.toLocaleString()}</td>
                      <td className="py-2 px-3 text-right font-mono text-amber-600 font-medium">{w.injuries?.toLocaleString()}</td>
                      <td className="py-2 px-3 text-right font-mono font-bold text-slate-800">{w.fatality_rate_pct?.toFixed(1)}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
