import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatNumber(num: number | undefined | null): string {
  if (num === undefined || num === null) return "0";
  return new Intl.NumberFormat("en-US").format(num);
}

export function formatPercent(num: number | undefined | null): string {
  if (num === undefined || num === null) return "0.0%";
  return `${num.toFixed(1)}%`;
}
