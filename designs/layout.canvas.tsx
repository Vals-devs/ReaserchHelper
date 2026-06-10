import { useState } from "react";

// Color tokens
const T = {
  bg: "#F8F9FA",
  surface: "#FFFFFF",
  border: "#E8EAED",
  borderSoft: "#F1F3F4",
  text: "#1A1A2E",
  textSub: "#5F6368",
  textMuted: "#9AA0A6",
  primary: "#1A73E8",
  primarySoft: "#E8F0FE",
  primaryHover: "#1557B0",
  success: "#0D904F",
  successSoft: "#E6F4EA",
  warning: "#E37400",
  warningSoft: "#FEF7E0",
  danger: "#D93025",
  dangerSoft: "#FCE8E6",
  purple: "#7B1FA2",
  purpleSoft: "#F3E5F5",
};

// Icon components
const Icon = {
  search: (
    <svg width="18" height="18" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" viewBox="0 0 24 24">
      <circle cx="10.5" cy="10.5" r="7.5" /><path d="M21 21l-5.2-5.2" />
    </svg>
  ),
  papers: (
    <svg width="18" height="18" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" viewBox="0 0 24 24">
      <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" /><polyline points="14 2 14 8 20 8" />
    </svg>
  ),
  folder: (
    <svg width="18" height="18" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" viewBox="0 0 24 24">
      <path d="M22 19a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2h5l2 3h9a2 2 0 012 2z" />
    </svg>
  ),
  clock: (
    <svg width="18" height="18" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" viewBox="0 0 24 24">
      <circle cx="12" cy="12" r="10" /><polyline points="12 6 12 12 16 14" />
    </svg>
  ),
  bulb: (
    <svg width="18" height="18" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" viewBox="0 0 24 24">
      <path d="M9 18h6M10 22h4M12 2a7 7 0 00-4 12.7V17h8v-2.3A7 7 0 0012 2z" />
    </svg>
  ),
  book: (
    <svg width="18" height="18" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" viewBox="0 0 24 24">
      <path d="M4 19.5A2.5 2.5 0 016.5 17H20" /><path d="M6.5 2H20v20H6.5A2.5 2.5 0 014 19.5v-15A2.5 2.5 0 016.5 2z" />
    </svg>
  ),
  gear: (
    <svg width="17" height="17" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" viewBox="0 0 24 24">
      <circle cx="12" cy="12" r="3" />
      <path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 01-2.83 2.83l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83-2.83l.06-.06A1.65 1.65 0 004.68 15a1.65 1.65 0 00-1.51-1H3a2 2 0 010-4h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 012.83-2.83l.06.06A1.65 1.65 0 009 4.68a1.65 1.65 0 001-1.51V3a2 2 0 014 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 2.83l-.06.06A1.65 1.65 0 0019.4 9a1.65 1.65 0 001.51 1H21a2 2 0 010 4h-.09a1.65 1.65 0 00-1.51 1z" />
    </svg>
  ),
  logout: (
    <svg width="17" height="17" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" viewBox="0 0 24 24">
      <path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4" /><polyline points="16 17 21 12 16 7" /><line x1="21" y1="12" x2="9" y2="12" />
    </svg>
  ),
  bell: (
    <svg width="18" height="18" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" viewBox="0 0 24 24">
      <path d="M18 8A6 6 0 006 8c0 7-3 9-3 9h18s-3-2-3-9" /><path d="M13.73 21a2 2 0 01-3.46 0" />
    </svg>
  ),
  plus: (
    <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" viewBox="0 0 24 24">
      <line x1="12" y1="5" x2="12" y2="19" /><line x1="5" y1="12" x2="19" y2="12" />
    </svg>
  ),
  chevron: (
    <svg width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" viewBox="0 0 24 24">
      <polyline points="9 18 15 12 9 6" />
    </svg>
  ),
  sparkle: (
    <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" viewBox="0 0 24 24">
      <path d="M12 2l2.4 7.2L22 12l-7.6 2.8L12 22l-2.4-7.2L2 12l7.6-2.8z" />
    </svg>
  ),
  trending: (
    <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" viewBox="0 0 24 24">
      <polyline points="23 6 13.5 15.5 8.5 10.5 1 18" /><polyline points="17 6 23 6 23 12" />
    </svg>
  ),
};

