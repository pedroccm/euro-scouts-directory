"use client";

import * as React from "react";
import {
  ArrowUpDown,
  Building2,
  ChevronLeft,
  ChevronRight,
  LayoutGrid,
  Linkedin,
  List as ListIcon,
  MapPin,
  Search,
  Table as TableIcon,
  Trophy,
  Users,
} from "lucide-react";

import { Scout, LEAGUE_ORDER } from "@/lib/types";
import { cn } from "@/lib/utils";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { LeagueBadge } from "@/components/league-badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

const ALL = "__all__";
type View = "cards" | "list" | "table";
type SortKey = "name" | "club" | "league" | "title" | "location";

const PAGE_SIZE: Record<View, number> = { cards: 48, list: 60, table: 50 };

function initials(name: string) {
  return (
    name
      .trim()
      .split(/\s+/)
      .map((p) => p[0])
      .slice(0, 2)
      .join("")
      .toUpperCase() || "?"
  );
}

function loc(s: Scout) {
  return [s.city, s.country].filter(Boolean).join(", ");
}

export function ScoutsDirectory() {
  const [scouts, setScouts] = React.useState<Scout[] | null>(null);
  const [q, setQ] = React.useState("");
  const [league, setLeague] = React.useState<string>(ALL);
  const [club, setClub] = React.useState<string>(ALL);
  const [view, setView] = React.useState<View>("cards");
  const [page, setPage] = React.useState(1);
  const [sortKey, setSortKey] = React.useState<SortKey>("name");
  const [sortDir, setSortDir] = React.useState<"asc" | "desc">("asc");

  React.useEffect(() => {
    fetch("/data.json")
      .then((r) => r.json())
      .then((d: Scout[]) => setScouts(d))
      .catch(() => setScouts([]));
  }, []);

  const leagues = React.useMemo(() => {
    if (!scouts) return [];
    const present = new Set(scouts.map((s) => s.league));
    return LEAGUE_ORDER.filter((l) => present.has(l));
  }, [scouts]);

  const clubs = React.useMemo(() => {
    if (!scouts) return [];
    const pool = scouts.filter((s) => league === ALL || s.league === league);
    return Array.from(new Set(pool.map((s) => s.club).filter(Boolean))).sort();
  }, [scouts, league]);

  const filtered = React.useMemo(() => {
    if (!scouts) return [];
    const needle = q.toLowerCase().trim();
    let out = scouts.filter((s) => {
      if (league !== ALL && s.league !== league) return false;
      if (club !== ALL && s.club !== club) return false;
      if (needle) {
        const hay = `${s.name} ${s.club} ${s.title} ${s.league} ${loc(s)}`.toLowerCase();
        if (!hay.includes(needle)) return false;
      }
      return true;
    });
    const dir = sortDir === "asc" ? 1 : -1;
    const val = (s: Scout) =>
      sortKey === "location" ? loc(s) : (s[sortKey] || "");
    out = [...out].sort((a, b) =>
      val(a).localeCompare(val(b), "pt", { sensitivity: "base" }) * dir
    );
    return out;
  }, [scouts, q, league, club, sortKey, sortDir]);

  const pageSize = PAGE_SIZE[view];
  const totalPages = Math.max(1, Math.ceil(filtered.length / pageSize));
  const curPage = Math.min(page, totalPages);
  const pageItems = filtered.slice((curPage - 1) * pageSize, curPage * pageSize);

  // reset para página 1 quando filtros/visão mudam
  React.useEffect(() => setPage(1), [q, league, club, view, sortKey, sortDir]);

  function toggleSort(key: SortKey) {
    if (sortKey === key) setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    else {
      setSortKey(key);
      setSortDir("asc");
    }
  }

  const stats = React.useMemo(() => {
    if (!scouts) return { total: 0, clubs: 0, leagues: 0 };
    return {
      total: scouts.length,
      clubs: new Set(scouts.map((s) => s.club)).size,
      leagues: new Set(scouts.map((s) => s.league)).size,
    };
  }, [scouts]);

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="border-b bg-gradient-to-b from-slate-50 to-background">
        <div className="container py-8">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <h1 className="text-2xl font-bold tracking-tight sm:text-3xl">
                Euro Scouts{" "}
                <span className="text-muted-foreground">Directory</span>
              </h1>
              <p className="mt-1 text-sm text-muted-foreground">
                Scouts e recrutamento dos principais clubes da Europa + MLS, com
                LinkedIn.
              </p>
            </div>
            <div className="flex gap-2">
              <Stat icon={<Users className="h-4 w-4" />} label="scouts" value={stats.total} />
              <Stat icon={<Building2 className="h-4 w-4" />} label="clubes" value={stats.clubs} />
              <Stat icon={<Trophy className="h-4 w-4" />} label="ligas" value={stats.leagues} />
            </div>
          </div>
        </div>
      </header>

      <main className="container py-6">
        {/* Toolbar */}
        <div className="sticky top-0 z-10 -mx-4 mb-5 border-b bg-background/95 px-4 py-3 backdrop-blur supports-[backdrop-filter]:bg-background/75">
          <div className="flex flex-col gap-3 lg:flex-row lg:items-center">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                value={q}
                onChange={(e) => setQ(e.target.value)}
                placeholder="Buscar nome, clube, cargo…"
                className="pl-9"
              />
            </div>

            <div className="flex flex-wrap items-center gap-3">
              <Select
                value={league}
                onValueChange={(v) => {
                  setLeague(v);
                  setClub(ALL);
                }}
              >
                <SelectTrigger className="w-[180px]">
                  <SelectValue placeholder="Liga" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value={ALL}>Todas as ligas</SelectItem>
                  {leagues.map((l) => (
                    <SelectItem key={l} value={l}>
                      {l}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>

              <Select value={club} onValueChange={setClub}>
                <SelectTrigger className="w-[180px]">
                  <SelectValue placeholder="Clube" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value={ALL}>Todos os clubes</SelectItem>
                  {clubs.map((c) => (
                    <SelectItem key={c} value={c}>
                      {c}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>

              <Tabs value={view} onValueChange={(v) => setView(v as View)}>
                <TabsList>
                  <TabsTrigger value="cards">
                    <LayoutGrid /> Cards
                  </TabsTrigger>
                  <TabsTrigger value="list">
                    <ListIcon /> Lista
                  </TabsTrigger>
                  <TabsTrigger value="table">
                    <TableIcon /> Tabela
                  </TabsTrigger>
                </TabsList>
              </Tabs>
            </div>
          </div>
        </div>

        {/* Count + top pagination */}
        <div className="mb-4 flex items-center justify-between text-sm text-muted-foreground">
          <span>
            {scouts === null
              ? "Carregando…"
              : `${filtered.length.toLocaleString("pt-BR")} de ${stats.total.toLocaleString("pt-BR")} scouts`}
          </span>
          <Pager page={curPage} totalPages={totalPages} setPage={setPage} />
        </div>

        {/* Views */}
        {scouts === null ? (
          <div className="py-24 text-center text-muted-foreground">Carregando dados…</div>
        ) : pageItems.length === 0 ? (
          <div className="py-24 text-center text-muted-foreground">
            Nenhum scout encontrado com esses filtros.
          </div>
        ) : view === "cards" ? (
          <CardsView items={pageItems} />
        ) : view === "list" ? (
          <ListView items={pageItems} />
        ) : (
          <TableView
            items={pageItems}
            sortKey={sortKey}
            sortDir={sortDir}
            onSort={toggleSort}
          />
        )}

        {/* Bottom pagination */}
        <div className="mt-6 flex items-center justify-center">
          <Pager page={curPage} totalPages={totalPages} setPage={setPage} />
        </div>
      </main>

      <footer className="border-t py-8 text-center text-xs text-muted-foreground">
        Fontes: Apollo + Apify · TheSportsDB · Info profissional pública (nome,
        cargo, clube, LinkedIn).
      </footer>
    </div>
  );
}

function Stat({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode;
  label: string;
  value: number;
}) {
  return (
    <div className="flex items-center gap-2 rounded-lg border bg-card px-3 py-2 shadow-sm">
      <span className="text-muted-foreground">{icon}</span>
      <div className="leading-none">
        <div className="text-base font-semibold">
          {value.toLocaleString("pt-BR")}
        </div>
        <div className="text-[11px] text-muted-foreground">{label}</div>
      </div>
    </div>
  );
}

function LinkedinBtn({ url, full = false }: { url: string; full?: boolean }) {
  if (!url)
    return (
      <span className="text-xs text-muted-foreground">—</span>
    );
  return (
    <Button
      asChild
      size={full ? "sm" : "icon"}
      variant={full ? "default" : "ghost"}
      className={full ? "w-full bg-[#0a66c2] hover:bg-[#0a66c2]/90" : "h-8 w-8"}
    >
      <a href={url} target="_blank" rel="noopener noreferrer" title="Ver LinkedIn">
        <Linkedin />
        {full && "Ver LinkedIn"}
      </a>
    </Button>
  );
}

function ScoutAvatar({ s, size = "h-12 w-12" }: { s: Scout; size?: string }) {
  return (
    <Avatar className={size}>
      <AvatarImage src={s.image || undefined} alt={s.name} loading="lazy" />
      <AvatarFallback>{initials(s.name)}</AvatarFallback>
    </Avatar>
  );
}

function CardsView({ items }: { items: Scout[] }) {
  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
      {items.map((s, i) => (
        <Card key={s.linkedin || `${s.name}-${i}`} className="flex flex-col">
          <CardContent className="flex flex-1 flex-col gap-3 p-4">
            <div className="flex items-center gap-3">
              <ScoutAvatar s={s} />
              <div className="min-w-0">
                <div className="truncate font-semibold leading-tight">
                  {s.name}
                </div>
                <div className="truncate text-xs text-muted-foreground">
                  {s.title}
                </div>
              </div>
            </div>
            <div className="flex items-center gap-2 border-t pt-3">
              {s.badge ? (
                // eslint-disable-next-line @next/next/no-img-element
                <img src={s.badge} alt="" className="h-5 w-5 object-contain" loading="lazy" />
              ) : null}
              <div className="min-w-0">
                <div className="truncate text-sm">{s.club}</div>
                <LeagueBadge league={s.league} className="mt-0.5" />
              </div>
            </div>
            {loc(s) ? (
              <div className="flex items-center gap-1 text-xs text-muted-foreground">
                <MapPin className="h-3 w-3" /> {loc(s)}
              </div>
            ) : null}
            <div className="mt-auto pt-1">
              <LinkedinBtn url={s.linkedin} full />
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}

function ListView({ items }: { items: Scout[] }) {
  return (
    <div className="divide-y rounded-xl border bg-card shadow-sm">
      {items.map((s, i) => (
        <div
          key={s.linkedin || `${s.name}-${i}`}
          className="flex items-center gap-4 p-3 hover:bg-muted/40"
        >
          <ScoutAvatar s={s} size="h-10 w-10" />
          <div className="min-w-0 flex-1">
            <div className="truncate font-medium leading-tight">{s.name}</div>
            <div className="truncate text-xs text-muted-foreground">
              {s.title}
            </div>
          </div>
          <div className="hidden min-w-0 flex-1 items-center gap-2 sm:flex">
            {s.badge ? (
              // eslint-disable-next-line @next/next/no-img-element
              <img src={s.badge} alt="" className="h-5 w-5 object-contain" loading="lazy" />
            ) : null}
            <span className="truncate text-sm">{s.club}</span>
          </div>
          <div className="hidden w-36 shrink-0 md:block">
            <LeagueBadge league={s.league} />
          </div>
          <div className="hidden w-40 shrink-0 truncate text-xs text-muted-foreground lg:block">
            {loc(s)}
          </div>
          <LinkedinBtn url={s.linkedin} />
        </div>
      ))}
    </div>
  );
}

function SortHead({
  label,
  k,
  sortKey,
  sortDir,
  onSort,
  className,
}: {
  label: string;
  k: SortKey;
  sortKey: SortKey;
  sortDir: "asc" | "desc";
  onSort: (k: SortKey) => void;
  className?: string;
}) {
  return (
    <TableHead className={className}>
      <button
        onClick={() => onSort(k)}
        className="inline-flex items-center gap-1 hover:text-foreground"
      >
        {label}
        <ArrowUpDown
          className={cn(
            "h-3.5 w-3.5",
            sortKey === k ? "text-foreground" : "opacity-40"
          )}
        />
      </button>
    </TableHead>
  );
}

function TableView({
  items,
  sortKey,
  sortDir,
  onSort,
}: {
  items: Scout[];
  sortKey: SortKey;
  sortDir: "asc" | "desc";
  onSort: (k: SortKey) => void;
}) {
  return (
    <div className="rounded-xl border bg-card shadow-sm">
      <Table>
        <TableHeader>
          <TableRow className="hover:bg-transparent">
            <SortHead label="Nome" k="name" sortKey={sortKey} sortDir={sortDir} onSort={onSort} />
            <SortHead label="Cargo" k="title" sortKey={sortKey} sortDir={sortDir} onSort={onSort} className="hidden md:table-cell" />
            <SortHead label="Clube" k="club" sortKey={sortKey} sortDir={sortDir} onSort={onSort} />
            <SortHead label="Liga" k="league" sortKey={sortKey} sortDir={sortDir} onSort={onSort} className="hidden sm:table-cell" />
            <SortHead label="Local" k="location" sortKey={sortKey} sortDir={sortDir} onSort={onSort} className="hidden lg:table-cell" />
            <TableHead className="w-16 text-right">LinkedIn</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {items.map((s, i) => (
            <TableRow key={s.linkedin || `${s.name}-${i}`}>
              <TableCell>
                <div className="flex items-center gap-3">
                  <ScoutAvatar s={s} size="h-8 w-8" />
                  <span className="font-medium">{s.name}</span>
                </div>
              </TableCell>
              <TableCell className="hidden text-muted-foreground md:table-cell">
                {s.title}
              </TableCell>
              <TableCell>
                <div className="flex items-center gap-2">
                  {s.badge ? (
                    // eslint-disable-next-line @next/next/no-img-element
                    <img src={s.badge} alt="" className="h-4 w-4 object-contain" loading="lazy" />
                  ) : null}
                  <span>{s.club}</span>
                </div>
              </TableCell>
              <TableCell className="hidden sm:table-cell">
                <LeagueBadge league={s.league} />
              </TableCell>
              <TableCell className="hidden text-muted-foreground lg:table-cell">
                {loc(s)}
              </TableCell>
              <TableCell className="text-right">
                <LinkedinBtn url={s.linkedin} />
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}

function Pager({
  page,
  totalPages,
  setPage,
}: {
  page: number;
  totalPages: number;
  setPage: (n: number) => void;
}) {
  if (totalPages <= 1) return null;
  return (
    <div className="flex items-center gap-2">
      <Button
        variant="outline"
        size="icon"
        className="h-8 w-8"
        disabled={page <= 1}
        onClick={() => setPage(page - 1)}
      >
        <ChevronLeft />
      </Button>
      <span className="min-w-[5rem] text-center text-sm tabular-nums">
        {page} / {totalPages}
      </span>
      <Button
        variant="outline"
        size="icon"
        className="h-8 w-8"
        disabled={page >= totalPages}
        onClick={() => setPage(page + 1)}
      >
        <ChevronRight />
      </Button>
    </div>
  );
}
