import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { cn } from "@/lib/utils";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: "Leads Engine | AI Lead Generation",
  description: "AI-powered lead generation engine for modern sales teams.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full">
      <body
        className={cn(
          inter.variable,
          "antialiased h-full bg-grid"
        )}
      >
        {children}
      </body>
    </html>
  );
}
