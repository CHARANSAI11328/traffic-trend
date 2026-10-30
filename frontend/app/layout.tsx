import "./globals.css";
import type { Metadata, Viewport } from "next";
import { Sidebar } from "@/components/layout/Sidebar";
import { MobileNavProvider } from "@/components/layout/MobileNavContext";

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 5,
};

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
      <body className="bg-background text-slate-900 flex min-h-screen font-sans antialiased selection:bg-brand-teal/20 selection:text-brand-teal overflow-x-hidden">
        <MobileNavProvider>
          <Sidebar />
          <main className="flex-1 flex flex-col min-w-0 w-full overflow-y-auto overflow-x-hidden">
            {children}
          </main>
        </MobileNavProvider>
      </body>
    </html>
  );
}
