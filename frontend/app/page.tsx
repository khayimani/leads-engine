"use client";

import * as React from "react";
import { Logo } from "@/components/Logo";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { Search, Rocket, Download, Mail, User, Building2, Target, CheckCircle2, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { api, type Lead } from "@/lib/api";

export default function DashboardPage() {
  const [role, setRole] = React.useState("Founder");
  const [industry, setIndustry] = React.useState("Fintech");
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const [leads, setLeads] = React.useState<Lead[]>([]);

  const fetchLeads = React.useCallback(async () => {
    try {
      const data = await api.getLeads();
      setLeads(data);
      setError(null);
    } catch (err) {
      console.error("Failed to fetch leads:", err);
      // Don't set global error here to avoid blocking UI, maybe just log or toast
    }
  }, []);

  React.useEffect(() => {
    fetchLeads();
  }, [fetchLeads]);

  // Poll for leads when loading
  React.useEffect(() => {
    let interval: NodeJS.Timeout;
    if (loading) {
      interval = setInterval(fetchLeads, 3000);
    }
    return () => clearInterval(interval);
  }, [loading, fetchLeads]);

  const handleLaunch = async () => {
    if (!role || !industry) return;

    setLoading(true);
    setError(null);
    try {
      await api.startJob(role, industry);
      // We keep loading true to trigger polling
      // In a real app, we'd have a job ID to track
      setTimeout(() => setLoading(false), 30000); // Stop loading after 30s as a fallback
    } catch (err: any) {
      console.error("Failed to start job:", err);
      const errorMessage = err.response?.data?.message || err.message || "Failed to start the scraping job. Please try again.";
      setError(`Error: ${errorMessage}`);
      setLoading(false);
    }
  };

  const downloadCSV = () => {
    if (leads.length === 0) return;

    const headers = ["Name", "Email", "Company", "Role", "Intent", "Status"];
    const csvContent = [
      headers.join(","),
      ...leads.map(l => [
        l.Name,
        l.Email || "",
        l.Company,
        l.Role,
        l.Intent,
        l.Status
      ].map(v => `"${v}"`).join(","))
    ].join("\n");

    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", `leads_${new Date().toISOString().split('T')[0]}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const totalLeads = leads.length;
  const emailsFound = leads.filter(l => l.Email).length;
  const successRate = totalLeads > 0 ? Math.round((emailsFound / totalLeads) * 100) : 0;

  return (
    <main className="min-h-screen p-8 max-w-7xl mx-auto">
      <header className="flex items-center justify-between mb-12">
        <Logo />
        <div className="flex items-center gap-4">
          <span className="text-sm text-muted">v1.0.0</span>
          <div className="h-8 w-px bg-gray-200" />
          <Button variant="ghost" className="text-sm font-medium">Documentation</Button>
        </div>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* Sidebar / Search */}
        <aside className="lg:col-span-1">
          <Card className="sticky top-8">
            <div className="flex items-center gap-2 mb-6">
              <Search className="w-5 h-5 text-foreground" />
              <h2 className="font-semibold text-lg">Search Leads</h2>
            </div>

            <div className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium text-muted">Target Role</label>
                <Input
                  value={role}
                  onChange={(e) => setRole(e.target.value)}
                  placeholder="e.g. Founder, CEO"
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium text-muted">Industry</label>
                <Input
                  value={industry}
                  onChange={(e) => setIndustry(e.target.value)}
                  placeholder="e.g. Fintech, SaaS"
                />
              </div>

              <Button
                onClick={handleLaunch}
                disabled={loading}
                className="w-full mt-4"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Hunting...
                  </>
                ) : (
                  <>
                    <Rocket className="w-4 h-4" />
                    Launch Scraper
                  </>
                )}
              </Button>
              {error && (
                <div className="p-3 text-sm text-red-600 bg-red-50 rounded-md mt-2">
                  {error}
                </div>
              )}
            </div>
          </Card>
        </aside>

        {/* Main Content */}
        <section className="lg:col-span-3 space-y-8">
          {/* Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card className="flex flex-col gap-1">
              <span className="text-sm text-muted font-medium">Total Leads</span>
              <span className="text-3xl font-bold">{totalLeads}</span>
            </Card>
            <Card className="flex flex-col gap-1">
              <span className="text-sm text-muted font-medium">Emails Found</span>
              <span className="text-3xl font-bold">{emailsFound}</span>
            </Card>
            <Card className="flex flex-col gap-1">
              <span className="text-sm text-muted font-medium">Success Rate</span>
              <span className="text-3xl font-bold text-green-600">{successRate}%</span>
            </Card>
          </div>

          {/* Results */}
          <Card className="p-0 overflow-hidden">
            <div className="p-6 border-b border-gray-100 flex items-center justify-between">
              <h3 className="font-semibold text-lg">Lead Results</h3>
              {leads.length > 0 && (
                <Button
                  variant="secondary"
                  className="py-2 px-4 text-sm"
                  onClick={downloadCSV}
                >
                  <Download className="w-4 h-4" />
                  Download CSV
                </Button>
              )}
            </div>

            <div className="overflow-x-auto">
              {leads.length > 0 ? (
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="bg-gray-50/50">
                      <th className="p-4 text-sm font-medium text-muted border-b border-gray-100">Name</th>
                      <th className="p-4 text-sm font-medium text-muted border-b border-gray-100">Email</th>
                      <th className="p-4 text-sm font-medium text-muted border-b border-gray-100">Company</th>
                      <th className="p-4 text-sm font-medium text-muted border-b border-gray-100">Role</th>
                      <th className="p-4 text-sm font-medium text-muted border-b border-gray-100">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {leads.map((lead) => (
                      <tr key={lead.id} className="hover:bg-gray-50/30 transition-colors">
                        <td className="p-4 border-b border-gray-100">
                          <div className="flex items-center gap-2">
                            <User className="w-4 h-4 text-muted" />
                            <span className="font-medium">{lead.Name}</span>
                          </div>
                        </td>
                        <td className="p-4 border-b border-gray-100">
                          <div className="flex items-center gap-2">
                            <Mail className="w-4 h-4 text-muted" />
                            <span className={lead.Email ? "text-foreground" : "text-muted italic"}>
                              {lead.Email || "Not found"}
                            </span>
                          </div>
                        </td>
                        <td className="p-4 border-b border-gray-100">
                          <div className="flex items-center gap-2">
                            <Building2 className="w-4 h-4 text-muted" />
                            <span>{lead.Company}</span>
                          </div>
                        </td>
                        <td className="p-4 border-b border-gray-100">
                          <div className="flex items-center gap-2">
                            <Target className="w-4 h-4 text-muted" />
                            <span>{lead.Role}</span>
                          </div>
                        </td>
                        <td className="p-4 border-b border-gray-100">
                          <div className="flex items-center gap-3">
                            {lead.Status === "Verified" ? (
                              <div className="flex items-center gap-1.5 text-green-600 bg-green-50 px-2 py-1 rounded-full text-xs font-semibold">
                                <CheckCircle2 className="w-3 h-3" />
                                Verified
                              </div>
                            ) : (
                              <div className="flex items-center gap-1.5 text-amber-600 bg-amber-50 px-2 py-1 rounded-full text-xs font-semibold">
                                <Loader2 className="w-3 h-3 animate-spin" />
                                Pending
                              </div>
                            )}
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              ) : (
                <div className="p-12 text-center">
                  <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-gray-50 mb-4">
                    <Search className="w-6 h-6 text-muted" />
                  </div>
                  <h4 className="text-lg font-medium mb-1">No leads found</h4>
                  <p className="text-muted text-sm">Enter a role and industry to start hunting for leads.</p>
                </div>
              )}
            </div>
          </Card>
        </section>
      </div>
    </main>
  );
}
