"use client";

import { useEffect, useState } from "react";
import { TopNav } from "@/components/layout/TopNav";
import { GlobalFilterBar } from "@/components/layout/GlobalFilterBar";
import { KPICard } from "@/components/dashboard/KPICard";
import { EChartComponent } from "@/components/charts/EChartComponent";
import { TrafficLoadingAnimation } from "@/components/shared/TrafficLoadingAnimation";
import { api } from "@/services/api";
import { OverviewData, FilterState } from "@/types";
import {
  Car,
  AlertTriangle,
  UserX,
  HeartPulse,
  Percent,
  Calendar,
  Sparkles,
  MapPin,
  Clock,
} from "lucide-react";

export default function OverviewPage() {
  const [data, setData] = useState<OverviewData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [filters, setFilters] = useState<FilterState>({
    state: "All",
    severity: "All",
    year: 0,
    weather: "All",
    road_type: "All",
  });

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await api.getOverview(filters);
      setData(res);
    } catch (err: any) {
      setError(err.message || "Failed to load dashboard overview");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [filters]);

  const handleResetFilters = () => {
    setFilters({
      state: "All",
      severity: "All",
      year: 0,
      weather: "All",
      road_type: "All",
    });
  };

  // ECharts Option for Multi-Year Trend in Light Theme
  const getTrendChartOption = () => {
    if (!data?.yearly_trend || data.yearly_trend.length === 0) return {};

    const years = data.yearly_trend.map((d: any) => d.year);
    const accidents = data.yearly_trend.map((d: any) => d.total_accidents);
    const fatalities = data.yearly_trend.map((d: any) => d.fatalities);
    const injuries = data.yearly_trend.map((d: any) => d.injuries);

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
      legend: {
        data: ["Accidents", "Fatalities", "Injuries"],
        textStyle: { color: "#475569", fontSize: 11 },
        top: 0,
        right: 10,
      },
      grid: {
        left: "3%",
        right: "4%",
        bottom: "3%",
        top: "15%",
        containLabel: true,
      },
      xAxis: {
        type: "category",
        data: years,
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
          name: "Accidents",
          type: "line",
          smooth: true,
          data: accidents,
          itemStyle: { color: "#0a545c" },
          lineStyle: { width: 3 },
          symbolSize: 6,
        },
        {
          name: "Fatalities",
          type: "line",
          smooth: true,
          data: fatalities,
          itemStyle: { color: "#dc2626" },
          lineStyle: { width: 3 },
          symbolSize: 6,
        },
        {
          name: "Injuries",
          type: "line",
          smooth: true,
          data: injuries,
          itemStyle: { color: "#d97706" },
          lineStyle: { width: 3 },
          symbolSize: 6,
        },
      ],
    };
  };

  // ECharts Option for Severity Donut in Light Theme
  const getSeverityDonutOption = () => {
    if (!data?.severity_breakdown || data.severity_breakdown.length === 0) return {};

    const colorMap: Record<string, string> = {
      Fatal: "#dc2626",
      "Grievous Injury": "#d97706",
      "Minor Injury": "#0a545c",
      "Property Damage Only": "#64748b",
    };

    const chartData = data.severity_breakdown.map((s: any) => ({
      name: s.accident_severity,
      value: s.accident_count,
    }));

    return {
      backgroundColor: "transparent",
      tooltip: {
        trigger: "item",
        backgroundColor: "#ffffff",
        borderColor: "#e2e8f0",
        borderWidth: 1,
        textStyle: { color: "#0f172a", fontSize: 12 },
        extraCssText: "box-shadow: 0 4px 12px rgba(15, 23, 42, 0.08); border-radius: 8px;",
        formatter: "{b}: {c} crashes ({d}%)",
      },
      legend: {
        orient: "horizontal",
        bottom: 0,
        textStyle: { color: "#475569", fontSize: 10 },
      },
      series: [
        {
          name: "Crash Severity",
          type: "pie",
          radius: ["45%", "72%"],
          center: ["50%", "45%"],
          avoidLabelOverlap: false,
          itemStyle: {
            borderRadius: 6,
            borderColor: "#ffffff",
            borderWidth: 2,
            color: (params: any) => colorMap[params.name] || "#64748b",
          },
          label: { show: false },
          emphasis: {
            label: {
              show: true,
              fontSize: 12,
              fontWeight: "bold",
              color: "#0f172a",
            },
          },
          data: chartData,
        },
      ],
    };
  };

  return (
    <div className="flex-1 flex flex-col min-h-screen bg-[#f4f6f8]">
      <TopNav
        onRefresh={fetchData}
        datasetName={data?.kpis ? "Active Ingested Dataset" : undefined}
        coveragePeriod={data?.kpis?.data_coverage_period}
      />

      <div className="p-6 max-w-[1600px] mx-auto w-full">
        {/* Global Filter Bar */}
        {data?.filter_options && (
          <GlobalFilterBar
            options={data.filter_options}
            filters={filters}
            onChange={setFilters}
            onReset={handleResetFilters}
          />
        )}

        {/* Error State */}
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 text-red-700 p-4 rounded-xl text-sm flex items-center justify-between shadow-xs">
            <span className="font-medium">{error}</span>
            <button
              onClick={fetchData}
              className="px-3 py-1 bg-red-100 hover:bg-red-200 text-red-800 rounded text-xs font-semibold transition"
            >
              Retry
            </button>
          </div>
        )}

        {/* Interactive Loading State with Custom Bike Animation */}
        {loading && !data && (
          <div className="bg-white border border-slate-200/90 rounded-xl p-8 mb-6 shadow-xs">
            <TrafficLoadingAnimation
              message="Simulating Crash Dynamics & Ingesting Fleet Records..."
              subtext="Computing 24hr Diurnal Heatmaps & Executive Road Safety KPIs"
            />
          </div>
        )}

        {/* Dynamic Executive KPIs */}
        {data?.kpis && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4 mb-6">
            <KPICard
              title="Total Crashes"
              value={data.kpis.total_accidents}
              icon={Car}
              deltaPct={data.kpis.accidents_delta_pct}
              accentColor="cyan"
            />
            <KPICard
              title="Fatalities"
              value={data.kpis.total_fatalities}
              icon={AlertTriangle}
              deltaPct={data.kpis.fatalities_delta_pct}
              accentColor="red"
            />
            <KPICard
              title="Injured Persons"
              value={data.kpis.total_injured}
              icon={UserX}
              deltaPct={data.kpis.injured_delta_pct}
              accentColor="amber"
            />
            <KPICard
              title="Total Casualties"
              value={data.kpis.total_casualties}
              icon={HeartPulse}
              subtitle="Deaths + Injuries"
              accentColor="blue"
            />
            <KPICard
              title="Fatality Rate"
              value={`${data.kpis.fatality_rate_pct}%`}
              icon={Percent}
              subtitle="Per 100 crashes"
              accentColor="red"
            />
            <KPICard
              title="Crashes / Day"
              value={data.kpis.avg_accidents_per_day}
              icon={Calendar}
              subtitle="Daily average"
              accentColor="emerald"
            />
          </div>
        )}

        {/* Secondary Context Banner: Most Impacted Region & Diurnal Window */}
        {data?.kpis && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            <div className="bg-white border border-slate-200 rounded-xl p-4 flex items-center gap-4 shadow-xs">
              <div className="w-10 h-10 rounded-lg bg-teal-50 border border-teal-200 flex items-center justify-center shrink-0">
                <MapPin className="w-5 h-5 text-brand-teal" />
              </div>
              <div>
                <span className="text-[10px] uppercase font-mono tracking-wider text-slate-500 font-semibold block">
                  Most Impacted Region
                </span>
                <span className="text-sm font-bold text-slate-900 block mt-0.5">
                  {data.kpis.most_affected_region}
                </span>
              </div>
            </div>

            <div className="bg-white border border-slate-200 rounded-xl p-4 flex items-center gap-4 shadow-xs">
              <div className="w-10 h-10 rounded-lg bg-amber-50 border border-amber-200 flex items-center justify-center shrink-0">
                <Clock className="w-5 h-5 text-amber-600" />
              </div>
              <div>
                <span className="text-[10px] uppercase font-mono tracking-wider text-slate-500 font-semibold block">
                  Peak Diurnal Crash Window
                </span>
                <span className="text-sm font-bold text-slate-900 block mt-0.5">
                  {data.kpis.most_affected_time_window}
                </span>
              </div>
            </div>
          </div>
        )}

        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
          {/* Multi-Year Trend Chart (2 columns) */}
          <div className="lg:col-span-2 bg-white border border-slate-200 rounded-xl p-5 shadow-xs">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-sm font-bold text-slate-900 tracking-wide">
                  Longitudinal Accident & Casualty Trajectory
                </h3>
                <p className="text-xs text-slate-500 mt-0.5">
                  Annual crash volume mapped alongside recorded fatality and injury counts
                </p>
              </div>
            </div>
            {loading && !data ? (
              <div className="h-[320px] flex items-center justify-center">
                <TrafficLoadingAnimation compact />
              </div>
            ) : (
              <EChartComponent option={getTrendChartOption()} style={{ height: "320px", width: "100%" }} />
            )}
          </div>

          {/* Severity Breakdown Donut (1 column) */}
          <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-sm font-bold text-slate-900 tracking-wide">
                  Accident Severity Distribution
                </h3>
                <p className="text-xs text-slate-500 mt-0.5">
                  Categorical breakdown of crash impact severity
                </p>
              </div>
            </div>
            {loading && !data ? (
              <div className="h-[320px] flex items-center justify-center">
                <TrafficLoadingAnimation compact />
              </div>
            ) : (
              <EChartComponent option={getSeverityDonutOption()} style={{ height: "320px", width: "100%" }} />
            )}
          </div>
        </div>

        {/* Bottom Row: Regional Crash Rankings & Dynamic Analytical Observations */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Regional Table */}
          <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs">
            <h3 className="text-sm font-bold text-slate-900 tracking-wide mb-1">
              Top Impacted States / Regions
            </h3>
            <p className="text-xs text-slate-500 mb-4">
              Aggregated accident volume and severity by administrative jurisdiction
            </p>

            <div className="overflow-x-auto">
              <table className="w-full text-xs text-left">
                <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 uppercase font-mono text-[10px]">
                  <tr>
                    <th className="py-2.5 px-3">State / Jurisdiction</th>
                    <th className="py-2.5 px-3 text-right">Crashes</th>
                    <th className="py-2.5 px-3 text-right">Fatalities</th>
                    <th className="py-2.5 px-3 text-right">Injured</th>
                    <th className="py-2.5 px-3 text-right">Fatality Rate</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {data?.top_states?.map((st: any) => (
                    <tr key={st.state} className="hover:bg-slate-50/80 transition">
                      <td className="py-2.5 px-3 font-semibold text-slate-800">{st.state}</td>
                      <td className="py-2.5 px-3 text-right font-mono text-slate-700">{st.total_accidents?.toLocaleString()}</td>
                      <td className="py-2.5 px-3 text-right font-mono text-red-600 font-bold">
                        {st.fatalities?.toLocaleString()}
                      </td>
                      <td className="py-2.5 px-3 text-right font-mono text-amber-600 font-medium">
                        {st.injuries?.toLocaleString()}
                      </td>
                      <td className="py-2.5 px-3 text-right font-mono text-slate-600">
                        {st.fatality_rate_pct?.toFixed(1)}%
                      </td>
                    </tr>
                  ))}
                  {(!data?.top_states || data.top_states.length === 0) && (
                    <tr>
                      <td colSpan={5} className="py-6 text-center text-slate-500">
                        No regional data available for the selected filters.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>

          {/* Analytical Observations Card */}
          <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs flex flex-col justify-between">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <Sparkles className="w-4 h-4 text-brand-teal" />
                <h3 className="text-sm font-bold text-slate-900 tracking-wide">
                  Python-Computed Analytical Observations
                </h3>
              </div>
              <p className="text-xs text-slate-500 mb-4">
                Dynamic data-driven findings generated directly from active dataset calculations
              </p>

              <div className="space-y-3">
                {data?.recent_observations?.map((obs, idx) => (
                  <div
                    key={idx}
                    className="p-3 rounded-lg bg-slate-50 border border-slate-200/90 text-xs text-slate-700 leading-relaxed flex items-start gap-2.5"
                  >
                    <span className="w-2 h-2 rounded-full bg-brand-teal mt-1.5 shrink-0"></span>
                    <span>{obs}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-400 font-mono">
              <span>Analytical Engine: Python 3.15 + Pandas</span>
              <span>Backend: FastAPI + Neon PostgreSQL</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
