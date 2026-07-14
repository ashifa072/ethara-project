"use client";

import { ReactNode } from "react";

interface LayoutProps {
  children: ReactNode;
  title: string;
  subtitle?: string;
}

export default function PageLayout({ children, title, subtitle }: LayoutProps) {
  return (
    <div className="ml-64 min-h-screen bg-slate-50">
      <header className="border-b border-slate-200 bg-white px-8 py-6">
        <h1 className="text-2xl font-bold text-slate-900">{title}</h1>
        {subtitle && <p className="mt-1 text-sm text-slate-500">{subtitle}</p>}
      </header>
      <main className="p-8">{children}</main>
    </div>
  );
}
