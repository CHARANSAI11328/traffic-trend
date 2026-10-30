"use client";

import { useEffect, useState } from "react";
import { TopNav } from "@/components/layout/TopNav";
import { TrafficLoadingAnimation } from "@/components/shared/TrafficLoadingAnimation";
import { api } from "@/services/api";
import { DatasetItem, QualityProfile } from "@/types";
import {
  UploadCloud,
  FileCheck,
  Sparkles,
  Database,
  Trash2,
  CheckCircle2,
  AlertCircle,
  Sliders,
  Play,
  RotateCcw,
} from "lucide-react";

export default function DataManagementPage() {
  const [datasets, setDatasets] = useState<DatasetItem[]>([]);
  const [selectedDatasetId, setSelectedDatasetId] = useState<number | null>(null);
  const [profile, setProfile] = useState<QualityProfile | null>(null);
  const [cleanSummary, setCleanSummary] = useState<any | null>(null);
  const [previewRows, setPreviewRows] = useState<any[]>([]);

  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [profiling, setProfiling] = useState(false);
  const [cleaning, setCleaning] = useState(false);
  const [applying, setApplying] = useState(false);
  const [initialLoading, setInitialLoading] = useState(true);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Cleaning Options State
  const [cleaningOptions, setCleaningOptions] = useState({
    drop_duplicates: true,
    handle_missing_dates: "drop",
    handle_missing_severity: "impute_unknown",
    handle_missing_casualties: "impute_zero",
    impute_missing_categoricals: true,
    categorical_fill_value: "Unknown",
    validate_coordinates: true,
    enforce_non_negative_casualties: true,
  });

  const loadDatasets = async () => {
    try {
      const list = await api.getDatasets();
      setDatasets(list);
      const active = list.find((d) => d.is_active);
      if (active && !selectedDatasetId) {
        setSelectedDatasetId(active.id);
      }
    } catch (err: any) {
      setErrorMessage("Failed to load dataset repository");
    } finally {
      setInitialLoading(false);
    }
  };

  useEffect(() => {
    loadDatasets();
  }, []);

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!uploadFile) return;

    try {
      setUploading(true);
      setErrorMessage(null);
      setStatusMessage("Uploading and validating dataset schema...");
      const res = await api.uploadDataset(uploadFile);
      setStatusMessage(`Dataset uploaded successfully: ${res.row_count} records identified.`);
      setUploadFile(null);
      await loadDatasets();
      setSelectedDatasetId(res.dataset_id);
      // Auto-profile newly uploaded dataset
      handleProfile(res.dataset_id);
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to upload dataset");
    } finally {
      setUploading(false);
    }
  };

  const handleProfile = async (id: number) => {
    try {
      setProfiling(true);
      setErrorMessage(null);
      setStatusMessage("Computing 4-dimensional mathematical quality scorecard...");
      const res = await api.profileDataset(id);
      setProfile(res);
      setStatusMessage(`Profiling complete: Data Quality Score ${res.overall_score}/100 (${res.quality_grade})`);
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to profile dataset");
    } finally {
      setProfiling(false);
    }
  };

  const handlePreviewClean = async () => {
    if (!selectedDatasetId) return;
    try {
      setCleaning(true);
      setErrorMessage(null);
      const res = await api.cleanDataset(selectedDatasetId, cleaningOptions, false);
      setCleanSummary(res.summary);
      setPreviewRows(res.sample_preview || []);
      setStatusMessage("Cleaning preview generated. Review modifications before applying to database.");
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to run cleaning preview");
    } finally {
      setCleaning(false);
    }
  };

  const handleApplyToDb = async () => {
    if (!selectedDatasetId) return;
    try {
      setApplying(true);
      setErrorMessage(null);
      const res = await api.cleanDataset(selectedDatasetId, cleaningOptions, true);
      setCleanSummary(res.summary);
      setStatusMessage(`Cleaned dataset successfully committed to Neon PostgreSQL database and activated!`);
      await loadDatasets();
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to commit cleaned data");
    } finally {
      setApplying(false);
    }
  };

  const handleActivate = async (id: number) => {
    try {
      setStatusMessage("Switching active dataset...");
      await api.activateDataset(id);
      await loadDatasets();
      setSelectedDatasetId(id);
      setStatusMessage("Active dataset updated successfully.");
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to activate dataset");
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Are you sure you want to delete this dataset?")) return;
    try {
      await api.deleteDataset(id);
      await loadDatasets();
      if (selectedDatasetId === id) {
        setSelectedDatasetId(null);
        setProfile(null);
        setCleanSummary(null);
      }
      setStatusMessage("Dataset removed from system.");
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to delete dataset");
    }
  };

  return (
    <div className="flex-1 flex flex-col min-h-screen bg-[#f4f6f8]">
      <TopNav onRefresh={loadDatasets} />

      <div className="p-6 max-w-[1600px] mx-auto w-full">
        {/* Banner */}
        <div className="bg-white border border-slate-200/80 rounded-xl p-5 mb-6 flex flex-col md:flex-row items-start md:items-center justify-between gap-4 shadow-sm">
          <div>
            <div className="flex items-center gap-2">
              <Database className="w-5 h-5 text-brand-teal" />
              <h2 className="text-base font-bold text-slate-900 tracking-wide">
                Data Management Center & Quality Assurance
              </h2>
            </div>
            <p className="text-xs text-slate-500 mt-1">
              Upload raw CSV or Excel datasets, inspect schemas, generate mathematical quality scorecards, preview cleaning pipelines, and commit to the database.
            </p>
          </div>
          <div className="text-xs font-mono text-emerald-700 px-3 py-1.5 rounded-lg bg-emerald-50 border border-emerald-200 font-semibold">
            Transparent Audit Trail Enforced
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

        {/* Loading Animation for Async Processing */}
        {(profiling || cleaning || applying || uploading) && (
          <div className="mb-6">
            <TrafficLoadingAnimation
              message={
                profiling
                  ? "Profiling dataset quality score (Completeness, Uniqueness, Validity, Consistency)..."
                  : cleaning
                  ? "Executing mathematical deduplication & coordinate sanity checks..."
                  : applying
                  ? "Committing cleaned incident records to Neon PostgreSQL repository..."
                  : "Ingesting and parsing uploaded crash telemetry file..."
              }
            />
          </div>
        )}

        {/* Step 1: Upload Form & Repository */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
          <div className="lg:col-span-1 bg-white border border-slate-200/80 rounded-xl p-5 shadow-sm">
            <div className="flex items-center gap-2 mb-3">
              <UploadCloud className="w-4 h-4 text-brand-teal" />
              <h3 className="text-sm font-bold text-slate-900">Upload New Dataset</h3>
            </div>
            <p className="text-xs text-slate-500 mb-4">
              Accepts CSV (.csv) or Excel (.xlsx, .xls) files. Automatically identifies accident date, severity, and location columns.
            </p>

            <form onSubmit={handleUpload} className="space-y-4">
              <div className="border-2 border-dashed border-slate-300 hover:border-brand-teal/80 rounded-xl p-6 text-center cursor-pointer transition bg-slate-50/70">
                <input
                  type="file"
                  accept=".csv,.xlsx,.xls,.parquet"
                  onChange={(e) => setUploadFile(e.target.files?.[0] || null)}
                  className="hidden"
                  id="dataset-upload-input"
                />
                <label htmlFor="dataset-upload-input" className="cursor-pointer">
                  <UploadCloud className="w-8 h-8 text-slate-400 mx-auto mb-2" />
                  <span className="text-xs text-slate-700 font-medium block">
                    {uploadFile ? uploadFile.name : "Click to browse or drop file here"}
                  </span>
                  <span className="text-[10px] text-slate-400 block mt-1">
                    Up to 100MB per file (CSV, XLSX, XLS)
                  </span>
                </label>
              </div>

              <button
                type="submit"
                disabled={!uploadFile || uploading}
                className="w-full py-2 px-4 rounded-lg bg-brand-teal hover:bg-[#084248] disabled:opacity-40 text-xs font-semibold text-white transition flex items-center justify-center gap-2 shadow-sm"
              >
                {uploading ? "Ingesting..." : "Upload & Inspect"}
              </button>
            </form>
          </div>

          {/* Dataset Repository List */}
          <div className="lg:col-span-2 bg-white border border-slate-200/80 rounded-xl p-5 shadow-sm">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-bold text-slate-900">Dataset Repository & Activation</h3>
              <span className="text-xs text-slate-500 font-mono">{datasets.length} available</span>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-xs text-left">
                <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 uppercase font-mono text-[10px]">
                  <tr>
                    <th className="py-2.5 px-3">Dataset Name</th>
                    <th className="py-2.5 px-3 text-right">Rows</th>
                    <th className="py-2.5 px-3">Origin / Format</th>
                    <th className="py-2.5 px-3 text-center">Status</th>
                    <th className="py-2.5 px-3 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {datasets.map((d) => (
                    <tr
                      key={d.id}
                      className={`hover:bg-slate-50 transition cursor-pointer ${
                        selectedDatasetId === d.id ? "bg-teal-50/50" : ""
                      }`}
                      onClick={() => setSelectedDatasetId(d.id)}
                    >
                      <td className="py-2.5 px-3">
                        <div className="font-semibold text-slate-900">{d.name}</div>
                        <div className="text-[10px] text-slate-500 truncate max-w-[220px]">{d.filename}</div>
                      </td>
                      <td className="py-2.5 px-3 text-right font-mono font-medium text-slate-800">{d.row_count?.toLocaleString()}</td>
                      <td className="py-2.5 px-3 text-slate-500 text-[11px] truncate max-w-[150px]">{d.origin}</td>
                      <td className="py-2.5 px-3 text-center">
                        {d.is_active ? (
                          <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
                            Active
                          </span>
                        ) : (
                          <span className="px-2 py-0.5 rounded text-[10px] font-mono text-slate-500 bg-slate-100">
                            Ready
                          </span>
                        )}
                      </td>
                      <td className="py-2.5 px-3 text-right">
                        <div className="flex items-center justify-end gap-1.5" onClick={(e) => e.stopPropagation()}>
                          {!d.is_active && (
                            <button
                              onClick={() => handleActivate(d.id)}
                              className="px-2.5 py-1 rounded bg-teal-50 hover:bg-teal-100 text-[11px] text-brand-teal font-medium border border-teal-200"
                            >
                              Activate
                            </button>
                          )}
                          <button
                            onClick={() => handleProfile(d.id)}
                            className="px-2.5 py-1 rounded bg-slate-100 hover:bg-slate-200 text-[11px] text-slate-700 border border-slate-200"
                          >
                            Profile
                          </button>
                          <button
                            onClick={() => handleDelete(d.id)}
                            className="p-1 rounded hover:bg-red-50 text-slate-400 hover:text-red-600 transition"
                            title="Delete Dataset"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                  {datasets.length === 0 && !initialLoading && (
                    <tr>
                      <td colSpan={5} className="py-8 text-center text-slate-400">
                        No datasets uploaded yet. Upload a CSV or Excel file to get started.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Step 2: Quality Scorecard */}
        {profile && (
          <div className="bg-white border border-slate-200/80 rounded-xl p-5 mb-6 shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <div>
                <div className="flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-brand-teal" />
                  <h3 className="text-sm font-bold text-slate-900">Mathematical Data Quality Scorecard</h3>
                </div>
                <p className="text-xs text-slate-500 mt-0.5">
                  Institutional multi-dimensional evaluation of Completeness, Uniqueness, Validity, and Consistency
                </p>
              </div>
              <div className="text-right">
                <span className="text-2xl font-bold font-mono text-brand-teal">{profile.overall_score} / 100</span>
                <span className="text-xs font-semibold block text-slate-600">{profile.quality_grade}</span>
              </div>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
              <div className="p-3.5 bg-slate-50 rounded-xl border border-slate-200">
                <span className="text-[10px] uppercase font-mono text-slate-500 block">Completeness (30%)</span>
                <span className="text-xl font-bold font-mono text-slate-900 mt-1 block">{profile.completeness_score}%</span>
                <span className="text-[11px] text-slate-500">{profile.total_missing_cells} missing cells ({profile.missing_cells_pct}%)</span>
              </div>

              <div className="p-3.5 bg-slate-50 rounded-xl border border-slate-200">
                <span className="text-[10px] uppercase font-mono text-slate-500 block">Uniqueness (25%)</span>
                <span className="text-xl font-bold font-mono text-slate-900 mt-1 block">{profile.uniqueness_score}%</span>
                <span className="text-[11px] text-slate-500">{profile.duplicate_count} duplicate rows ({profile.duplicate_pct}%)</span>
              </div>

              <div className="p-3.5 bg-slate-50 rounded-xl border border-slate-200">
                <span className="text-[10px] uppercase font-mono text-slate-500 block">Validity (25%)</span>
                <span className="text-xl font-bold font-mono text-slate-900 mt-1 block">{profile.validity_score}%</span>
                <span className="text-[11px] text-slate-500">{profile.invalid_dates_count} unparseable dates</span>
              </div>

              <div className="p-3.5 bg-slate-50 rounded-xl border border-slate-200">
                <span className="text-[10px] uppercase font-mono text-slate-500 block">Consistency (20%)</span>
                <span className="text-xl font-bold font-mono text-slate-900 mt-1 block">{profile.consistency_score}%</span>
                <span className="text-[11px] text-slate-500">Casualty & severity coherence</span>
              </div>
            </div>

            {/* Column Profiles Summary */}
            {profile.column_profiles && (
              <div className="mt-4 pt-4 border-t border-slate-100">
                <h4 className="text-xs font-bold text-slate-900 mb-2">Column Profiling Breakdown</h4>
                <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-2">
                  {Object.entries(profile.column_profiles).slice(0, 12).map(([col, meta]: any) => (
                    <div key={col} className="p-2 bg-slate-50 rounded border border-slate-200 text-[11px]">
                      <span className="font-mono text-brand-teal truncate block font-semibold">{col}</span>
                      <span className="text-[10px] text-slate-500 block">{meta.dtype} | {meta.unique_values} unique</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Step 3: Interactive Cleaning Configuration & Execution */}
        {selectedDatasetId && (
          <div className="bg-white border border-slate-200/80 rounded-xl p-5 mb-6 shadow-sm">
            <div className="flex items-center gap-2 mb-3">
              <Sliders className="w-4 h-4 text-brand-teal" />
              <h3 className="text-sm font-bold text-slate-900">Interactive Data Cleaning Pipeline Configuration</h3>
            </div>
            <p className="text-xs text-slate-500 mb-4">
              Select remediation strategies before modifying records. Changes can be previewed before writing to the database.
            </p>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-5">
              <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
                <label className="flex items-center gap-2 text-xs font-medium text-slate-800 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={cleaningOptions.drop_duplicates}
                    onChange={(e) => setCleaningOptions({ ...cleaningOptions, drop_duplicates: e.target.checked })}
                    className="rounded border-slate-300 text-brand-teal focus:ring-teal-500"
                  />
                  <span>Deduplicate Exact Matches</span>
                </label>
                <span className="text-[10px] text-slate-500 block mt-1 pl-5">
                  Removes identical duplicate crash rows
                </span>
              </div>

              <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
                <label className="flex items-center gap-2 text-xs font-medium text-slate-800 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={cleaningOptions.validate_coordinates}
                    onChange={(e) => setCleaningOptions({ ...cleaningOptions, validate_coordinates: e.target.checked })}
                    className="rounded border-slate-300 text-brand-teal focus:ring-teal-500"
                  />
                  <span>Sanitize Coordinates</span>
                </label>
                <span className="text-[10px] text-slate-500 block mt-1 pl-5">
                  Nullifies coordinates outside [-90, 90] / [-180, 180]
                </span>
              </div>

              <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
                <label className="flex items-center gap-2 text-xs font-medium text-slate-800 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={cleaningOptions.enforce_non_negative_casualties}
                    onChange={(e) => setCleaningOptions({ ...cleaningOptions, enforce_non_negative_casualties: e.target.checked })}
                    className="rounded border-slate-300 text-brand-teal focus:ring-teal-500"
                  />
                  <span>Enforce Non-Negative Casualties</span>
                </label>
                <span className="text-[10px] text-slate-500 block mt-1 pl-5">
                  Clips negative fatality and injury counts to 0
                </span>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex items-center gap-3">
              <button
                onClick={handlePreviewClean}
                disabled={cleaning}
                className="px-4 py-2 bg-slate-100 hover:bg-slate-200 border border-slate-300 text-slate-800 text-xs font-semibold rounded-lg flex items-center gap-2 transition"
              >
                <Play className="w-3.5 h-3.5 text-brand-teal" />
                <span>{cleaning ? "Simulating..." : "Preview Cleaning Pipeline"}</span>
              </button>

              <button
                onClick={handleApplyToDb}
                disabled={applying}
                className="px-4 py-2 bg-brand-teal hover:bg-[#084248] disabled:opacity-40 text-white text-xs font-semibold rounded-lg flex items-center gap-2 transition shadow-sm"
              >
                <Database className="w-3.5 h-3.5" />
                <span>{applying ? "Ingesting to Database..." : "Commit Cleaned Dataset & Activate"}</span>
              </button>
            </div>

            {/* Cleaning Audit Summary */}
            {cleanSummary && (
              <div className="mt-5 pt-4 border-t border-slate-200">
                <h4 className="text-xs font-bold text-slate-900 mb-2">Cleaning Transformation Audit Log</h4>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs font-mono mb-3">
                  <div className="p-2.5 bg-slate-50 rounded border border-slate-200">
                    <span className="text-slate-500 block text-[10px]">Original Records</span>
                    <strong className="text-slate-900">{cleanSummary.original_records?.toLocaleString()}</strong>
                  </div>
                  <div className="p-2.5 bg-amber-50 rounded border border-amber-200">
                    <span className="text-amber-700 block text-[10px]">Duplicates Purged</span>
                    <strong className="text-amber-800">{cleanSummary.duplicates_removed}</strong>
                  </div>
                  <div className="p-2.5 bg-teal-50 rounded border border-teal-200">
                    <span className="text-teal-700 block text-[10px]">Missing Imputed</span>
                    <strong className="text-teal-800">{cleanSummary.missing_imputed_count}</strong>
                  </div>
                  <div className="p-2.5 bg-emerald-50 rounded border border-emerald-200">
                    <span className="text-emerald-700 block text-[10px]">Final Retained</span>
                    <strong className="text-emerald-800">{cleanSummary.retained_records?.toLocaleString()}</strong>
                  </div>
                </div>

                <div className="space-y-1.5 max-h-36 overflow-y-auto bg-slate-50 p-3 rounded-lg border border-slate-200 text-[11px] font-mono text-slate-700">
                  {cleanSummary.modifications_log?.map((log: string, i: number) => (
                    <div key={i} className="flex items-center gap-2">
                      <span className="text-brand-teal font-bold">✓</span>
                      <span>{log}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
