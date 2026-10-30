"use client";

import { useEffect, useState } from "react";
import { TopNav } from "@/components/layout/TopNav";
import { GlobalFilterBar } from "@/components/layout/GlobalFilterBar";
import { EChartComponent } from "@/components/charts/EChartComponent";
import { TrafficLoadingAnimation } from "@/components/shared/TrafficLoadingAnimation";
import { api } from "@/services/api";
import { TrendData, FilterState, FilterOptions } from "@/types";
import { Clock, Calendar, TrendingUp } from "lucide-react";

export default function TrendsPage() {
  const [data, setData] = useState<TrendData | null>(null);
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

  const fetchTrends = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await api.getTrends(filters);
      setData(res);
    } catch (err: any) {
      setError(err.message || "Failed to load trends data");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTrends();
  }, [filters]);

  // Monthly Seasonality Option (Light Theme)
  const getMonthlyOption = () => {
    if (!data?.monthly || data.monthly.length === 0) return {};
    const months = data.monthly.map((m: any) => m.month.slice(0, 3));
    const counts = data.monthly.map((m: any) => m.total_accidents);
    const fatalities = data.monthly.map((m: any) => m.fatalities);

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
      grid: { left: "3%", right: "4%", bottom: "3%", top: "15%", containLabel: true },
      xAxis: {
        type: "category",
        data: months,
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
          data: counts,
          itemStyle: { color: "#0a545c", borderRadius: [4, 4, 0, 0] },
        },
        {
          name: "Fatalities",
          type: "line",
          data: fatalities,
          itemStyle: { color: "#dc2626" },
          lineStyle: { width: 2.5, color: "#dc2626" },
          symbolSize: 6,
        },
      ],
    };
  };

  // Day of Week Option (Light Theme)
  const getDayOfWeekOption = () => {
    if (!data?.day_of_week || data.day_of_week.length === 0) return {};
    const days = data.day_of_week.map((d: any) => d.day_of_week);
    const counts = data.day_of_week.map((d: any) => d.total_accidents);

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
      grid: { left: "3%", right: "4%", bottom: "3%", top: "10%", containLabel: true },
      xAxis: {
        type: "category",
        data: days,
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
          type: "bar",
          data: counts,
          itemStyle: {
            color: (params: any) => (params.name === "Saturday" || params.name === "Sunday" ? "#d97706" : "#0a545c"),
            borderRadius: [4, 4, 0, 0],
          },
        },
      ],
    };
  };

  // 24-Hour Diurnal Pattern Option (Light Theme)
  const getHourlyOption = () => {
    if (!data?.hourly || data.hourly.length === 0) return {};
    const hours = data.hourly.map((h: any) => `${h.hour_of_day}:00`);
    const counts = data.hourly.map((h: any) => h.total_accidents);

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
      grid: { left: "3%", right: "4%", bottom: "3%", top: "10%", containLabel: true },
      xAxis: {
        type: "category",
        data: hours,
        axisLine: { lineStyle: { color: "#cbd5e1" } },
        axisLabel: { color: "#64748b", interval: 2, fontSize: 11 },
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
          data: counts,
          itemStyle: { color: "#0a545c" },
          areaStyle: {
            color: {
              type: "linear",
              x: 0, y: 0, x2: 0, y2: 1,
              colorStops: [
                { offset: 0, color: "rgba(10, 84, 92, 0.2)" },
                { offset: 1, color: "rgba(10, 84, 92, 0.0)" },
              ],
            },
          },
          lineStyle: { width: 3 },
          symbolSize: 5,
        },
      ],
    };
  };

  // Day vs Hour Heatmap Option (Light Theme)
  const getHeatmapOption = () => {
    if (!data?.day_hour_heatmap || data.day_hour_heatmap.length === 0) return {};

    const days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
    const hours = Array.from({ length: 24 }, (_, i) => `${i}h`);
    const heatmapData = data.day_hour_heatmap.map((item: any) => [
      item.hour,
      item.day_index,
      item.count,
    ]);

    const maxVal = Math.max(...data.day_hour_heatmap.map((d: any) => d.count), 10);

    return {
      backgroundColor: "transparent",
      tooltip: {
        position: "top",
        backgroundColor: "#ffffff",
        borderColor: "#e2e8f0",
        borderWidth: 1,
        textStyle: { color: "#0f172a", fontSize: 12 },
        extraCssText: "box-shadow: 0 4px 12px rgba(15, 23, 42, 0.08); border-radius: 8px;",
        formatter: (params: any) =>
          `${days[params.data[1]]} at ${params.data[0]}:00<br/><strong>${params.data[2]} crashes</strong>`,
      },
      grid: { left: "4%", right: "4%", bottom: "12%", top: "5%", containLabel: true },
      xAxis: {
        type: "category",
        data: hours,
        splitArea: { show: true },
        axisLine: { lineStyle: { color: "#cbd5e1" } },
        axisLabel: { color: "#64748b", fontSize: 11 },
      },
      yAxis: {
        type: "category",
        data: days,
        splitArea: { show: true },
        axisLine: { lineStyle: { color: "#cbd5e1" } },
        axisLabel: { color: "#64748b", fontSize: 11 },
      },
      visualMap: {
        min: 0,
        max: maxVal,
        calculable: true,
        orient: "horizontal",
        left: "center",
        bottom: "0%",
        inRange: {
          color: ["#f8fafc", "#e0f2fe", "#38bdf8", "#f59e0b", "#dc2626"],
        },
        textStyle: { color: "#64748b", fontSize: 10 },
      },
      series: [
        {
          name: "Accidents",
          type: "heatmap",
          data: heatmapData,
          label: { show: false },
          emphasis: {
            itemStyle: { shadowBlur: 8, shadowColor: "rgba(0, 0, 0, 0.15)" },
          },
        },
      ],
    };
  };

  return (
    <div className="flex-1 flex flex-col min-h-screen bg-[#f4f6f8]">
      <TopNav onRefresh={fetchTrends} />

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
            <button onClick={fetchTrends} className="px-3 py-1 bg-red-100 hover:bg-red-200 text-red-800 rounded text-xs font-semibold">
              Retry
            </button>
          </div>
        )}

        {/* Loading State with Bike Animation */}
        {loading && !data && (
          <div className="bg-white border border-slate-200/90 rounded-xl p-8 mb-6 shadow-xs">
            <TrafficLoadingAnimation
              message="Decomposing Temporal Dynamics & 24hr Diurnal Heatmaps..."
              subtext="Aggregating collision frequency across months, weekdays, and hourly rush intervals"
            />
          </div>
        )}

        {/* Top Charts Row: Seasonality & Day of Week */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-sm font-bold text-slate-900 tracking-wide">
                  Monthly Seasonality Distribution
                </h3>
                <p className="text-xs text-slate-500 mt-0.5">
                  Aggregated crash incidence across calendar months
                </p>
              </div>
              <Calendar className="w-4 h-4 text-brand-teal" />
            </div>
            <EChartComponent option={getMonthlyOption()} style={{ height: "300px", width: "100%" }} />
          </div>

          <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-sm font-bold text-slate-900 tracking-wide">
                  Day-of-Week Distribution (Weekday vs Weekend)
                </h3>
                <p className="text-xs text-slate-500 mt-0.5">
                  Weekend crash counts highlighted in warm amber
                </p>
              </div>
              <TrendingUp className="w-4 h-4 text-amber-600" />
            </div>
            <EChartComponent option={getDayOfWeekOption()} style={{ height: "300px", width: "100%" }} />
          </div>
        </div>

        {/* Diurnal 24-Hour Distribution */}
        <div className="bg-white border border-slate-200 rounded-xl p-5 mb-6 shadow-xs">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-slate-900 tracking-wide">
                Diurnal Hourly Incident Profile (00:00 – 23:00)
              </h3>
              <p className="text-xs text-slate-500 mt-0.5">
                Identifies morning commute and late-night accident spikes
              </p>
            </div>
            <Clock className="w-4 h-4 text-brand-teal" />
          </div>
          <EChartComponent option={getHourlyOption()} style={{ height: "280px", width: "100%" }} />
        </div>

        {/* 2D Heatmap: Day vs Hour */}
        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-slate-900 tracking-wide">
                Day-of-Week × Hour-of-Day Collision Density Heatmap
              </h3>
              <p className="text-xs text-slate-500 mt-0.5">
                Visualizes high-density temporal clusters across all 168 hours of the week
              </p>
            </div>
          </div>
          <EChartComponent option={getHeatmapOption()} style={{ height: "320px", width: "100%" }} />
        </div>
      </div>
    </div>
  );
}
