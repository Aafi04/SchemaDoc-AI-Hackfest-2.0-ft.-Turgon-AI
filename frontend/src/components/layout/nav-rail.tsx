"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import {
  LayoutDashboard,
  TableProperties,
  GitFork,
  MessageSquare,
  Settings,
  Database,
} from "lucide-react";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/dashboard/schema", label: "Schema", icon: TableProperties },
  { href: "/dashboard/graph", label: "Graph", icon: GitFork },
  { href: "/dashboard/chat", label: "Chat", icon: MessageSquare },
  { href: "/dashboard/settings", label: "Settings", icon: Settings },
];

export function NavRail() {
  const pathname = usePathname();

  return (
    <nav className="fixed left-0 top-0 z-40 flex h-screen w-16 flex-col items-center border-r border-zinc-800 bg-zinc-950 py-4">
      {/* Logo */}
      <Link
        href="/"
        className="mb-8 flex h-10 w-10 items-center justify-center rounded-lg bg-blue-500/10 text-blue-400 transition-colors hover:bg-blue-500/20"
      >
        <Database className="h-5 w-5" />
      </Link>

      {/* Nav Items */}
      <div className="flex flex-1 flex-col items-center gap-2">
        {navItems.map((item) => {
          const isActive =
            item.href === "/dashboard"
              ? pathname === "/dashboard"
              : pathname.startsWith(item.href);

          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "group relative flex h-10 w-10 items-center justify-center rounded-lg transition-all duration-200",
                isActive
                  ? "bg-blue-500/15 text-blue-400"
                  : "text-zinc-500 hover:bg-zinc-800 hover:text-zinc-300",
              )}
            >
              <item.icon className="h-5 w-5" />
              {/* Tooltip */}
              <span className="pointer-events-none absolute left-14 rounded-md bg-zinc-800 px-2 py-1 text-xs font-medium text-zinc-200 opacity-0 shadow-lg transition-opacity group-hover:opacity-100">
                {item.label}
              </span>
              {/* Active indicator */}
              {isActive && (
                <span className="absolute -left-[1.45rem] h-5 w-1 rounded-r-full bg-blue-500" />
              )}
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
