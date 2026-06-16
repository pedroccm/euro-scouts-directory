import { cn } from "@/lib/utils";

const LEAGUE_STYLES: Record<string, string> = {
  "Premier League": "bg-violet-100 text-violet-700 ring-violet-600/20",
  "La Liga": "bg-orange-100 text-orange-700 ring-orange-600/20",
  "Serie A": "bg-sky-100 text-sky-700 ring-sky-600/20",
  Bundesliga: "bg-red-100 text-red-700 ring-red-600/20",
  "Ligue 1": "bg-blue-100 text-blue-700 ring-blue-600/20",
  MLS: "bg-emerald-100 text-emerald-700 ring-emerald-600/20",
  Eredivisie: "bg-amber-100 text-amber-700 ring-amber-600/20",
  "Liga Portugal": "bg-green-100 text-green-700 ring-green-600/20",
  "Liga Portugal 2": "bg-lime-100 text-lime-700 ring-lime-600/20",
  Championship: "bg-fuchsia-100 text-fuchsia-700 ring-fuchsia-600/20",
  "League One": "bg-pink-100 text-pink-700 ring-pink-600/20",
  "2. Bundesliga": "bg-rose-100 text-rose-700 ring-rose-600/20",
  "Brasileirão Série A": "bg-yellow-100 text-yellow-800 ring-yellow-600/20",
  "Brasileirão Série B": "bg-teal-100 text-teal-700 ring-teal-600/20",
  "Brasileirão Série C": "bg-cyan-100 text-cyan-700 ring-cyan-600/20",
  "Brasileirão Série D": "bg-indigo-100 text-indigo-700 ring-indigo-600/20",
  "Belgian Pro League": "bg-red-100 text-red-700 ring-red-600/20",
  "Ukrainian Premier League": "bg-sky-100 text-sky-700 ring-sky-600/20",
  "Cypriot First Division": "bg-orange-100 text-orange-700 ring-orange-600/20",
  "Scottish Premiership": "bg-blue-100 text-blue-700 ring-blue-600/20",
  "Super League Greece": "bg-cyan-100 text-cyan-700 ring-cyan-600/20",
  "Süper Lig": "bg-red-100 text-red-700 ring-red-600/20",
  "Saudi Pro League": "bg-green-100 text-green-700 ring-green-600/20",
  "Liga Profesional Argentina": "bg-sky-100 text-sky-700 ring-sky-600/20",
  "Swiss Super League": "bg-rose-100 text-rose-700 ring-rose-600/20",
  "Austrian Bundesliga": "bg-red-100 text-red-700 ring-red-600/20",
  "Liga MX": "bg-emerald-100 text-emerald-700 ring-emerald-600/20",
  "Danish Superliga": "bg-red-100 text-red-700 ring-red-600/20",
  Ekstraklasa: "bg-amber-100 text-amber-700 ring-amber-600/20",
  Allsvenskan: "bg-yellow-100 text-yellow-800 ring-yellow-600/20",
  Eliteserien: "bg-blue-100 text-blue-700 ring-blue-600/20",
};

export function LeagueBadge({
  league,
  className,
}: {
  league: string;
  className?: string;
}) {
  return (
    <span
      className={cn(
        "inline-flex items-center whitespace-nowrap rounded-md px-2 py-0.5 text-xs font-medium ring-1 ring-inset",
        LEAGUE_STYLES[league] ?? "bg-slate-100 text-slate-700 ring-slate-600/20",
        className
      )}
    >
      {league}
    </span>
  );
}
