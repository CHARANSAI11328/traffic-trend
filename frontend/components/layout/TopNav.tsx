"use client";

import { usePathname } from "next/navigation";
import { Database, ShieldCheck, RefreshCw } from "lucide-react";

interface TopNavProps {
  onRefresh?: () => void;
  datasetName?: string;
  coveragePeriod?: string;
}

export function TopNav({ onRefresh, datasetName, coveragePeriod }: TopNavProps) {
  const pathname = usePathname();

  const getPageTitle = (path: string) => {
    switch (path) {
      case "/":
      case "/overview":
        return "Executive Overview & KPIs";
      case "/accidents":
        return "Accident Analysis & Exploration";
      case "/geography":
        return "Geographical Intelligence & Hotspots";
      case "/trends":
        return "Temporal Patterns & Time-Series";
      case "/severity":
        return "Severity & Casualty Intelligence";
      case "/intelligence":
        return "Risk Intelligence & Predictive Anomalies";
      case "/data-management":
        return "Data Management & Quality Profiler";
      case "/reports":
        return "Executive Reporting Center";
      case "/system":
        return "System Health & Ingestion Telemetry";
      case "/login":
        return "Operator Authentication";
      default:
        return "Road Safety Platform";
    }
  };

  return (
    <header className="h-16 border-b border-slate-200 bg-white/90 backdrop-blur sticky top-0 z-20 flex items-center justify-between px-6 shadow-xs">
      {/* Breadcrumb / Title */}
      <div>
        <div className="flex items-center gap-2 text-xs text-slate-500 font-medium">
          <span>Traffic Trend</span>
          <span>/</span>
          <span className="text-brand-teal font-semibold">Dashboard</span>
        </div>
        <h1 className="text-lg font-bold text-slate-900 tracking-tight leading-tight">
          {getPageTitle(pathname)}
        </h1>
      </div>

      {/* Status Bar */}
      <div className="flex items-center gap-3">
        {coveragePeriod && (
          <div className="hidden lg:flex items-center gap-2 px-3 py-1.5 rounded-md bg-white border border-slate-200 text-xs text-slate-600 shadow-xs">
            <span className="text-slate-400 font-medium">Coverage:</span>
            <span className="text-slate-800 font-mono font-semibold">{coveragePeriod}</span>
          </div>
        )}

        <div className="flex items-center gap-2 px-3 py-1.5 rounded-md bg-white border border-slate-200 text-xs shadow-xs">
          <Database className="w-3.5 h-3.5 text-brand-teal" />
          <span className="text-slate-700 font-medium truncate max-w-[200px]">
            {datasetName || "Benchmark Demonstration Dataset"}
          </span>
          <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
            PostgreSQL Live
          </span>
        </div>

        {onRefresh && (
          <button
            onClick={onRefresh}
            className="p-2 rounded-md bg-white border border-slate-200 hover:border-slate-300 hover:bg-slate-50 text-slate-600 hover:text-slate-900 transition shadow-xs"
            title="Refresh Data"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        )}
      </div>
    </header>
  );
}
