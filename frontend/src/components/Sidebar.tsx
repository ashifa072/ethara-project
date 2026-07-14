"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const navItems = [
  { href: "/", label: "Dashboard", icon: "📊" },
  { href: "/employees", label: "Employees", icon: "👥" },
  { href: "/seats", label: "Seats", icon: "💺" },
  { href: "/new-joiners", label: "New Joiners", icon: "🆕" },
  { href: "/ai-assistant", label: "AI Assistant", icon: "🤖" },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="fixed left-0 top-0 z-40 h-screen w-64 bg-slate-900 text-white shadow-xl">
      <div className="flex h-16 items-center border-b border-slate-700 px-6">
        <div>
          <h1 className="text-lg font-bold tracking-tight">Ethara</h1>
          <p className="text-xs text-slate-400">Seat Allocation System</p>
        </div>
      </div>
      <nav className="mt-6 px-3">
        {navItems.map((item) => {
          const active = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`mb-1 flex items-center gap-3 rounded-lg px-4 py-3 text-sm font-medium transition-colors ${
                active
                  ? "bg-indigo-600 text-white"
                  : "text-slate-300 hover:bg-slate-800 hover:text-white"
              }`}
            >
              <span className="text-lg">{item.icon}</span>
              {item.label}
            </Link>
          );
        })}
      </nav>
      <div className="absolute bottom-0 w-full border-t border-slate-700 p-4">
        <p className="text-xs text-slate-500">© 2026 Ethara Technologies</p>
      </div>
    </aside>
  );
}
