import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Euro Scouts Directory",
  description:
    "Diretório de scouts e recrutamento dos principais clubes da Europa + MLS, com LinkedIn.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="pt-BR">
      <body className="min-h-screen bg-background font-sans text-foreground antialiased">
        {children}
      </body>
    </html>
  );
}
