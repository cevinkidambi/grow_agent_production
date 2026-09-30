// app/risk-profile/page.tsx
"use client";

import { FormEvent, ChangeEvent, useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import {
  saveRiskProfile,
  RiskProfileAnswers,
  RiskProfilePayload,
} from "@/lib/api";
import { getSessionId } from "@/lib/session";

export default function RiskProfilePage() {
  const router = useRouter();
  const [form, setForm] = useState<RiskProfileAnswers>({
    name: "",
    risk_level: "Berimbang",
    horizon: "3-5 tahun",
    goal: "Pertumbuhan modal",
  });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleChange = (
    e: ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setForm((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (saving) return;

    setSaving(true);
    setError(null);

    try {
      const sessionId = getSessionId();
      const payload: RiskProfilePayload = {
        sessionId: sessionId,
        answers: form,
      };

      await saveRiskProfile(payload);
      router.push("/dashboard");
    } catch (err: any) {
      console.error(err);
      setError(
        err?.message ??
        "Gagal menyimpan profil risiko. Coba beberapa saat lagi."
      );
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="page-wrap">
      <section className="section narrow">
        <h1 className="section-title">Profil Risiko</h1>
        <p className="section-subtitle">
          Jawab beberapa pertanyaan agar Grow Agent dapat memberikan shortlist
          Reksadana yang sesuai dengan profil risiko Anda.
        </p>

        <form onSubmit={handleSubmit} className="card form-card">
          <div className="form-row">
            <label className="label">
              Nama (opsional)
              <input
                className="input"
                name="name"
                value={form.name ?? ""}
                onChange={handleChange}
                placeholder="Nama Anda"
              />
            </label>
          </div>

          <div className="form-row">
            <label className="label">
              Profil Risiko
              <select
                className="input"
                name="risk_level"
                value={form.risk_level ?? "Berimbang"}
                onChange={handleChange}
              >
                <option value="Konservatif">Konservatif</option>
                <option value="Moderat">Moderat</option>
                <option value="Berimbang">Berimbang</option>
                <option value="Agresif">Agresif</option>
              </select>
            </label>
          </div>

          <div className="form-row">
            <label className="label">
              Horizon Investasi
              <select
                className="input"
                name="horizon"
                value={form.horizon ?? "3-5 tahun"}
                onChange={handleChange}
              >
                <option value="&lt; 1 tahun">&lt; 1 tahun</option>
                <option value="1-3 tahun">1-3 tahun</option>
                <option value="3-5 tahun">3-5 tahun</option>
                <option value="&gt; 5 tahun">&gt; 5 tahun</option>
              </select>
            </label>
          </div>

          <div className="form-row">
            <label className="label">
              Tujuan Investasi
              <select
                className="input"
                name="goal"
                value={form.goal ?? "Pertumbuhan modal"}
                onChange={handleChange}
              >
                <option value="Pertumbuhan modal">Pertumbuhan modal</option>
                <option value="Pendapatan pasif">Pendapatan pasif</option>
                <option value="Dana pendidikan">Dana pendidikan</option>
                <option value="Dana pensiun">Dana pensiun</option>
              </select>
            </label>
          </div>

          {error && <p className="error-text mt-2">{error}</p>}

          <div className="form-actions">
            <button
              type="submit"
              className="btn-primary"
              disabled={saving}
            >
              {saving ? "Menyimpan..." : "Lanjut ke Dashboard"}
            </button>
          </div>
        </form>
      </section>
    </div>
  );
}
