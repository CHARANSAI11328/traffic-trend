"use client";

import { useEffect, useState } from "react";
import { TopNav } from "@/components/layout/TopNav";
import { EChartComponent } from "@/components/charts/EChartComponent";
import { TrafficLoadingAnimation } from "@/components/shared/TrafficLoadingAnimation";
import { api } from "@/services/api";
import { Brain, AlertTriangle, TrendingUp, Info } from "lucide-react";

export default function IntelligencePage() {
  const [anomalies, setAnomalies] = useState<any>(null);
  const [forecast, setForecast] = useState<any>(null);
  const [correlations, setCorrelations] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchIntelligence = async () => {
    try {
      setLoading(true);
      setError(null);
      const [anomRes, foreRes, corrRes] = await Promise.all([
        api.getAnomalies(),
        api.getForecast(6),
        api.getCorrelations(),
      ]);
      setAnomalies(anomRes);
      setForecast(foreRes);
      setCorrelations(corrRes);
    } catch (err: any) {
      setError(err.message || "Failed to load risk intelligence");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchIntelligence();
  }, []);

  // Time-Series Forecast Option - Bespoke Light Styling
  const getForecastOption = () => {
    if (!forecast?.historical || forecast.historical.length === 0) return {};

    const periods: string[] = [];
    const actuals: (number | null)[] = [];
    const predicted: (number | null)[] = [];
    const lowerBands: (number | null)[] = [];
    const upperBands: (number | null)[] = [];

    // Historical
    forecast.historical.forEach((h: any) => {
      periods.push(h.period);
      actuals.push(h.actual);
      predicted.push(null);
      lowerBands.push(null);
      upperBands.push(null);
    });

    // Bridge point
    if (forecast.forecast && forecast.forecast.length > 0) {
      const lastHist = forecast.historical[forecast.historical.length - 1];
      predicted[predicted.length - 1] = lastHist.actual;
      lowerBands[lowerBands.length - 1] = lastHist.actual;
      upperBands[upperBands.length - 1] = lastHist.actual;

      forecast.forecast.forEach((f: any) => {
        periods.push(f.period);
        actuals.push(null);
        predicted.push(f.predicted);
        lowerBands.push(f.lower_bound_95);
        upperBands.push(f.upper_bound_95);
      });
    }

    return {
      backgroundColor: "transparent",
      tooltip: {
        trigger: "axis",
        backgroundColor: "#ffffff",
        borderColor: "#cbd5e1",
        borderWidth: 1,
        textStyle: { color: "#0f172a", fontSize: 12 },
        extraCssText: "box-shadow: 0 4px 12px rgba(0,0,0,0.08); border-radius: 8px;",
      },
      legend: {
        data: ["Historical Volume", "Projected Trend", "95% Confidence Interval"],
        textStyle: { color: "#475569" },
        top: "2%",
      },
      grid: { left: "3%", right: "4%", bottom: "6%", top: "16%", containLabel: true },
      xAxis: {
        type: "category",
        data: periods,
        axisLine: { lineStyle: { color: "#cbd5e1" } },
        axisLabel: { color: "#64748b", rotate: 25 },
      },
      yAxis: {
        type: "value",
        splitLine: { lineStyle: { color: "#f1f5f9" } },
        axisLabel: { color: "#64748b" },
      },
      series: [
        {
          name: "Historical Volume",
          type: "line",
          data: actuals,
          itemStyle: { color: "#0a545c" },
          lineStyle: { width: 3, color: "#0a545c" },
        },
        {
          name: "Projected Trend",
          type: "line",
          data: predicted,
          itemStyle: { color: "#0891b2" },
          lineStyle: { width: 3, type: "dashed", color: "#0891b2" },
        },
        {
          name: "95% Confidence Interval",
          type: "line",
          data: upperBands,
          lineStyle: { opacity: 0 },
          stack: "confidence-band",
          symbol: "none",
        },
        {
          name: "95% Confidence Interval",
          type: "line",
          data: lowerBands,
          lineStyle: { opacity: 0 },
          areaStyle: { color: "rgba(8, 145, 178, 0.12)" },
          stack: "confidence-band",
          symbol: "none",
        },
      ],
    };
  };

  return (
    <div className="flex-1 flex flex-col min-h-screen bg-[#f4f6f8]">
      <TopNav onRefresh={fetchIntelligence} />

      <div className="p-3 sm:p-5 md:p-6 max-w-[1600px] mx-auto w-full">
        {/* Header Banner */}
        <div className="bg-white border border-slate-200/80 rounded-xl p-5 mb-6 flex flex-col md:flex-row items-start md:items-center justify-between gap-4 shadow-sm">
          <div>
            <div className="flex items-center gap-2">
              <Brain className="w-5 h-5 text-brand-teal" />
              <h2 className="text-base font-bold text-slate-900 tracking-wide">
                Risk Intelligence & Statistical Anomaly Engine
              </h2>
            </div>
            <p className="text-xs text-slate-500 mt-1">
              Data science modules detect statistical outliers, severity spikes, and projected trajectories without asserting unverified causal claims.
            </p>
          </div>
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-teal-50 border border-teal-200 text-xs text-brand-teal font-mono">
            <span>Model: OLS + Z-Score Outlier Filter</span>
          </div>
        </div>

        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 text-red-700 p-4 rounded-xl text-sm flex items-center justify-between">
            <span>{error}</span>
            <button onClick={fetchIntelligence} className="px-3 py-1 bg-red-100 hover:bg-red-200 rounded text-xs font-semibold">Retry</button>
          </div>
        )}

        {loading ? (
          <TrafficLoadingAnimation message="Synthesizing econometric forecasts, statistical anomalies & empirical confidence bounds..." />
        ) : (
          <>
            {/* Statistical Anomalies Grid */}
            <div className="mb-6">
              <div className="flex items-center gap-2 mb-3">
                <AlertTriangle className="w-4 h-4 text-amber-600" />
                <h3 className="text-sm font-bold text-slate-900 tracking-wide">
                  Statistical Outliers & Regional Spikes (|Z| &gt; 1.96 or Tukey Fence)
                </h3>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {anomalies?.regional_spikes?.map((a: any, i: number) => (
                  <div key={i} className="bg-white border border-amber-200 rounded-xl p-4 shadow-sm hover:shadow-md transition">
                    <div className="flex items-start justify-between">
                      <span className="text-xs font-bold text-slate-900">{a.entity}</span>
                      <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-amber-50 text-amber-700 border border-amber-300 font-semibold">
                        Z = +{a.z_score}
                      </span>
                    </div>
                    <div className="mt-2 text-2xl font-bold font-mono text-slate-900">
                      {a.observed_value?.toLocaleString()}{" "}
                      <span className="text-xs font-normal text-slate-500">crashes (vs mean {a.expected_mean})</span>
                    </div>
                    <p className="mt-2 text-[11px] text-slate-600 border-t border-slate-100 pt-2 leading-relaxed">
                      {a.analytical_note}
                    </p>
                  </div>
                ))}
                {(!anomalies?.regional_spikes || anomalies.regional_spikes.length === 0) && (
                  <div className="col-span-3 py-8 text-center text-slate-500 bg-white border border-slate-200 rounded-xl">
                    No statistically significant regional crash spikes detected at current alpha threshold.
                  </div>
                )}
              </div>
            </div>

            {/* High Severity Concentration Spikes */}
            {anomalies?.fatality_spikes && anomalies.fatality_spikes.length > 0 && (
              <div className="mb-6">
                <div className="flex items-center gap-2 mb-3">
                  <AlertTriangle className="w-4 h-4 text-red-600" />
                  <h3 className="text-sm font-bold text-slate-900 tracking-wide">
                    Severity Concentration Outliers (Elevated Fatality Ratios)
                  </h3>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                  {anomalies.fatality_spikes.slice(0, 4).map((f: any, i: number) => (
                    <div key={i} className="bg-white border border-red-200 rounded-xl p-4 shadow-sm">
                      <div className="flex items-start justify-between">
                        <span className="text-xs font-bold text-slate-900">{f.entity}</span>
                        <span className="px-1.5 py-0.5 rounded text-[10px] font-mono bg-red-50 text-red-700 border border-red-200 font-semibold">
                          Z = +{f.z_score}
                        </span>
                      </div>
                      <div className="mt-2 text-xl font-bold font-mono text-red-600">
                        {f.observed_value}% <span className="text-xs font-normal text-slate-500">fatality rate</span>
                      </div>
                      <div className="text-[11px] text-slate-500 mt-1">
                        {f.fatalities} deaths across {f.total_crashes} crashes
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Time-Series Forecast */}
            <div className="bg-white border border-slate-200/80 rounded-xl p-5 mb-6 shadow-sm">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <div className="flex items-center gap-2">
                    <TrendingUp className="w-4 h-4 text-brand-teal" />
                    <h3 className="text-sm font-bold text-slate-900 tracking-wide">
                      Time-Series Accident Trajectory & 6-Month Projection
                    </h3>
                  </div>
                  <p className="text-xs text-slate-500 mt-0.5">
                    Econometric trend projection using OLS regression with empirical 95% confidence intervals
                  </p>
                </div>
                {forecast?.trend_direction && (
                  <span className={`px-2.5 py-1 rounded-full text-xs font-mono font-semibold ${
                    forecast.trend_direction === "Increasing" ? "bg-red-50 text-red-700 border border-red-200" : "bg-emerald-50 text-emerald-700 border border-emerald-200"
                  }`}>
                    Trend: {forecast.trend_direction} (Slope: {forecast.slope})
                  </span>
                )}
              </div>
              <EChartComponent option={getForecastOption()} style={{ height: "340px", width: "100%" }} />
            </div>

            {/* Methodology Caveats */}
            <div className="bg-white border border-slate-200/80 rounded-xl p-5 shadow-sm">
              <div className="flex items-center gap-2 mb-2">
                <Info className="w-4 h-4 text-brand-teal" />
                <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
                  Analytical Methodology & Scientific Integrity Guidelines
                </h4>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs text-slate-600 leading-relaxed mt-3">
                <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
                  <strong className="text-slate-900 block mb-1">1. Descriptive vs Causal Claims</strong>
                  Historical correlations identify observed co-occurrence but do not prove causation. Road design, speed, and enforcement interact in non-linear ways.
                </div>
                <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
                  <strong className="text-slate-900 block mb-1">2. Exposure & Denominator Bias</strong>
                  A high aggregate accident count does not automatically indicate higher danger if traffic exposure, road mileage, or regional population are unavailable.
                </div>
                <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
                  <strong className="text-slate-900 block mb-1">3. Forecast Limitations</strong>
                  Trend projections assume statistical stationarity. Real-world policy interventions, road upgrades, and weather anomalies will alter true outcomes.
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
