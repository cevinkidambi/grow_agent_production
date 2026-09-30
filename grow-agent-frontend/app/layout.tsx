// app/layout.tsx
import "./globals.css";
import type { Metadata } from "next";
import Navbar from "./components/Navbar";

export const metadata: Metadata = {
  title: "Grow Agent – GetU Advisor",
  description:
    "Grow Agent membantu investor Indonesia menemukan Reksadana yang sesuai dengan profil risiko dan tujuan investasi mereka.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="id">
      <body>
        <div className="app-shell">
          <Navbar />

          <main className="main">{children}</main>

          <footer className="footer">
            <span>© {new Date().getFullYear()} PT. GET Kemajuan Bangsa.</span>
            <span className="footer-dot">•</span>
            <span className="footer-muted">
              Bukan rekomendasi resmi investasi.
            </span>
          </footer>
        </div>
      </body>
    </html>
  );
}
