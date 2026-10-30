"use client";

import { useState } from "react";
import { Filter, RotateCcw, ChevronDown, ChevronUp } from "lucide-react";
import { FilterOptions, FilterState } from "@/types";

interface FilterBarProps {
  options: FilterOptions;
  filters: FilterState;
  onChange: (filters: FilterState) => void;
  onReset: () => void;
}

export function GlobalFilterBar({ options, filters, onChange, onReset }: FilterBarProps) {
  const [mobileExpanded, setMobileExpanded] = useState(false);

  // Count active non-default filters
  const activeCount = [
    filters.state !== "All",
    filters.severity !== "All",
    filters.year !== 0,
    filters.weather && filters.weather !== "All",
    filters.road_type && filters.road_type !== "All",
  ].filter(Boolean).length;

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-3 sm:p-3.5 mb-6 shadow-xs">
      {/* Top Bar on Mobile: Title + Active Badge + Collapse Toggle + Reset */}
      <div className="flex items-center justify-between lg:hidden mb-2.5 pb-2 border-b border-slate-100">
        <button
          onClick={() => setMobileExpanded(!mobileExpanded)}
          className="flex items-center gap-2 text-xs font-bold text-brand-teal uppercase tracking-wider"
        >
          <Filter className="w-3.5 h-3.5" />
          <span>Filters</span>
          {activeCount > 0 && (
            <span className="px-1.5 py-0.5 rounded-full text-[10px] bg-brand-teal/10 text-brand-teal font-mono">
              {activeCount} active
            </span>
          )}
          {mobileExpanded ? (
            <ChevronUp className="w-3.5 h-3.5 text-slate-400" />
          ) : (
            <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
          )}
        </button>

        <button
          onClick={onReset}
          className="flex items-center gap-1 text-[11px] text-slate-500 hover:text-slate-800 bg-slate-50 hover:bg-slate-100 px-2.5 py-1 rounded-lg border border-slate-200 transition font-medium"
        >
          <RotateCcw className="w-3 h-3" />
          <span>Reset</span>
        </button>
      </div>

      {/* Filter Select Controls (Always visible on lg, collapsible on mobile) */}
      <div
        className={`${
          mobileExpanded ? "grid" : "hidden lg:flex"
        } grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:flex lg:flex-wrap items-center gap-2 sm:gap-3`}
      >
        {/* Desktop Filter Icon */}
        <div className="hidden lg:flex items-center gap-2 text-xs font-bold text-brand-teal uppercase tracking-wider pl-1 pr-3 border-r border-slate-200">
          <Filter className="w-3.5 h-3.5" />
          <span>Filters</span>
          {activeCount > 0 && (
            <span className="px-1.5 py-0.5 rounded-full text-[10px] bg-brand-teal/10 text-brand-teal font-mono">
              {activeCount}
            </span>
          )}
        </div>

        {/* State Filter */}
        <div className="w-full lg:w-auto">
          <select
            value={filters.state}
            onChange={(e) => onChange({ ...filters, state: e.target.value })}
            className="w-full lg:w-auto min-h-[38px] bg-slate-50 border border-slate-200 text-xs rounded-lg px-3 py-2 text-slate-800 font-medium focus:outline-none focus:border-brand-teal focus:bg-white transition shadow-2xs"
          >
            <option value="All">All States / Regions</option>
            {options.states.map((s) => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
        </div>

        {/* Severity Filter */}
        <div className="w-full lg:w-auto">
          <select
            value={filters.severity}
            onChange={(e) => onChange({ ...filters, severity: e.target.value })}
            className="w-full lg:w-auto min-h-[38px] bg-slate-50 border border-slate-200 text-xs rounded-lg px-3 py-2 text-slate-800 font-medium focus:outline-none focus:border-brand-teal focus:bg-white transition shadow-2xs"
          >
            <option value="All">All Severities</option>
            {options.severities.map((s) => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
        </div>

        {/* Year Filter */}
        <div className="w-full lg:w-auto">
          <select
            value={filters.year}
            onChange={(e) => onChange({ ...filters, year: parseInt(e.target.value) || 0 })}
            className="w-full lg:w-auto min-h-[38px] bg-slate-50 border border-slate-200 text-xs rounded-lg px-3 py-2 text-slate-800 font-medium focus:outline-none focus:border-brand-teal focus:bg-white transition shadow-2xs"
          >
            <option value={0}>All Years</option>
            {options.years.map((y) => (
              <option key={y} value={y}>{y}</option>
            ))}
          </select>
        </div>

        {/* Weather Filter */}
        {options.weather && options.weather.length > 0 && (
          <div className="w-full lg:w-auto">
            <select
              value={filters.weather}
              onChange={(e) => onChange({ ...filters, weather: e.target.value })}
              className="w-full lg:w-auto min-h-[38px] bg-slate-50 border border-slate-200 text-xs rounded-lg px-3 py-2 text-slate-800 font-medium focus:outline-none focus:border-brand-teal focus:bg-white transition shadow-2xs"
            >
              <option value="All">All Weather</option>
              {options.weather.map((w) => (
                <option key={w} value={w}>{w}</option>
              ))}
            </select>
          </div>
        )}

        {/* Road Type Filter */}
        {options.road_types && options.road_types.length > 0 && (
          <div className="w-full lg:w-auto">
            <select
              value={filters.road_type}
              onChange={(e) => onChange({ ...filters, road_type: e.target.value })}
              className="w-full lg:w-auto min-h-[38px] bg-slate-50 border border-slate-200 text-xs rounded-lg px-3 py-2 text-slate-800 font-medium focus:outline-none focus:border-brand-teal focus:bg-white transition shadow-2xs"
            >
              <option value="All">All Road Types</option>
              {options.road_types.map((r) => (
                <option key={r} value={r}>{r}</option>
              ))}
            </select>
          </div>
        )}

        {/* Desktop Reset Button */}
        <button
          onClick={onReset}
          className="hidden lg:flex ml-auto items-center gap-1.5 text-xs text-slate-600 hover:text-slate-900 bg-white hover:bg-slate-50 px-2.5 py-1.5 rounded-lg border border-slate-200 hover:border-slate-300 font-medium transition shadow-2xs"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          <span>Reset Filters</span>
        </button>
      </div>
    </div>
  );
}
