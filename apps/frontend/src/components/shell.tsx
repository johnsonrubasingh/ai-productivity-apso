import type { ReactNode } from "react";

const navItems = [
  { label: "Dashboard", href: "/" },
  { label: "Auth", href: "/auth" },
  { label: "Setup", href: "/setup" },
  { label: "Ingestion", href: "/ingestion" },
  { label: "Explorer", href: "/explorer" },
  { label: "Workbench", href: "/workbench" },
  { label: "Findings", href: "/findings" },
  { label: "Integrations", href: "/integrations" },
  { label: "API Contract", href: "/api-contract" },
];

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen bg-[var(--background)]">
      <aside className="fixed inset-y-0 left-0 hidden w-64 border-r border-[var(--border)] bg-white lg:block">
        <div className="flex h-16 items-center border-b border-[var(--border)] px-6">
          <div>
            <div className="text-lg font-semibold tracking-[0]">APSO</div>
            <div className="text-xs font-medium text-[var(--muted)]">SDLC intelligence</div>
          </div>
        </div>
        <nav className="space-y-1 px-3 py-4">
          {navItems.map((item) => (
            <a
              className="focus-ring flex h-10 items-center rounded-md px-3 text-sm font-medium text-slate-700 hover:bg-slate-100"
              href={item.href}
              key={item.href}
            >
              {item.label}
            </a>
          ))}
        </nav>
      </aside>
      <div className="lg:pl-64">
        <header className="sticky top-0 z-10 border-b border-[var(--border)] bg-white/95 backdrop-blur">
          <div className="flex min-h-16 flex-wrap items-center justify-between gap-3 px-4 py-3 sm:px-6">
            <div>
              <div className="text-sm font-semibold text-[var(--muted)]">Development workspace</div>
              <h1 className="text-xl font-semibold tracking-[0] text-[var(--foreground)] sm:text-2xl">
                APSO Control Center
              </h1>
            </div>
            <div className="flex flex-wrap items-center gap-2">
              <a
                className="focus-ring rounded-md border border-[var(--border)] bg-white px-3 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50"
                href="/ingestion"
              >
                Ingestion
              </a>
              <a
                className="focus-ring rounded-md bg-[var(--accent)] px-3 py-2 text-sm font-semibold text-white hover:bg-teal-800"
                href="#release"
              >
                Readiness
              </a>
            </div>
          </div>
        </header>
        <main className="px-4 py-6 sm:px-6">{children}</main>
      </div>
    </div>
  );
}
