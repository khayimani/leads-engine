import * as React from "react";
import { cn } from "@/lib/utils";

export function Logo({ className }: { className?: string }) {
    return (
        <div className={cn("logo-wrap", className)}>
            <div className="logo-square">
                <svg
                    width="24"
                    height="24"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2.5"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                >
                    <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z" />
                </svg>
            </div>
            <div className="logo-text">
                <span className="reveal-inner">Leads Engine</span>
            </div>
        </div>
    );
}
