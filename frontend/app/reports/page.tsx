"use client";

import { useEffect, useState } from "react";
import { TopNav } from "@/components/layout/TopNav";
import { TrafficLoadingAnimation } from "@/components/shared/TrafficLoadingAnimation";
import { api } from "@/services/api";
import { FilterOptions } from "@/types";
import {
  FileText,
  FileSpreadsheet,
  Download,
  CheckCircle2,
  AlertCircle,
  Sparkles,
} from "lucide-react";

export default function ReportsPage() {
  const [reports, setReports] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const [filterOptions, setFilterOptions] = useState<FilterOptions>({
    states: [],
    severities: [],
    years: [],
    weather: [],
    road_types: [],
  });

  const [formData, setFormData] = useState({
    title: "Executive Road Safety Intelligence Brief",
    report_type: "executive",
    format: "pdf",
    state: "All",
    severity: "All",
    year: 0,
  });

  const loadData = async () => {
    try {
      setLoading(true);
      const [reps, ov] = await Promise.all([api.getReports(), api.getOverview()]);
      setReports(reps);
      if (ov.filter_options) setFilterOptions(ov.filter_options);
    } catch (err: any) {
      setErrorMessage("Failed to load reporting data");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setGenerating(true);
      setErrorMessage(null);
      setStatusMessage(`Generating institutional ${formData.format.toUpperCase()} report from PostgreSQL database...`);
      const newReport = await api.generateReport(formData);
      setStatusMessage(`Report '${newReport.title}' generated successfully! Ready for download.`);
      await loadData();
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to generate report");
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="flex-1 flex flex-col min-h-screen bg-[#f4f6f8]">
      <TopNav onRefresh={loadData} />

      <div className="p-6 max-w-[1600px] mx-auto w-full">
        {/* Banner */}
        <div className="bg-white border border-slate-200/80 rounded-xl p-5 mb-6 flex flex-col md:flex-row items-start md:items-center justify-between gap-4 shadow-sm">
          <div>
            <div className="flex items-center gap-2">
              <FileSpreadsheet className="w-5 h-5 text-brand-teal" />
              <h2 className="text-base font-bold text-slate-900 tracking-wide">
                Executive Reporting & Export Center
              </h2>
            </div>
            <p className="text-xs text-slate-500 mt-1">
              Generate publication-grade PDF briefs with embedded KPI tables and multi-tab formatted Excel workbooks from live database queries.
            </p>
          </div>
          <div className="text-xs font-mono text-brand-teal px-3 py-1.5 rounded-lg bg-teal-50 border border-teal-200">
            Engine: ReportLab + OpenPyXL
          </div>
        </div>

        {/* Notifications */}
        {statusMessage && (
          <div className="mb-6 bg-teal-50 border border-teal-200 text-teal-800 p-3.5 rounded-xl text-xs flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 shrink-0 text-teal-600" />
            <span>{statusMessage}</span>
          </div>
        )}
        {errorMessage && (
          <div className="mb-6 bg-red-50 border border-red-200 text-red-700 p-3.5 rounded-xl text-xs flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0 text-red-500" />
            <span>{errorMessage}</span>
          </div>
        )}

        {/* Generating Animation */}
        {generating && (
          <div className="mb-6">
            <TrafficLoadingAnimation message={`Compiling ${formData.format.toUpperCase()} executive document from accident database records...`} />
          </div>
        )}

        {/* Report Generation Form */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
          <div className="lg:col-span-1 bg-white border border-slate-200/80 rounded-xl p-5 shadow-sm">
            <h3 className="text-sm font-bold text-slate-900 mb-2">Generate Custom Report</h3>
            <p className="text-xs text-slate-500 mb-4">
              Configure parameters to export filtered records, KPI summaries, and regional rankings.
            </p>

            <form onSubmit={handleGenerate} className="space-y-4 text-xs">
              <div>
                <label className="text-slate-700 font-medium block mb-1">Report Document Title</label>
                <input
                  type="text"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-300 rounded-lg text-slate-900 focus:outline-none focus:border-brand-teal"
                  required
                />
              </div>

              <div>
                <label className="text-slate-700 font-medium block mb-1">Export Format</label>
                <div className="grid grid-cols-3 gap-2">
                  {["pdf", "excel", "csv"].map((fmt) => (
                    <button
                      type="button"
                      key={fmt}
                      onClick={() => setFormData({ ...formData, format: fmt })}
                      className={`py-2 px-3 rounded-lg border text-center font-mono uppercase text-xs font-semibold transition ${
                        formData.format === fmt
                          ? "bg-teal-50 border-brand-teal text-brand-teal shadow-sm"
                          : "bg-white border-slate-200 text-slate-600 hover:text-slate-900 hover:border-slate-300"
                      }`}
                    >
                      {fmt}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="text-slate-700 font-medium block mb-1">State / Jurisdiction Filter</label>
                <select
                  value={formData.state}
                  onChange={(e) => setFormData({ ...formData, state: e.target.value })}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-300 rounded-lg text-slate-800 focus:outline-none focus:border-brand-teal"
                >
                  <option value="All">All States / Regions</option>
                  {filterOptions.states.map((s) => (
                    <option key={s} value={s}>{s}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="text-slate-700 font-medium block mb-1">Severity Filter</label>
                <select
                  value={formData.severity}
                  onChange={(e) => setFormData({ ...formData, severity: e.target.value })}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-300 rounded-lg text-slate-800 focus:outline-none focus:border-brand-teal"
                >
                  <option value="All">All Severities</option>
                  {filterOptions.severities.map((s) => (
                    <option key={s} value={s}>{s}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="text-slate-700 font-medium block mb-1">Year Scope</label>
                <select
                  value={formData.year}
                  onChange={(e) => setFormData({ ...formData, year: parseInt(e.target.value) || 0 })}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-300 rounded-lg text-slate-800 focus:outline-none focus:border-brand-teal"
                >
                  <option value={0}>All Recorded Years</option>
                  {filterOptions.years.map((y) => (
                    <option key={y} value={y}>{y}</option>
                  ))}
                </select>
              </div>

              <button
                type="submit"
                disabled={generating}
                className="w-full py-2.5 px-4 bg-brand-teal hover:bg-[#084248] disabled:opacity-40 text-white font-semibold rounded-lg transition flex items-center justify-center gap-2 mt-2 shadow-sm"
              >
                <Sparkles className="w-4 h-4" />
                <span>{generating ? "Compiling Document..." : "Generate Report Now"}</span>
              </button>
            </form>
          </div>

          {/* Generated Reports History */}
          <div className="lg:col-span-2 bg-white border border-slate-200/80 rounded-xl p-5 shadow-sm">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-bold text-slate-900">Generated Report History & Downloads</h3>
              <span className="text-xs text-slate-500 font-mono">{reports.length} compiled</span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-xs text-left">
                <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 uppercase font-mono text-[10px]">
                  <tr>
                    <th className="py-2.5 px-3">Document Title</th>
                    <th className="py-2.5 px-3 text-center">Format</th>
                    <th className="py-2.5 px-3">Generated Timestamp</th>
                    <th className="py-2.5 px-3 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {reports.map((r) => (
                    <tr key={r.id} className="hover:bg-slate-50 transition">
                      <td className="py-3 px-3 font-semibold text-slate-900">
                        <div className="flex items-center gap-2">
                          {r.format === "pdf" ? (
                            <FileText className="w-4 h-4 text-red-500 shrink-0" />
                          ) : (
                            <FileSpreadsheet className="w-4 h-4 text-emerald-600 shrink-0" />
                          )}
                          <span>{r.title}</span>
                        </div>
                      </td>
                      <td className="py-3 px-3 text-center font-mono uppercase font-bold text-[10px]">
                        <span className={`px-2 py-0.5 rounded border ${
                          r.format === "pdf" ? "bg-red-50 text-red-700 border-red-200" : "bg-emerald-50 text-emerald-700 border-emerald-200"
                        }`}>
                          {r.format}
                        </span>
                      </td>
                      <td className="py-3 px-3 text-slate-500 font-mono text-[11px]">
                        {new Date(r.generated_at).toLocaleString()}
                      </td>
                      <td className="py-3 px-3 text-right">
                        <a
                          href={api.getReportDownloadUrl(r.id)}
                          download
                          className="inline-flex items-center gap-1.5 px-3 py-1 rounded bg-teal-50 hover:bg-teal-100 text-brand-teal border border-teal-200 text-xs font-semibold transition"
                        >
                          <Download className="w-3 h-3" />
                          <span>Download</span>
                        </a>
                      </td>
                    </tr>
                  ))}
                  {reports.length === 0 && !loading && (
                    <tr>
                      <td colSpan={4} className="py-10 text-center text-slate-400">
                        No reports generated yet. Configure options on the left to compile your first report.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
