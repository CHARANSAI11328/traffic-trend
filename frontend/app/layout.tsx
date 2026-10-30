import "./globals.css";
import type { Metadata } from "next";
import { Sidebar } from "@/components/layout/Sidebar";

export const metadata: Metadata = {
  title: "TRAFFIC TREND — Road Safety Intelligence & Accident Analytics",
  description: "Enterprise Road Accident Analytics, Geographical Hotspotting, and Severity Intelligence Platform",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-background text-slate-900 flex min-h-screen font-sans antialiased selection:bg-brand-teal/20 selection:text-brand-teal">
        <Sidebar />
        <main className="flex-1 flex flex-col min-w-0 overflow-y-auto">
          {children}
        </main>
      </body>
    </html>
  );
}
