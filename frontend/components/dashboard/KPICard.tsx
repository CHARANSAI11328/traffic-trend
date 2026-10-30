"use client";

import { LucideIcon, TrendingDown, TrendingUp, Minus } from "lucide-react";
import { formatNumber } from "@/lib/utils";

interface KPICardProps {
  title: string;
  value: number | string;
  icon: LucideIcon;
  subtitle?: string;
  deltaPct?: number | null;
  deltaLabel?: string;
  inverseDeltaColors?: boolean; // If true, negative delta is good (e.g., accidents reduced)
  accentColor?: "cyan" | "red" | "amber" | "blue" | "emerald";
}

export function KPICard({
  title,
  value,
  icon: Icon,
  subtitle,
  deltaPct,
  deltaLabel = "vs prior period",
  inverseDeltaColors = true,
  accentColor = "cyan",
}: KPICardProps) {
  const getAccentStyles = () => {
    switch (accentColor) {
      case "red":
        return {
          iconBg: "bg-red-50 text-red-600 border-red-200",
          glow: "group-hover:border-red-300",
        };
      case "amber":
        return {
          iconBg: "bg-amber-50 text-amber-600 border-amber-200",
          glow: "group-hover:border-amber-300",
        };
      case "emerald":
        return {
          iconBg: "bg-emerald-50 text-emerald-600 border-emerald-200",
          glow: "group-hover:border-emerald-300",
        };
      case "blue":
        return {
          iconBg: "bg-blue-50 text-blue-600 border-blue-200",
          glow: "group-hover:border-blue-300",
        };
      default:
        return {
          iconBg: "bg-teal-50 text-brand-teal border-teal-200",
          glow: "group-hover:border-teal-300",
        };
    }
  };

  const accent = getAccentStyles();

  const renderDelta = () => {
    if (deltaPct === null || deltaPct === undefined) return null;

    const isZero = deltaPct === 0;
    const isPositive = deltaPct > 0;

    let isFavorable = isPositive;
    if (inverseDeltaColors) {
      isFavorable = !isPositive;
    }

    const badgeColor = isZero
      ? "bg-slate-100 text-slate-600 border-slate-200"
      : isFavorable
      ? "bg-emerald-50 text-emerald-700 border-emerald-200"
      : "bg-red-50 text-red-700 border-red-200";

    const DeltaIcon = isZero ? Minus : isPositive ? TrendingUp : TrendingDown;

    return (
      <div className="flex items-center gap-1.5 mt-2">
        <span
          className={`inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[11px] font-mono font-semibold border ${badgeColor}`}
        >
          <DeltaIcon className="w-3 h-3" />
          <span>{Math.abs(deltaPct).toFixed(1)}%</span>
        </span>
        <span className="text-[11px] text-slate-500 font-medium">{deltaLabel}</span>
      </div>
    );
  };

  return (
    <div
      className={`bg-white border border-slate-200/90 rounded-xl p-5 transition-all duration-200 shadow-xs hover:shadow-md hover:border-slate-300 group ${accent.glow}`}
    >
      <div className="flex items-start justify-between">
        <div>
          <span className="text-xs font-semibold text-slate-500 tracking-wider uppercase">
            {title}
          </span>
          <div className="text-2xl font-extrabold text-slate-900 mt-1 font-mono tracking-tight">
            {typeof value === "number" ? formatNumber(value) : value}
          </div>
        </div>
        <div
          className={`w-10 h-10 rounded-lg flex items-center justify-center border ${accent.iconBg} shadow-2xs`}
        >
          <Icon className="w-5 h-5" />
        </div>
      </div>

      {renderDelta()}

      {subtitle && (
        <div className="mt-2 text-xs text-slate-500 font-medium truncate">{subtitle}</div>
      )}
    </div>
  );
}
