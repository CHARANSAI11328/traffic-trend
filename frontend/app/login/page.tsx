"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { TopNav } from "@/components/layout/TopNav";
import { api } from "@/services/api";
import { Lock, ShieldAlert, CheckCircle2, AlertCircle, LogOut } from "lucide-react";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("admin@traffictrend.io");
  const [password, setPassword] = useState("TrafficTrend2026!");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentUser, setCurrentUser] = useState<any | null>(null);

  useEffect(() => {
    const token = localStorage.getItem("traffictrend_token");
    if (token) {
      api.getMe().then(setCurrentUser).catch(() => localStorage.removeItem("traffictrend_token"));
    }
  }, []);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setLoading(true);
      setError(null);
      const res = await api.jsonLogin({ email, password });
      if (res.access_token) {
        localStorage.setItem("traffictrend_token", res.access_token);
        const me = await api.getMe();
        setCurrentUser(me);
        router.push("/data-management");
      }
    } catch (err: any) {
      setError(err.message || "Invalid operator credentials");
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("traffictrend_token");
    setCurrentUser(null);
  };

  return (
    <div className="flex-1 flex flex-col min-h-screen bg-[#f4f6f8]">
      <TopNav />

      <div className="flex-1 flex items-center justify-center p-4 sm:p-6">
        <div className="w-full max-w-md bg-white border border-slate-200/80 rounded-2xl p-5 sm:p-8 shadow-lg">
          <div className="text-center mb-6">
            <div className="w-12 h-12 rounded-xl bg-teal-50 border border-teal-200 flex items-center justify-center mx-auto mb-3 shadow-sm">
              <ShieldAlert className="w-6 h-6 text-brand-teal" />
            </div>
            <h2 className="text-xl font-bold text-slate-900 tracking-tight">Operator Authentication</h2>
            <p className="text-xs text-slate-500 mt-1">
              Required for dataset upload, cleaning execution, and administrative pipeline control.
            </p>
          </div>

          {currentUser ? (
            <div className="space-y-4 text-center">
              <div className="p-4 bg-slate-50 rounded-xl border border-slate-200">
                <CheckCircle2 className="w-8 h-8 text-emerald-600 mx-auto mb-2" />
                <span className="text-sm font-semibold text-slate-900 block">{currentUser.full_name || currentUser.email}</span>
                <span className="text-xs text-brand-teal font-mono font-semibold block mt-0.5">Role: {currentUser.role?.toUpperCase()}</span>
                <span className="text-[11px] text-slate-500 block mt-1">{currentUser.email}</span>
              </div>

              <div className="flex gap-3">
                <button
                  onClick={() => router.push("/data-management")}
                  className="flex-1 py-2 px-4 rounded-lg bg-brand-teal hover:bg-[#084248] text-xs font-semibold text-white transition shadow-sm"
                >
                  Data Management
                </button>
                <button
                  onClick={handleLogout}
                  className="py-2 px-4 rounded-lg border border-slate-300 hover:bg-slate-50 text-xs font-medium text-slate-700 flex items-center gap-1.5 transition"
                >
                  <LogOut className="w-3.5 h-3.5" />
                  <span>Sign Out</span>
                </button>
              </div>
            </div>
          ) : (
            <form onSubmit={handleLogin} className="space-y-4 text-xs">
              {error && (
                <div className="bg-red-50 border border-red-200 text-red-700 p-3 rounded-xl flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 shrink-0 text-red-500" />
                  <span>{error}</span>
                </div>
              )}

              <div>
                <label className="text-slate-700 font-medium block mb-1">Operator Email</label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full px-3 py-2.5 bg-slate-50 border border-slate-300 rounded-lg text-slate-900 focus:outline-none focus:border-brand-teal"
                  required
                />
              </div>

              <div>
                <label className="text-slate-700 font-medium block mb-1">Password</label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full px-3 py-2.5 bg-slate-50 border border-slate-300 rounded-lg text-slate-900 focus:outline-none focus:border-brand-teal"
                  required
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full py-2.5 px-4 bg-brand-teal hover:bg-[#084248] text-white font-semibold rounded-lg shadow-sm disabled:opacity-40 transition flex items-center justify-center gap-2"
              >
                <Lock className="w-4 h-4" />
                <span>{loading ? "Authenticating..." : "Authorize Operator Access"}</span>
              </button>

              <div className="mt-4 p-3 bg-slate-50 rounded-xl border border-slate-200 text-[11px] text-slate-600 text-center leading-relaxed">
                <span className="font-semibold text-slate-800">Seed Operator Credentials:</span>
                <br />
                <span className="font-mono text-slate-700">admin@traffictrend.io</span> &bull; <span className="font-mono text-slate-700">TrafficTrend2026!</span>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
