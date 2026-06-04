type StatusPillProps = {
  label: string;
  tone?: "neutral" | "success" | "warning" | "danger" | "accent";
};

const tones: Record<NonNullable<StatusPillProps["tone"]>, string> = {
  neutral: "border-slate-200 bg-slate-50 text-slate-700",
  success: "border-emerald-200 bg-emerald-50 text-emerald-700",
  warning: "border-amber-200 bg-amber-50 text-amber-800",
  danger: "border-red-200 bg-red-50 text-red-700",
  accent: "border-teal-200 bg-teal-50 text-teal-800",
};

export function StatusPill({ label, tone = "neutral" }: StatusPillProps) {
  return (
    <span
      className={`inline-flex h-7 items-center whitespace-nowrap rounded-full border px-3 text-xs font-semibold ${tones[tone]}`}
    >
      {label}
    </span>
  );
}
