"use client";

import { useState } from "react";
import PageLayout from "@/components/PageLayout";
import { api } from "@/lib/api";

const EXAMPLE_QUERIES = [
  "Where is employee Amit seated?",
  "Where is my seat? My email is amit.patel100@ethara.ai",
  "Which project am I assigned to? My email is priya.sharma200@ethara.ai",
  "Show all available seats on Floor 3",
  "How many seats are occupied for Project Indigo?",
  "Who is sitting near me? My email is rajesh.kumar300@ethara.ai",
  "Show dashboard summary",
  "How many employees are pending allocation?",
];

interface Message {
  role: "user" | "assistant";
  content: string;
  intent?: string;
}

export default function AIAssistantPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content:
        "Hello! I'm the Ethara AI Assistant. I can help you find seat locations, project assignments, available seats, nearby colleagues, and utilization stats. Try asking a question!",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: userMessage }]);
    setLoading(true);

    try {
      const response = await api.aiQuery(userMessage);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: response.answer, intent: response.intent },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Sorry, I couldn't process your query. Please ensure the backend is running.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleExample = (query: string) => {
    setInput(query);
  };

  return (
    <PageLayout
      title="AI Assistant"
      subtitle="Ask natural language questions about seats, projects, and utilization"
    >
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <div className="flex h-[500px] flex-col rounded-xl border border-slate-200 bg-white shadow-sm">
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.map((msg, i) => (
                <div
                  key={i}
                  className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
                >
                  <div
                    className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm ${
                      msg.role === "user"
                        ? "bg-indigo-600 text-white"
                        : "bg-slate-100 text-slate-800"
                    }`}
                  >
                    <p>{msg.content}</p>
                    {msg.intent && (
                      <p className="mt-1 text-xs opacity-60">Intent: {msg.intent}</p>
                    )}
                  </div>
                </div>
              ))}
              {loading && (
                <div className="flex justify-start">
                  <div className="rounded-2xl bg-slate-100 px-4 py-3 text-sm text-slate-500">
                    Thinking...
                  </div>
                </div>
              )}
            </div>

            <form onSubmit={handleSubmit} className="border-t border-slate-200 p-4">
              <div className="flex gap-2">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Ask a question about seats, projects, or employees..."
                  className="flex-1 rounded-lg border border-slate-300 px-4 py-2.5 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                />
                <button
                  type="submit"
                  disabled={loading || !input.trim()}
                  className="rounded-lg bg-indigo-600 px-5 py-2.5 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50"
                >
                  Send
                </button>
              </div>
            </form>
          </div>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <h3 className="mb-4 text-lg font-semibold text-slate-900">Example Queries</h3>
          <div className="space-y-2">
            {EXAMPLE_QUERIES.map((query) => (
              <button
                key={query}
                onClick={() => handleExample(query)}
                className="w-full rounded-lg border border-slate-200 p-3 text-left text-xs text-slate-600 transition-colors hover:border-indigo-300 hover:bg-indigo-50"
              >
                {query}
              </button>
            ))}
          </div>
          <div className="mt-6 rounded-lg bg-slate-50 p-4">
            <h4 className="text-sm font-medium text-slate-700">Supported Intents</h4>
            <ul className="mt-2 space-y-1 text-xs text-slate-500">
              <li>Employee seat lookup</li>
              <li>My seat / project assignment</li>
              <li>Available seats by floor</li>
              <li>Nearby colleagues</li>
              <li>Project utilization</li>
              <li>Dashboard summary</li>
              <li>Pending allocations</li>
            </ul>
          </div>
        </div>
      </div>
    </PageLayout>
  );
}
