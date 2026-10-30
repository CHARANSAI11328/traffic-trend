"use client";

import { useEffect, useState } from "react";
import ReactECharts from "echarts-for-react";

interface EChartComponentProps {
  option: any;
  style?: React.CSSProperties;
  className?: string;
  theme?: string;
}

export function EChartComponent({
  option,
  style = { height: "350px", width: "100%" },
  className = "",
}: EChartComponentProps) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return (
      <div
        style={style}
        className={`flex items-center justify-center bg-surface-subtle/40 rounded-lg animate-pulse ${className}`}
      >
        <span className="text-xs text-slate-500 font-mono">Loading chart engine...</span>
      </div>
    );
  }

  return (
    <ReactECharts
      option={option}
      style={style}
      className={className}
      opts={{ renderer: "canvas" }}
      notMerge={true}
      lazyUpdate={true}
    />
  );
}
