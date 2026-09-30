import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import "leaflet/dist/leaflet.css";
import { AppShell } from "@/components/AppShell";

const inter = Inter({ subsets: ["latin"], variable: "--font-sans", display: "swap" });
const mono = JetBrains_Mono({ subsets: ["latin"], variable: "--font-mono", display: "swap" });

export const metadata: Metadata = {
  title: {
    default: "SkillPulse India — District Labour Market Intelligence",
    template: "%s · SkillPulse India",
  },
  description:
    "District-level labour-market intelligence: measure skill demand, detect emerging skills, find training-supply gaps, and generate evidence-based skill-development plans.",
  applicationName: "SkillPulse India",
  keywords: [
    "labour market intelligence",
    "skill gap analysis",
    "skill development",
    "district training plan",
    "India",
    "SIH26134",
  ],
  openGraph: {
    title: "SkillPulse India — District Labour Market Intelligence",
    description:
      "From job-market signals to district training plans. Evidence-based skill-development intelligence.",
    type: "website",
  },
  robots: { index: true, follow: true },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${inter.variable} ${mono.variable}`}>
      <body>
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}
