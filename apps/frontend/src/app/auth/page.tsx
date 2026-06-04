import { AuthTokenPanel } from "@/components/auth-token-panel";
import { AppShell } from "@/components/shell";

export default function AuthPage() {
  return (
    <AppShell>
      <AuthTokenPanel />
    </AppShell>
  );
}