// Menu config
const mainNav = [
  { id: "search", label: "Search Papers", icon: Icon.search, badge: null },
  { id: "collections", label: "Collections", icon: Icon.folder, badge: "12" },
  { id: "history", label: "Search History", icon: Icon.clock, badge: null },
  { id: "gap", label: "Gap Analysis", icon: Icon.bulb, badge: "New" },
  { id: "biblio", label: "Bibliography", icon: Icon.book, badge: null },
];

const bottomNav = [
  { id: "settings", label: "Settings", icon: Icon.gear },
  { id: "logout", label: "Log Out", icon: Icon.logout },
];

// Sidebar Component
function Sidebar({ active, onNav }: { active: string; onNav: (id: string) => void }) {
  return (
    <aside style={{
      width: 252, minWidth: 252, height: "100vh", background: T.surface,
      borderRight: `1px solid ${T.border}`, display: "flex", flexDirection: "column",
      position: "fixed", left: 0, top: 0, zIndex: 20,
    }}>
      {/* Brand */}
      <div style={{ padding: "22px 20px 24px", display: "flex", alignItems: "center", gap: 11 }}>
        <div style={{
          width: 34, height: 34, borderRadius: 10,
          background: `linear-gradient(135deg, ${T.primary}, #4285F4)`,
          display: "flex", alignItems: "center", justifyContent: "center",
          boxShadow: "0 2px 8px rgba(26,115,232,0.25)",
        }}>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="white">
            <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" opacity="0.9" />
            <polyline points="14 2 14 8 20 8" fill="none" stroke="white" strokeWidth="1.5" />
          </svg>
        </div>
        <div>
          <div style={{ fontSize: 15, fontWeight: 800, color: T.text, letterSpacing: "-0.4px" }}>
            ResearchFinder
          </div>
          <div style={{ fontSize: 10.5, color: T.textMuted, fontWeight: 500, marginTop: 1 }}>
            AI-Powered Research Tool
          </div>
        </div>
      </div>

      {/* New Search CTA */}
      <div style={{ padding: "0 12px", marginBottom: 8 }}>
        <button style={{
          width: "100%", display: "flex", alignItems: "center", justifyContent: "center",
          gap: 8, padding: "10px 0", borderRadius: 10, border: "none",
          background: T.primary, color: "white", fontSize: 13, fontWeight: 600,
          cursor: "pointer", boxShadow: "0 1px 4px rgba(26,115,232,0.2)",
        }}>
          {Icon.plus} New Search
        </button>
      </div>

      {/* Navigation */}
      <nav style={{ flex: 1, padding: "8px 10px", overflowY: "auto" }}>
        <div style={{
          fontSize: 10, fontWeight: 700, color: T.textMuted, textTransform: "uppercase",
          letterSpacing: "0.8px", padding: "8px 12px 6px",
        }}>
          Navigation
        </div>
        {mainNav.map((item) => {
          const isActive = active === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onNav(item.id)}
              style={{
                width: "100%", display: "flex", alignItems: "center", gap: 10,
                padding: "10px 12px", borderRadius: 10, border: "none",
                cursor: "pointer", fontSize: 13.5, marginBottom: 2,
                fontWeight: isActive ? 600 : 450,
                color: isActive ? T.primary : T.textSub,
                background: isActive ? T.primarySoft : "transparent",
                transition: "all 0.15s ease",
              }}
            >
              <span style={{
                display: "flex", opacity: isActive ? 1 : 0.55,
                color: isActive ? T.primary : T.textSub,
              }}>
                {item.icon}
              </span>
              <span style={{ flex: 1, textAlign: "left" }}>{item.label}</span>
              {item.badge && (
                <span style={{
                  fontSize: 10, fontWeight: 700, padding: "2px 7px", borderRadius: 20,
                  background: item.badge === "New" ? T.successSoft : T.borderSoft,
                  color: item.badge === "New" ? T.success : T.textMuted,
                }}>
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </nav>

      {/* Bottom section */}
      <div style={{ padding: "0 10px", borderTop: `1px solid ${T.borderSoft}`, paddingTop: 8 }}>
        {bottomNav.map((item) => (
          <button key={item.id} style={{
            width: "100%", display: "flex", alignItems: "center", gap: 10,
            padding: "9px 12px", borderRadius: 10, border: "none",
            cursor: "pointer", fontSize: 13, color: T.textMuted,
            background: "transparent", marginBottom: 2,
          }}>
            <span style={{ opacity: 0.5, display: "flex" }}>{item.icon}</span>
            {item.label}
          </button>
        ))}
      </div>

      {/* User Card */}
      <div style={{
        margin: "6px 12px 14px", padding: "12px 14px", borderRadius: 12,
        background: T.bg, border: `1px solid ${T.borderSoft}`,
        display: "flex", alignItems: "center", gap: 10,
      }}>
        <div style={{
          width: 34, height: 34, borderRadius: "50%",
          background: `linear-gradient(135deg, ${T.primary}, ${T.purple})`,
          display: "flex", alignItems: "center", justifyContent: "center",
          color: "white", fontSize: 12.5, fontWeight: 700, flexShrink: 0,
        }}>
          IP
        </div>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ fontSize: 13, fontWeight: 650, color: T.text }}>Ival Permana</div>
          <div style={{
            fontSize: 11, color: T.textMuted, overflow: "hidden",
            textOverflow: "ellipsis", whiteSpace: "nowrap",
          }}>
            ival@univ.ac.id
          </div>
        </div>
        <span style={{ color: T.textMuted, display: "flex", cursor: "pointer" }}>{Icon.chevron}</span>
      </div>
    </aside>
  );
}

// Top Bar Component
function TopBar() {
  return (
    <header style={{
      height: 58, background: T.surface, borderBottom: `1px solid ${T.border}`,
      display: "flex", alignItems: "center", justifyContent: "space-between",
      padding: "0 32px", position: "sticky", top: 0, zIndex: 10,
    }}>
      {/* Breadcrumb */}
      <div style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 13 }}>
        <span style={{ color: T.textMuted }}>Dashboard</span>
        <span style={{ color: T.border, fontWeight: 300 }}>/</span>
        <span style={{ fontWeight: 600, color: T.text }}>Overview</span>
      </div>

      {/* Right actions */}
      <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
        {/* Quick search */}
        <div style={{
          display: "flex", alignItems: "center", gap: 8,
          padding: "8px 14px", borderRadius: 10,
          border: `1px solid ${T.border}`, background: T.bg, width: 280,
        }}>
          <span style={{ color: T.textMuted, display: "flex" }}>{Icon.search}</span>
          <span style={{ fontSize: 13, color: T.textMuted, flex: 1 }}>Quick search papers...</span>
          <kbd style={{
            fontSize: 10, color: T.textMuted, background: T.surface,
            border: `1px solid ${T.border}`, borderRadius: 5,
            padding: "2px 6px", fontWeight: 600, fontFamily: "inherit",
          }}>
            Ctrl K
          </kbd>
        </div>

        {/* Notifications */}
        <button style={{
          width: 38, height: 38, borderRadius: 10,
          border: `1px solid ${T.border}`, background: T.surface,
          cursor: "pointer", display: "flex", alignItems: "center",
          justifyContent: "center", color: T.textSub, position: "relative",
        }}>
          {Icon.bell}
          <span style={{
            position: "absolute", top: 7, right: 7, width: 8, height: 8,
            borderRadius: "50%", background: T.danger,
            border: `2px solid ${T.surface}`,
          }} />
        </button>
      </div>
    </header>
  );
}

