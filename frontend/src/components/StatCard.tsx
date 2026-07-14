interface StatCardProps {
  title: string;
  value: number | string;
  subtitle?: string;
  color?: "blue" | "green" | "yellow" | "red" | "purple" | "indigo";
}

const colorMap = {
  blue: "bg-blue-50 border-blue-200 text-blue-700",
  green: "bg-green-50 border-green-200 text-green-700",
  yellow: "bg-yellow-50 border-yellow-200 text-yellow-700",
  red: "bg-red-50 border-red-200 text-red-700",
  purple: "bg-purple-50 border-purple-200 text-purple-700",
  indigo: "bg-indigo-50 border-indigo-200 text-indigo-700",
};

export default function StatCard({ title, value, subtitle, color = "blue" }: StatCardProps) {
  return (
    <div className={`rounded-xl border p-5 ${colorMap[color]}`}>
      <p className="text-sm font-medium opacity-80">{title}</p>
      <p className="mt-2 text-3xl font-bold">{value.toLocaleString()}</p>
      {subtitle && <p className="mt-1 text-xs opacity-60">{subtitle}</p>}
    </div>
  );
}
