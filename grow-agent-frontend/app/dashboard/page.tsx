// app/dashboard/page.tsx
"use client";

import { useEffect, useState } from "react";
import {
  DashboardData,
  fetchDashboardData,
  FundTypeCode,
} from "@/lib/api";
import { getSessionId } from "@/lib/session";

const FUND_LABEL: Record<FundTypeCode, string> = {
  PU: "Pasar Uang",
  PT: "Pendapatan Tetap",
  CP: "Campuran",
  SH: "Saham",
};

export default function DashboardPage() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      try {
        const sessionId = getSessionId();
        const res = await fetchDashboardData(sessionId);
        setData(res);
      } catch (err: any) {
        console.error(err);
        setError(
          err?.message || "Gagal memuat dashboard. Coba beberapa saat lagi."
        );
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  if (loading) {
    return (
      <div className="page-wrap">
        <section className="section">
          <h1 className="section-title">Dashboard</h1>
          <p className="section-subtitle">Memuat rekomendasi...</p>
          <div className="skeleton skeleton-card" />
        </section>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="page-wrap">
        <section className="section">
          <h1 className="section-title">Dashboard</h1>
          <p className="section-subtitle error-text">
            {error ?? "Tidak ada data."}
          </p>
        </section>
      </div>
    );
  }

  const { riskProfile, allowedFundTypes, fundsByType, performance, partners } =
    data;

  return (
    <div className="page-wrap">
      {/* SUMMARY */}
      <section className="section">
        <h1 className="section-title">Dashboard</h1>
        <p className="section-subtitle">
          Rekomendasi Reksadana berdasarkan profil risiko dan preferensi Anda.
        </p>

        <div className="summary-grid">
          <div className="card summary-card">
            <h3 className="card-title">Profil Risiko</h3>
            <p className="summary-main">
              {riskProfile?.risk_level ?? "Belum diisi"}
            </p>
            <p className="summary-sub">
              Horizon: {riskProfile?.horizon ?? "-"} · Tujuan:{" "}
              {riskProfile?.goal ?? "-"}
            </p>
            <a href="/risk-profile" className="link-inline">
              Ubah profil risiko →
            </a>
          </div>

          <div className="card summary-card">
            <h3 className="card-title">Alokasi Kategori</h3>
            <div className="chips-wrap">
              {allowedFundTypes.map((t) => (
                <span key={t} className="chip chip-green">
                  {FUND_LABEL[t]}
                </span>
              ))}
            </div>
            <p className="summary-sub">
              Grow Agent hanya akan menampilkan rekomendasi dalam kategori
              di atas agar konsisten dengan profil risiko Anda.
            </p>
          </div>

          <div className="card summary-card">
            <h3 className="card-title">Alpha Top 10% vs Pasar</h3>
            <p className="summary-sub">
              Berdasarkan uji out-of-sample, model merekomendasikan Top 10% fund
              yang secara historis juga mengalahkan rata-rata pasar.
            </p>
            {performance && (
              <div className="alpha-grid">
                {Object.entries(performance.data).map(([mfType, rawAlpha]) => {
                  const alpha = (rawAlpha as number) * 100; // 0.16 -> 16%
                  return (
                    <div key={mfType} className="alpha-item">
                      <span className="alpha-label">{mfType}</span>
                      <span className="alpha-value">
                        {alpha > 0 ? "+" : ""}
                        {alpha.toFixed(2)}%
                      </span>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      </section>

      {/* FUNDS BY TYPE */}
      <section className="section">
        <h2 className="section-title">Rekomendasi Reksadana</h2>
        <p className="section-subtitle">
          Daftar di bawah ini merupakan shortlist Top 5 berdasarkan model AI
          GetU-rkQuant-1.0 untuk tiap kategori yang diizinkan sesuai profil risiko Anda.
        </p>

        <div className="funds-section">
          {allowedFundTypes.map((t) => {
            const funds = fundsByType[t] ?? [];
            return (
              <div key={t} className="fund-type-block">
                <div className="fund-type-header">
                  <h3>{FUND_LABEL[t]}</h3>
                  <span className="badge-soft">
                    {funds.length} rekomendasi
                  </span>
                </div>
                {funds.length === 0 ? (
                  <p className="muted">Belum ada data untuk kategori ini.</p>
                ) : (
                  <div className="fund-cards">
                    {funds.map((f) => (
                      <article key={f.mfName} className="fund-card">
                        <h4 className="fund-card-name">{f.mfName}</h4>
                        <p className="fund-card-meta">
                          Score AI: <strong>{f.score}</strong> · Rank{" "}
                          {f.rank}
                        </p>
                        <div className="fund-card-actions">
                          <a
                            href={`/advisor?fund=${encodeURIComponent(
                              f.mfName
                            )}`}
                            className="btn-ghost"
                          >
                            Tanya Advisor
                          </a>
                        </div>
                      </article>
                    ))}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </section>

      {/* PARTNERS */}
      <section className="section">
        <h2 className="section-title">Channel Partner</h2>
        <p className="section-subtitle">
          Pilih platform tempat Anda ingin bertransaksi. Grow Agent hanya
          memberikan edukasi & simulasi.
        </p>

        <div className="partner-grid">
          {partners.map((p) => (
            <article key={p.name} className="card partner-card">
              <h3 className="card-title">{p.name}</h3>
              <p className="partner-promo">{p.promo}</p>
              <p className="card-body">{p.benefits}</p>
              <a
                href={p.link}
                target="_blank"
                rel="noreferrer"
                className="btn-primary btn-small"
              >
                Invest via {p.name}
              </a>
            </article>
          ))}
        </div>
      </section>
    </div>
  );
}
