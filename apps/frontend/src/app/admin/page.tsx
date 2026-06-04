import { AdminConsole } from "@/components/admin-console";
import { AppShell } from "@/components/shell";

export default function AdminPage() {
  return (
    <AppShell>
      <AdminConsole />
    </AppShell>
  );
}
