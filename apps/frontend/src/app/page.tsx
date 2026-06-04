import { DashboardSections } from "@/components/dashboard-sections";
import { AppShell } from "@/components/shell";
import { getDashboardData } from "@/lib/api";

export default async function Home() {
  const data = await getDashboardData();

  return (
    <AppShell>
      <DashboardSections data={data} />
    </AppShell>
  );
}
