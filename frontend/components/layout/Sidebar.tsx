"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Car,
  MapPin,
  TrendingUp,
  AlertTriangle,
  Brain,
  Database,
  FileSpreadsheet,
  Activity,
  ShieldAlert,
  ChevronRight,
  Lock,
  Unlock,
} from "lucide-react";

const navigation = [
  { name: "Executive Overview", href: "/overview", icon: LayoutDashboard },
  { name: "Accident Analysis", href: "/accidents", icon: Car },
  { name: "Geographical Intelligence", href: "/geography", icon: MapPin },
  { name: "Temporal Intelligence", href: "/trends", icon: TrendingUp },
  { name: "Severity Intelligence", href: "/severity", icon: AlertTriangle },
  { name: "Risk Intelligence", href: "/intelligence", icon: Brain },
  { name: "Data Management", href: "/data-management", icon: Database },
  { name: "Executive Reports", href: "/reports", icon: FileSpreadsheet },
  { name: "System Monitoring", href: "/system", icon: Activity },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 bg-white border-r border-slate-200 flex flex-col shrink-0 h-screen sticky top-0 select-none z-30 shadow-xs">
      {/* Brand Header */}
      <div className="h-16 flex items-center px-5 border-b border-slate-200 gap-3 bg-white">
        <div className="w-9 h-9 rounded-lg bg-brand-teal flex items-center justify-center shadow-md shadow-brand-teal/20">
          <ShieldAlert className="w-5 h-5 text-white" />
        </div>
        <div>
          <span className="font-bold tracking-tight text-slate-900 text-base block leading-none">
            TRAFFIC TREND
          </span>
          <span className="text-[10px] text-brand-teal font-mono tracking-wider uppercase block mt-1 font-semibold">
            Safety Intelligence
          </span>
        </div>
      </div>

      {/* Navigation Items */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        <div className="text-[10px] uppercase font-mono tracking-wider text-slate-400 px-3 mb-2 font-semibold">
          Analytics Engine
        </div>
        {navigation.map((item) => {
          const isActive = pathname === item.href || (item.href === "/overview" && pathname === "/");
          const Icon = item.icon;

          return (
            <Link
              key={item.name}
              href={item.href}
              className={`flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium transition-all group ${
                isActive
                  ? "bg-teal-50/90 text-brand-teal border border-teal-200 font-semibold shadow-xs"
                  : "text-slate-600 hover:text-slate-900 hover:bg-slate-100/70"
              }`}
            >
              <div className="flex items-center gap-3">
                <Icon
                  className={`w-4 h-4 transition-colors ${
                    isActive ? "text-brand-teal" : "text-slate-400 group-hover:text-slate-600"
                  }`}
                />
                <span>{item.name}</span>
              </div>
              {isActive && <ChevronRight className="w-3.5 h-3.5 text-brand-teal" />}
            </Link>
          );
        })}
      </nav>

      {/* Live Status Badge & Login Status */}
      <div className="p-4 border-t border-slate-200 bg-slate-50/60">
        <div className="rounded-lg bg-white p-3 border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between text-xs mb-1.5">
            <span className="text-slate-500 font-medium">Data Feed</span>
            <span className="flex items-center gap-1.5 text-[11px] text-amber-700 font-mono font-semibold">
              <span className="w-1.5 h-1.5 rounded-full bg-amber-500 animate-pulse"></span>
              Historical
            </span>
          </div>
          <div className="text-[11px] text-slate-600 truncate font-medium">
            Benchmark Dataset Active
          </div>
        </div>

        <Link
          href="/login"
          className="mt-3 flex items-center justify-center gap-2 text-xs py-2 px-3 rounded-lg border border-slate-200 hover:border-slate-300 bg-white hover:bg-slate-50 text-slate-700 font-medium transition shadow-xs"
        >
          <Lock className="w-3.5 h-3.5 text-slate-500" />
          <span>Operator Access</span>
        </Link>
      </div>
    </aside>
  );
}