// Dashboard content
function Dashboard() {
  const stats = [
    { label: "Saved Papers", value: "47", change: "+5 this week", icon: Icon.papers, color: T.primary, bg: T.primarySoft },
    { label: "Collections", value: "12", change: "+2 this week", icon: Icon.folder, color: T.purple, bg: T.purpleSoft },
    { label: "AI Summaries", value: "23", change: "+3 this week", icon: Icon.sparkle, color: T.warning, bg: T.warningSoft },
  ];

  return (
    <div style={{ padding: "28px 32px" }}>
      {/* Welcome */}
      <div style={{ marginBottom: 28 }}>
        <h1 style={{ fontSize: 24, fontWeight: 800, color: T.text, margin: 0, letterSpacing: "-0.5px" }}>
          Selamat Datang, Ival!
        </h1>
        <p style={{ fontSize: 14, color: T.textSub, marginTop: 6, lineHeight: 1.5 }}>
          Temukan, pahami, dan kelola paper ilmiah dengan bantuan AI.
        </p>
      </div>

      {/* Stats cards */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 16, marginBottom: 28 }}>
        {stats.map((s) => (
          <div key={s.label} style={{
            background: T.surface, border: `1px solid ${T.border}`,
            borderRadius: 14, padding: "22px 24px",
          }}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 14 }}>
              <div style={{
                width: 40, height: 40, borderRadius: 12,
                background: s.bg, color: s.color,
                display: "flex", alignItems: "center", justifyContent: "center",
              }}>
                {s.icon}
              </div>
              <span style={{
                display: "flex", alignItems: "center", gap: 4,
                fontSize: 12, fontWeight: 600, color: T.success,
              }}>
                {Icon.trending} {s.change}
              </span>
            </div>
            <div style={{ fontSize: 30, fontWeight: 800, color: T.text, letterSpacing: "-1px" }}>
              {s.value}
            </div>
            <div style={{ fontSize: 13, color: T.textSub, marginTop: 2, fontWeight: 500 }}>
              {s.label}
            </div>
          </div>
        ))}
      </div>

      {/* Quick actions + Recent activity */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
        {/* Quick Actions */}
        <div style={{
          background: T.surface, border: `1px solid ${T.border}`,
          borderRadius: 14, padding: "22px 24px",
        }}>
          <h3 style={{ fontSize: 14, fontWeight: 700, color: T.text, margin: "0 0 16px" }}>
            Quick Actions
          </h3>
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {[
              { label: "Cari Paper Baru", desc: "Semantic Scholar + arXiv", color: T.primary },
              { label: "Generate AI Summary", desc: "Ringkasan bahasa Indonesia", color: T.warning },
              { label: "Analisis Research Gap", desc: "Temukan celah penelitian", color: T.purple },
              { label: "Export Bibliography", desc: "Format APA / IEEE / Chicago", color: T.success },
            ].map((a) => (
              <div key={a.label} style={{
                display: "flex", alignItems: "center", gap: 12,
                padding: "12px 14px", borderRadius: 10, background: T.bg,
                cursor: "pointer", border: `1px solid transparent`,
                transition: "border-color 0.15s",
              }}>
                <div style={{
                  width: 8, height: 8, borderRadius: "50%", background: a.color, flexShrink: 0,
                }} />
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: 13, fontWeight: 600, color: T.text }}>{a.label}</div>
                  <div style={{ fontSize: 11.5, color: T.textMuted, marginTop: 1 }}>{a.desc}</div>
                </div>
                <span style={{ color: T.textMuted, display: "flex" }}>{Icon.chevron}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Searches */}
        <div style={{
          background: T.surface, border: `1px solid ${T.border}`,
          borderRadius: 14, padding: "22px 24px",
        }}>
          <h3 style={{ fontSize: 14, fontWeight: 700, color: T.text, margin: "0 0 16px" }}>
            Recent Searches
          </h3>
          <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
            {[
              { q: "transformer neural network", n: 47, t: "2 jam lalu" },
              { q: "BERT fine-tuning Indonesian", n: 12, t: "5 jam lalu" },
              { q: "attention mechanism survey", n: 23, t: "Kemarin" },
              { q: "GAN image synthesis", n: 89, t: "2 hari lalu" },
            ].map((r) => (
              <div key={r.q} style={{
                display: "flex", alignItems: "center", gap: 12,
                padding: "10px 14px", borderRadius: 10, background: T.bg,
                cursor: "pointer",
              }}>
                <span style={{ color: T.textMuted, display: "flex", flexShrink: 0 }}>{Icon.search}</span>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{
                    fontSize: 13, fontWeight: 500, color: T.text,
                    overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap",
                  }}>
                    {r.q}
                  </div>
                </div>
                <span style={{ fontSize: 11, color: T.textMuted, whiteSpace: "nowrap" }}>{r.n} hasil</span>
                <span style={{ fontSize: 11, color: T.textMuted, whiteSpace: "nowrap" }}>{r.t}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

// Main export
export default function LayoutCanvas() {
  const [active, setActive] = useState("search");

  return (
    <div style={{
      fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
      background: T.bg, minHeight: "100vh", display: "flex",
    }}>
      <Sidebar active={active} onNav={setActive} />
      <div style={{ marginLeft: 252, flex: 1, minHeight: "100vh" }}>
        <TopBar />
        <Dashboard />
      </div>
    </div>
  );
}
