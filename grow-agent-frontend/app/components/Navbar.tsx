// app/components/Navbar.tsx
"use client";

import { useState } from "react";
import Link from "next/link";

export default function Navbar() {
    const [menuOpen, setMenuOpen] = useState(false);

    return (
        <header className="nav">
            <div className="nav-left">
                <Link href="/" className="nav-brand">
                    <span className="logo-pill">GA</span>
                    <span className="logo-text">GetU Advisor</span>
                </Link>
            </div>

            {/* Hamburger button for mobile */}
            <button
                className="nav-hamburger"
                onClick={() => setMenuOpen(!menuOpen)}
                aria-label="Toggle menu"
                aria-expanded={menuOpen}
            >
                <span className={`hamburger-line ${menuOpen ? "open" : ""}`}></span>
                <span className={`hamburger-line ${menuOpen ? "open" : ""}`}></span>
                <span className={`hamburger-line ${menuOpen ? "open" : ""}`}></span>
            </button>

            <nav className={`nav-links ${menuOpen ? "nav-links-open" : ""}`}>
                <Link href="/" onClick={() => setMenuOpen(false)}>Beranda</Link>
                <Link href="/risk-profile" onClick={() => setMenuOpen(false)}>Profil Risiko</Link>
                <Link href="/dashboard" onClick={() => setMenuOpen(false)}>Dashboard</Link>
                <Link href="/advisor" onClick={() => setMenuOpen(false)}>Grow Agent</Link>
            </nav>

            <div className="nav-right">
                <Link href="/risk-profile" className="btn-primary btn-small">
                    Mulai Sekarang
                </Link>
            </div>
        </header>
    );
}
