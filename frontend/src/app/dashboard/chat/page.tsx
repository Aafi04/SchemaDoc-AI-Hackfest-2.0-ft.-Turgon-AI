"use client";

import { useState, useRef, useEffect } from "react";
import { useMutation } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { cn } from "@/lib/utils";
import { motion, AnimatePresence } from "framer-motion";
import {
  Send,
  Bot,
  User,
  Loader2,
  Sparkles,
  MessageSquare,
  Copy,
  Check,
} from "lucide-react";

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  sql?: string;
  timestamp: Date;
}

function CodeBlock({ code }: { code: string }) {
  const [copied, setCopied] = useState(false);

  const copy = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="mt-2 overflow-hidden rounded-lg border border-zinc-700">
      <div className="flex items-center justify-between bg-zinc-800 px-3 py-1.5">
        <span className="text-[10px] font-medium uppercase tracking-wider text-zinc-500">
          SQL
        </span>
        <button
          onClick={copy}
          className="text-zinc-500 hover:text-zinc-300 transition-colors"
        >
          {copied ? (
            <Check className="h-3.5 w-3.5 text-emerald-400" />
          ) : (
            <Copy className="h-3.5 w-3.5" />
          )}
        </button>
      </div>
      <pre className="overflow-x-auto bg-zinc-900 p-3 font-mono text-xs text-blue-300">
        {code}
      </pre>
    </div>
  );
}

export default function ChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages]);

  const mutation = useMutation({
    mutationFn: (question: string) =>
      api.sendChatMessage({ question, db_path: "" }),
    onSuccess: (data) => {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: data.response,
          sql: data.sql_query ?? undefined,
          timestamp: new Date(),
        },
      ]);
    },
    onError: () => {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Sorry, I encountered an error. Please try again.",
          timestamp: new Date(),
        },
      ]);
    },
  });

  const send = () => {
    const q = input.trim();
    if (!q || mutation.isPending) return;

    setMessages((prev) => [
      ...prev,
      { role: "user", content: q, timestamp: new Date() },
    ]);
    setInput("");
    mutation.mutate(q);
  };

  const suggestions = [
    "Show me all tables with foreign key relationships",
    "Which tables have the most columns?",
    "Find all columns that store dates or timestamps",
    "What are the primary keys across all tables?",
  ];

  return (
    <div className="mx-auto flex h-[calc(100vh-140px)] max-w-4xl flex-col">
      {/* Header */}
      <div className="mb-4">
        <h1 className="text-2xl font-bold text-zinc-100">AI Chat</h1>
        <p className="mt-1 text-sm text-zinc-500">
          Ask questions about your database schema in natural language
        </p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto rounded-xl border border-zinc-800 bg-zinc-900/30 p-4">
        {messages.length === 0 ? (
          <div className="flex h-full flex-col items-center justify-center">
            <div className="mb-6 flex h-16 w-16 items-center justify-center rounded-2xl bg-blue-500/10">
              <Sparkles className="h-8 w-8 text-blue-400" />
            </div>
            <h2 className="mb-2 text-lg font-semibold text-zinc-200">
              Ask anything about your schema
            </h2>
            <p className="mb-8 text-sm text-zinc-500">
              I can help you understand your database structure, find
              relationships, and generate SQL queries.
            </p>

            {/* Suggestions */}
            <div className="grid max-w-lg grid-cols-1 gap-2 sm:grid-cols-2">
              {suggestions.map((s) => (
                <button
                  key={s}
                  onClick={() => setInput(s)}
                  className="rounded-lg border border-zinc-800 bg-zinc-900/50 px-3 py-2 text-left text-xs text-zinc-400 transition-colors hover:border-zinc-700 hover:text-zinc-300"
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            <AnimatePresence>
              {messages.map((msg, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  className={cn(
                    "flex gap-3",
                    msg.role === "user" ? "justify-end" : "justify-start",
                  )}
                >
                  {msg.role === "assistant" && (
                    <div className="flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-lg bg-blue-500/10">
                      <Bot className="h-4 w-4 text-blue-400" />
                    </div>
                  )}

                  <div
                    className={cn(
                      "max-w-[80%] rounded-xl px-4 py-3",
                      msg.role === "user"
                        ? "bg-blue-600 text-white"
                        : "bg-zinc-800 text-zinc-200",
                    )}
                  >
                    <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                    {msg.sql && <CodeBlock code={msg.sql} />}
                  </div>

                  {msg.role === "user" && (
                    <div className="flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-lg bg-zinc-700">
                      <User className="h-4 w-4 text-zinc-300" />
                    </div>
                  )}
                </motion.div>
              ))}
            </AnimatePresence>

            {mutation.isPending && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex gap-3"
              >
                <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-blue-500/10">
                  <Bot className="h-4 w-4 text-blue-400" />
                </div>
                <div className="rounded-xl bg-zinc-800 px-4 py-3">
                  <Loader2 className="h-4 w-4 animate-spin text-blue-400" />
                </div>
              </motion.div>
            )}

            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input */}
      <div className="mt-3 flex items-center gap-2">
        <div className="relative flex-1">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && send()}
            placeholder="Ask about your database schema..."
            className="w-full rounded-xl border border-zinc-700 bg-zinc-900 py-3 pl-4 pr-12 text-sm text-zinc-200 outline-none placeholder:text-zinc-600 focus:border-blue-500/50"
          />
          <button
            onClick={send}
            disabled={!input.trim() || mutation.isPending}
            className={cn(
              "absolute right-2 top-1/2 -translate-y-1/2 rounded-lg p-2 transition-all",
              input.trim() && !mutation.isPending
                ? "bg-blue-600 text-white hover:bg-blue-500"
                : "text-zinc-600",
            )}
          >
            <Send className="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
