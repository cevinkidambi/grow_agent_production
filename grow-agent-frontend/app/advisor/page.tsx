// app/advisor/page.tsx
"use client";

import { FormEvent, useState } from "react";
import { callAgent } from "@/lib/api";
import { getSessionId } from "@/lib/session";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

type ChatMessage = {
  role: "user" | "agent";
  content: string;
};

export default function AdvisorPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: "agent",
      content:
        "Selamat datang! Saya **GetU Advisor**, asisten investasi Reksadana Anda. 👋\n\nTanyakan apa saja seputar:\n- Profil risiko investasi\n- Rekomendasi Reksadana\n- Analisis performa dana\n\n*Disclaimer: bukan rekomendasi resmi investasi.*",
    },
  ]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    const text = input.trim();
    if (!text || sending) return;

    // push user message
    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setInput("");
    setSending(true);

    // get reply as plain string
    const sessionId = getSessionId();
    const replyText = await callAgent(text, sessionId);

    setMessages((prev) => [
      ...prev,
      { role: "agent", content: replyText },
    ]);

    setSending(false);
  };

  return (
    <div className="page-wrap">
      <section className="section narrow">
        <h1 className="section-title">GetU Advisor</h1>
        <p className="section-subtitle">
          Tanya apa saja seputar Reksadana, profil risiko, atau rekomendasi
          yang muncul di Dashboard.
        </p>

        <div className="chat-card">
          <div className="chat-messages">
            {messages.map((m, idx) => (
              <div
                key={idx}
                className={
                  m.role === "user" ? "chat-bubble user" : "chat-bubble agent"
                }
              >
                {m.role === "agent" ? (
                  <ReactMarkdown 
                    remarkPlugins={[remarkGfm]}
                    components={{
                      // Style headings
                      h1: ({children}) => <h1 className="md-h1">{children}</h1>,
                      h2: ({children}) => <h2 className="md-h2">{children}</h2>,
                      h3: ({children}) => <h3 className="md-h3">{children}</h3>,
                      // Style lists
                      ul: ({children}) => <ul className="md-ul">{children}</ul>,
                      ol: ({children}) => <ol className="md-ol">{children}</ol>,
                      li: ({children}) => <li className="md-li">{children}</li>,
                      // Style tables
                      table: ({children}) => <table className="md-table">{children}</table>,
                      th: ({children}) => <th className="md-th">{children}</th>,
                      td: ({children}) => <td className="md-td">{children}</td>,
                      // Style code
                      code: ({children}) => <code className="md-code">{children}</code>,
                      // Style paragraphs
                      p: ({children}) => <p className="md-p">{children}</p>,
                      // Style bold and emphasis
                      strong: ({children}) => <strong className="md-strong">{children}</strong>,
                      em: ({children}) => <em className="md-em">{children}</em>,
                      // Style images
                      img: ({src, alt}) => <img src={src} alt={alt} className="md-img" />,
                      // Style links
                      a: ({href, children}) => <a href={href} className="md-link" target="_blank" rel="noopener noreferrer">{children}</a>,
                    }}
                  >
                    {m.content}
                  </ReactMarkdown>
                ) : (
                  m.content
                )}
              </div>
            ))}
            {sending && (
              <div className="chat-bubble agent loading">
                <span className="loading-dots">
                  GetU Advisor sedang berpikir
                  <span className="dot">.</span>
                  <span className="dot">.</span>
                  <span className="dot">.</span>
                </span>
              </div>
            )}
          </div>

          <form onSubmit={handleSubmit} className="chat-input-row">
            <input
              className="input chat-input"
              placeholder="Tanya GetU Advisor…"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={sending}
            />
            <button
              type="submit"
              className="btn-primary btn-small"
              disabled={sending}
            >
              {sending ? "Mengirim…" : "Kirim"}
            </button>
          </form>
        </div>
      </section>
    </div>
  );
}
