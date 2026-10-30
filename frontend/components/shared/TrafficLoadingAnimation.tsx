"use client";

import React from "react";

interface TrafficLoadingProps {
  message?: string;
  subtext?: string;
  compact?: boolean;
}

export function TrafficLoadingAnimation({
  message = "Analyzing Spatiotemporal Road Safety Dynamics...",
  subtext = "Querying incident records & executing Python analytics engine",
  compact = false,
}: TrafficLoadingProps) {
  return (
    <div className={`flex flex-col items-center justify-center w-full ${compact ? "py-6" : "py-16"} px-4 select-none`}>
      <div className="relative w-full max-w-[480px] h-[130px] overflow-hidden rounded-xl bg-slate-50 border border-slate-200/80 shadow-sm flex flex-col justify-end">
        {/* Sky / Ambient background with subtle safety beacon */}
        <div className="absolute top-2 right-4 flex items-center gap-1.5 text-[10px] font-mono text-slate-400">
          <span className="w-2 h-2 rounded-full bg-brand-coral animate-ping"></span>
          <span>LIVE TELEMETRY CALCULATION</span>
        </div>

        {/* Hazard Marker in the Center of the Road */}
        <div className="absolute left-1/2 bottom-[32px] -translate-x-1/2 flex flex-col items-center z-10">
          {/* Warning Pulse Aura */}
          <div className="absolute -top-3 w-10 h-10 rounded-full bg-brand-coral/15 animate-ping pointer-events-none"></div>
          
          {/* Traffic Hazard Cone */}
          <svg className="w-6 h-6 text-brand-coral drop-shadow-sm" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 2L6 20h12L12 2z" fill="#e0533c" />
            <path d="M8 14h8l-1.33-4h-5.34L8 14z" fill="#ffffff" />
            <path d="M7 17h10l-.67-2H7.67L7 17z" fill="#e0533c" />
            <rect x="4" y="20" width="16" height="2" rx="1" fill="#0f172a" />
          </svg>
        </div>

        {/* Animated Motorcycle & Rider Cruising in from Left and Skidding at Center */}
        <div className="absolute bottom-[28px] left-0 w-full pointer-events-none">
          <div className="motorcycle-carrier">
            <svg
              className="motorcycle-svg w-16 h-12"
              viewBox="0 0 80 50"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              {/* Back Wheel */}
              <circle cx="16" cy="38" r="9" stroke="#1e293b" strokeWidth="4" fill="#64748b" />
              <circle cx="16" cy="38" r="3" fill="#cbd5e1" />

              {/* Front Wheel */}
              <circle cx="62" cy="38" r="9" stroke="#1e293b" strokeWidth="4" fill="#64748b" />
              <circle cx="62" cy="38" r="3" fill="#cbd5e1" />

              {/* Bike Chassis / Frame */}
              <path d="M16 38 L34 38 L48 24 L62 38" stroke="#0a545c" strokeWidth="3.5" strokeLinecap="round" strokeLinejoin="round" />
              <path d="M34 38 L30 22 L46 22" stroke="#0a545c" strokeWidth="3" strokeLinecap="round" />
              <path d="M48 24 L52 16 L56 16" stroke="#0f172a" strokeWidth="2.5" strokeLinecap="round" /> {/* Handlebars */}

              {/* Engine Block */}
              <rect x="28" y="28" width="14" height="9" rx="2" fill="#334155" />

              {/* Rider Body */}
              <path d="M32 20 C32 16, 38 12, 42 16 L46 24 L38 28 Z" fill="#0891b2" />

              {/* Rider Arms holding handlebar */}
              <path d="M40 18 L52 17" stroke="#0f172a" strokeWidth="2.5" strokeLinecap="round" />

              {/* Rider Helmet / Head */}
              <circle cx="44" cy="9" r="6" fill="#e0533c" />
              <path d="M44 7 H49 V11 H44 Z" fill="#0f172a" /> {/* Helmet Visor */}

              {/* Headlight Beam */}
              <path d="M64 22 L78 18 L78 30 L64 26 Z" fill="rgba(245, 158, 11, 0.25)" />
            </svg>
          </div>
        </div>

        {/* The Clean Road Surface */}
        <div className="relative w-full h-[28px] bg-slate-800 border-t-2 border-slate-700">
          {/* Dashed Center Road Markings */}
          <div className="road-strip flex items-center justify-around w-full h-full">
            <span className="w-8 h-1 bg-amber-400/90 rounded-full"></span>
            <span className="w-8 h-1 bg-amber-400/90 rounded-full"></span>
            <span className="w-8 h-1 bg-amber-400/90 rounded-full"></span>
            <span className="w-8 h-1 bg-amber-400/90 rounded-full"></span>
            <span className="w-8 h-1 bg-amber-400/90 rounded-full"></span>
            <span className="w-8 h-1 bg-amber-400/90 rounded-full"></span>
            <span className="w-8 h-1 bg-amber-400/90 rounded-full"></span>
          </div>
        </div>
      </div>

      {/* Explanatory Context Message */}
      <div className="mt-4 text-center max-w-md">
        <div className="flex items-center justify-center gap-2">
          <div className="w-2 h-2 rounded-full bg-brand-teal animate-pulse"></div>
          <span className="text-sm font-semibold text-slate-800 tracking-tight">
            {message}
          </span>
        </div>
        <p className="text-xs text-slate-500 mt-1 font-mono">
          {subtext}
        </p>
      </div>

      {/* Embedded CSS Animations for the Bike & Skid Dynamics */}
      <style jsx>{`
        @keyframes cruiseAndSkid {
          0% {
            transform: translateX(-80px);
          }
          45% {
            transform: translateX(180px) rotate(0deg);
          }
          52% {
            /* Hitting the hazard: front wheel tips up and bike skids */
            transform: translateX(205px) rotate(-18deg) translateY(-8px);
          }
          65% {
            /* Bike balances back and settles */
            transform: translateX(215px) rotate(4deg) translateY(0);
          }
          75% {
            transform: translateX(215px) rotate(0deg);
          }
          100% {
            /* Drives off safely */
            transform: translateX(540px) rotate(0deg);
          }
        }

        .motorcycle-carrier {
          display: inline-block;
          animation: cruiseAndSkid 4.8s cubic-bezier(0.4, 0, 0.2, 1) infinite;
        }

        @keyframes roadMove {
          0% {
            transform: translateX(0);
          }
          100% {
            transform: translateX(-40px);
          }
        }

        .road-strip {
          animation: roadMove 0.8s linear infinite;
        }
      `}</style>
    </div>
  );
}
