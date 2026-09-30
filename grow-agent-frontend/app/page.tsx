// app/page.tsx
"use client";

import Link from "next/link";

const features = [
  {
    title: "Profil Risiko Otomatis",
    body: "Jawab beberapa pertanyaan sederhana, lalu Grow Agent mengelompokkan Anda ke profil Konservatif, Moderat, Berimbang, atau Agresif.",
  },
  {
    title: "Rekomendasi Berbasis Data",
    body: "Daftar Reksadana dipilih dari model AI yang mempertimbangkan return, risiko, value added, dan faktor lainnya.",
  },
  {
    title: "Terhubung ke Channel Partner",
    body: "Investasi di channel favorit Anda: Bibit, Bareksa, atau bank rekanan – Grow Agent hanya menjadi advisor netral.",
  },
  {
    title: "AI Agent Dibekali Pengetahuan Investasi dan Model Machine Learning",
    body: "Tanya apa saja: penjelasan risiko, perbandingan produk, sampai simulasi skenario sederhana – Grow Agent akan menjawab dengan bahasa yang mudah dipahami.",
  },
];

const steps = [
  "Isi profil risiko Anda (±1 menit).",
  "Lihat dashboard rekomendasi Reksadana sesuai profil.",
  "Diskusi dengan Grow Agent Advisor bila masih ragu.",
  "Klik channel partner untuk melanjutkan transaksi.",
];

export default function LandingPage() {
  return (
    <div className="page-wrap">
      {/* HERO */}
      <section className="hero">
        <div className="hero-main">
          <div className="hero-pill">Powered by GetU-rkQuant-1.0, our proprietary ML model</div>
          <h1 className="hero-title">
            Rekomendasi Reksadana
            <br />
            <span className="hero-gradient">berbasis Model Machine Learning.</span>
          </h1>
          <p className="hero-subtitle">
            Grow Agent membantu Anda menyusun shortlist Reksadana berdasarkan Model Machine Learning
            kami, sebelum bertransaksi di Bibit, Bareksa, atau bank rekanan.
          </p>

          <div className="hero-actions">
            <Link href="/risk-profile" className="btn-primary">
              Mulai Isi Profil Risiko
            </Link>
            <Link href="/advisor" className="btn-secondary">
              Tanya Grow Agent
            </Link>
          </div>

          <div className="hero-login-row">
            <span className="hero-login-label">Masuk lebih cepat:</span>
            <button
              className="btn-ghost"
              type="button"
              onClick={() => alert("Integrasi GetU.Pos SSO – coming soon")}
            >
              Login dengan GetU.Pos
            </button>
            <button
              className="btn-ghost"
              type="button"
              onClick={() => alert("Login Google – coming soon")}
            >
              Login dengan Google
            </button>
          </div>
        </div>

        <div className="hero-card">
          <div className="hero-card-header">
            <span className="badge-soft">Preview Dashboard</span>
            <h3>Contoh rekomendasi</h3>
            <p>Untuk profil Berimbang dengan horizon 3–5 tahun.</p>
          </div>
          <div className="hero-card-body">
            <div className="hero-chip-row">
              <span className="chip chip-green">PU · Cash Management</span>
              <span className="chip">PT · Obligasi</span>
              <span className="chip">CP · Campuran</span>
            </div>
            <div className="fund-row">
              <div>
                <div className="fund-name">Fund A Berimbang</div>
                <div className="fund-meta">Score AI · 92 / 100</div>
              </div>
              <div className="fund-badge">Top 1%</div>
            </div>
            <div className="fund-row">
              <div>
                <div className="fund-name">Fund B Pendapatan Tetap</div>
                <div className="fund-meta">Score AI · 88 / 100</div>
              </div>
              <div className="fund-badge fund-badge-muted">Top 5%</div>
            </div>
            <p className="hero-card-footnote">
              *Angka di atas hanya ilustrasi. Data aktual akan ditarik dari
              model & database Anda.
            </p>
          </div>
        </div>
      </section>

      {/* FEATURES */}
      <section className="section">
        <h2 className="section-title">Kenapa Grow Agent?</h2>
        <div className="cards-grid">
          {features.map((f) => (
            <article key={f.title} className="card">
              <h3 className="card-title">{f.title}</h3>
              <p className="card-body">{f.body}</p>
            </article>
          ))}
        </div>
      </section>

      {/* STEPS */}
      <section className="section">
        <h2 className="section-title">Alur Pengguna</h2>
        <ol className="steps-list">
          {steps.map((s, idx) => (
            <li key={idx} className="steps-item">
              <span className="steps-index">{idx + 1}</span>
              <span>{s}</span>
            </li>
          ))}
        </ol>
      </section>
    </div>
  );
}
