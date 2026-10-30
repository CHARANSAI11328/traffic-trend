"use client";

import { Filter, RotateCcw } from "lucide-react";
import { FilterOptions, FilterState } from "@/types";

interface FilterBarProps {
  options: FilterOptions;
  filters: FilterState;
  onChange: (filters: FilterState) => void;
  onReset: () => void;
}

export function GlobalFilterBar({ options, filters, onChange, onReset }: FilterBarProps) {
  return (
    <div className="bg-white border border-slate-200 rounded-xl p-3 mb-6 flex flex-wrap items-center gap-3 shadow-xs">
      <div className="flex items-center gap-2 text-xs font-bold text-brand-teal uppercase tracking-wider pl-1 pr-3 border-r border-slate-200">
        <Filter className="w-3.5 h-3.5" />
        <span>Filters</span>
      </div>

      {/* State Filter */}
      <div className="flex flex-col">
        <select
          value={filters.state}
          onChange={(e) => onChange({ ...filters, state: e.target.value })}
          className="bg-slate-50 border border-slate-200 text-xs rounded-lg px-2.5 py-1.5 text-slate-800 font-medium focus:outline-none focus:border-brand-teal focus:bg-white transition shadow-2xs"
        >
          <option value="All">All States / Regions</option>
          {options.states.map((s) => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>
      </div>

      {/* Severity Filter */}
      <div className="flex flex-col">
        <select
          value={filters.severity}
          onChange={(e) => onChange({ ...filters, severity: e.target.value })}
          className="bg-slate-50 border border-slate-200 text-xs rounded-lg px-2.5 py-1.5 text-slate-800 font-medium focus:outline-none focus:border-brand-teal focus:bg-white transition shadow-2xs"
        >
          <option value="All">All Severities</option>
          {options.severities.map((s) => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>
      </div>

      {/* Year Filter */}
      <div className="flex flex-col">
        <select
          value={filters.year}
          onChange={(e) => onChange({ ...filters, year: parseInt(e.target.value) || 0 })}
          className="bg-slate-50 border border-slate-200 text-xs rounded-lg px-2.5 py-1.5 text-slate-800 font-medium focus:outline-none focus:border-brand-teal focus:bg-white transition shadow-2xs"
        >
          <option value={0}>All Years</option>
          {options.years.map((y) => (
            <option key={y} value={y}>{y}</option>
          ))}
        </select>
      </div>

      {/* Weather Filter */}
      {options.weather && options.weather.length > 0 && (
        <div className="flex flex-col">
          <select
            value={filters.weather}
            onChange={(e) => onChange({ ...filters, weather: e.target.value })}
            className="bg-slate-50 border border-slate-200 text-xs rounded-lg px-2.5 py-1.5 text-slate-800 font-medium focus:outline-none focus:border-brand-teal focus:bg-white transition shadow-2xs"
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
        <div className="flex flex-col">
          <select
            value={filters.road_type}
            onChange={(e) => onChange({ ...filters, road_type: e.target.value })}
            className="bg-slate-50 border border-slate-200 text-xs rounded-lg px-2.5 py-1.5 text-slate-800 font-medium focus:outline-none focus:border-brand-teal focus:bg-white transition shadow-2xs"
          >
            <option value="All">All Road Types</option>
            {options.road_types.map((r) => (
              <option key={r} value={r}>{r}</option>
            ))}
          </select>
        </div>
      )}

      {/* Reset */}
      <button
        onClick={onReset}
        className="ml-auto flex items-center gap-1.5 text-xs text-slate-600 hover:text-slate-900 bg-white hover:bg-slate-50 px-2.5 py-1.5 rounded-lg border border-slate-200 hover:border-slate-300 font-medium transition shadow-2xs"
      >
        <RotateCcw className="w-3.5 h-3.5" />
        <span>Reset Filters</span>
      </button>
    </div>
  );
}
