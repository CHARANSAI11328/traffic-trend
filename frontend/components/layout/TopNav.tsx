"use client";

import { usePathname } from "next/navigation";
import { Database, RefreshCw, Menu } from "lucide-react";
import { useMobileNav } from "@/components/layout/MobileNavContext";

interface TopNavProps {
  onRefresh?: () => void;
  datasetName?: string;
  coveragePeriod?: string;
}

export function TopNav({ onRefresh, datasetName, coveragePeriod }: TopNavProps) {
  const pathname = usePathname();
  const { toggle } = useMobileNav();

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
    <header className="h-16 border-b border-slate-200 bg-white/90 backdrop-blur sticky top-0 z-20 flex items-center justify-between px-3 sm:px-6 shadow-xs shrink-0">
      {/* Mobile Menu Button + Breadcrumb / Title */}
      <div className="flex items-center min-w-0 gap-2">
        <button
          onClick={toggle}
          className="lg:hidden p-2 -ml-1 rounded-lg text-slate-600 hover:text-slate-900 hover:bg-slate-100 transition shrink-0"
          aria-label="Toggle navigation menu"
        >
          <Menu className="w-5 h-5 text-slate-700" />
        </button>

        <div className="min-w-0">
          <div className="hidden sm:flex items-center gap-1.5 text-xs text-slate-500 font-medium">
            <span>Traffic Trend</span>
            <span>/</span>
            <span className="text-brand-teal font-semibold">Dashboard</span>
          </div>
          <h1 className="text-sm sm:text-base md:text-lg font-bold text-slate-900 tracking-tight leading-tight truncate">
            {getPageTitle(pathname)}
          </h1>
        </div>
      </div>

      {/* Status Bar */}
      <div className="flex items-center gap-2 sm:gap-3 shrink-0">
        {coveragePeriod && (
          <div className="hidden xl:flex items-center gap-2 px-3 py-1.5 rounded-md bg-white border border-slate-200 text-xs text-slate-600 shadow-xs">
            <span className="text-slate-400 font-medium">Coverage:</span>
            <span className="text-slate-800 font-mono font-semibold">{coveragePeriod}</span>
          </div>
        )}

        {/* Desktop Dataset Status Pill */}
        <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-md bg-white border border-slate-200 text-xs shadow-xs">
          <Database className="w-3.5 h-3.5 text-brand-teal shrink-0" />
          <span className="text-slate-700 font-medium truncate max-w-[130px] md:max-w-[200px]">
            {datasetName || "Benchmark Demonstration Dataset"}
          </span>
          <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200 shrink-0">
            PostgreSQL Live
          </span>
        </div>

        {/* Mobile Compact Live Badge */}
        <div className="sm:hidden flex items-center gap-1.5 px-2 py-1 rounded-md bg-emerald-50 border border-emerald-200 text-[10px] font-semibold text-emerald-700">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
          <span>Live</span>
        </div>

        {onRefresh && (
          <button
            onClick={onRefresh}
            className="p-2 rounded-md bg-white border border-slate-200 hover:border-slate-300 hover:bg-slate-50 text-slate-600 hover:text-slate-900 transition shadow-xs shrink-0"
            title="Refresh Data"
            aria-label="Refresh Data"
          >
            <RefreshCw className="w-3.5 h-3.5" />
          </button>
        )}
      </div>
    </header>
  );
}
