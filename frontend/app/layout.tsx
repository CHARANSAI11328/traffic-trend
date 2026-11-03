import "./globals.css";
import type { Metadata, Viewport } from "next";
import Script from "next/script";
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
        {/* ModelDeck Personalized AI Assistant */}
        <Script
          src="https://modeldeck-git-main-charansai11328s-projects.vercel.app/embed.js"
          strategy="afterInteractive"
          data-assistant-id="asst-demo-mw0vbhbj"
          data-api-url="https://modeldeck-git-main-charansai11328s-projects.vercel.app"
          data-title="TRAFFIC TREND • AI Guide"
          data-greeting="Hi! 👋 I'm TRAFFIC TREND's AI Assistant. Ask me anything about TRAFFIC TREND's projects, technical skills, or experience!"
          data-avatar="🤖"
          data-color="#3b82f6"
          data-position="bottom-right"
          data-suggested="What are TRAFFIC TREND's main skills?,What projects have you worked on?,How can I get in touch with TRAFFIC TREND?"
          data-provider="groq"
          data-model="llama-3.3-70b-versatile"
        />
      </body>
    </html>
  );
}
