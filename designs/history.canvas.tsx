import { useState } from "react";

const C = {
  bg: "#FAFAFA", white: "#FFFFFF", border: "#E5E7EB", borderLight: "#F3F4F6",
  text: "#111827", sub: "#6B7280", muted: "#9CA3AF",
  accent: "#2563EB", accentLight: "#EFF6FF",
  green: "#059669", greenLight: "#ECFDF5",
  red: "#DC2626", redLight: "#FEF2F2",
  hover: "#F9FAFB",
};

const icons = {
  clock: <svg width="18" height="18" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>,
  search: <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>,
  redo: <svg width="14" height="14" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 11-2.12-9.36L23 10"/></svg>,
  trash: <svg width="14" height="14" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/></svg>,
  trashAll: <svg width="14" height="14" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24"><path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/><line x1="10" y1="11" x2="10" y2="17"/><line x1="14" y1="11" x2="14" y2="17"/></svg>,
  filter: <svg width="14" height="14" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24"><path d="M22 3H2l8 9.46V19l4 2v-8.54L22 3z"/></svg>,
  results: <svg width="14" height="14" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>,
};

const history = [
  { id: 1, query: "transformer neural network architecture", source: "Semantic Scholar + arXiv", results: 47, date: "10 Juni 2026, 14:32", filters: ["Computer Science", "2020-2026"] },
  { id: 2, query: "BERT fine-tuning Indonesian language", source: "Semantic Scholar", results: 12, date: "10 Juni 2026, 11:05", filters: ["NLP"] },
  { id: 3, query: "attention mechanism survey paper", source: "arXiv", results: 23, date: "9 Juni 2026, 20:15", filters: [] },
  { id: 4, query: "generative adversarial networks image synthesis", source: "Semantic Scholar + arXiv", results: 89, date: "8 Juni 2026, 16:44", filters: ["Computer Vision", "2018-2024"] },
  { id: 5, query: "reinforcement learning reward shaping", source: "Semantic Scholar", results: 15, date: "7 Juni 2026, 09:20", filters: ["Machine Learning"] },
  { id: 6, query: "systematic literature review methodology", source: "CrossRef", results: 34, date: "5 Juni 2026, 13:10", filters: [] },
  { id: 7, query: "self-supervised learning contrastive", source: "arXiv", results: 28, date: "3 Juni 2026, 18:55", filters: ["Deep Learning", "2021-2026"] },
];

function HistoryRow({ item, onDelete, onRerun }: { item: typeof history[0]; onDelete: () => void; onRerun: () => void }) {
  return (
    <div style={{
      background: C.white, border: `1px solid ${C.border}`, borderRadius: 12,
      padding: "16px 20px", display: "flex", alignItems: "center", gap: 16,
      transition: "border-color 0.15s",
    }}>
      {/* Icon */}
      <div style={{
        width: 38, height: 38, borderRadius: 10, background: C.hover,
        display: "flex", alignItems: "center", justifyContent: "center",
        color: C.muted, flexShrink: 0,
      }}>
        {icons.search}
      </div>

      {/* Content */}
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4 }}>
          <span style={{ fontSize: 14, fontWeight: 600, color: C.text }}>
            "{item.query}"
          </span>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 10, fontSize: 12, color: C.muted }}>
          <span style={{ display: "flex", alignItems: "center", gap: 4 }}>{icons.results} {item.results} hasil</span>
          <span>·</span>
          <span>{item.source}</span>
          <span>·</span>
          <span>{item.date}</span>
        </div>
        {item.filters.length > 0 && (
          <div style={{ display: "flex", gap: 6, marginTop: 8 }}>
            {item.filters.map((f) => (
              <span key={f} style={{
                fontSize: 10.5, fontWeight: 500, padding: "2px 8px", borderRadius: 6,
                background: C.accentLight, color: C.accent,
              }}>
                {f}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Actions */}
      <div style={{ display: "flex", gap: 6, flexShrink: 0 }}>
        <button
          onClick={onRerun}
          style={{
            display: "flex", alignItems: "center", gap: 5, padding: "7px 14px", borderRadius: 8,
            border: "none", background: C.accentLight, fontSize: 12,
            color: C.accent, cursor: "pointer", fontWeight: 600,
          }}
        >
          {icons.redo} Cari Lagi
        </button>
        <button
          onClick={onDelete}
          style={{
            display: "flex", alignItems: "center", gap: 5, padding: "7px 12px", borderRadius: 8,
            border: `1px solid ${C.border}`, background: C.white, fontSize: 12,
            color: C.sub, cursor: "pointer",
          }}
        >
          {icons.trash}
        </button>
      </div>
    </div>
  );
}

export default function HistoryDesign() {
  const [items, setItems] = useState(history);
  const [searchFilter, setSearchFilter] = useState("");

  const filtered = items.filter((h) =>
    h.query.toLowerCase().includes(searchFilter.toLowerCase())
  );

  const deleteItem = (id: number) => setItems(items.filter((h) => h.id !== id));

  return (
    <div style={{ fontFamily: "'Inter', -apple-system, sans-serif", background: C.bg, minHeight: "100vh", display: "flex" }}>
      {/* Sidebar placeholder */}
      <div style={{ width: 240, borderRight: `1px solid ${C.border}`, background: C.white, padding: 20, position: "fixed", height: "100vh" }}>
        <div style={{ fontSize: 15, fontWeight: 700, color: C.text }}>ResearchFinder</div>
        <div style={{ marginTop: 24, fontSize: 13, color: C.sub }}>Search Papers</div>
        <div style={{ marginTop: 8, fontSize: 13, color: C.sub }}>Collections</div>
        <div style={{ marginTop: 8, fontSize: 13, color: C.accent, fontWeight: 600 }}>🕐 History</div>
      </div>

      <div style={{ marginLeft: 240, flex: 1, padding: "28px 40px", maxWidth: 900 }}>
        {/* Header */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24 }}>
          <div>
            <h1 style={{ fontSize: 22, fontWeight: 700, color: C.text, margin: 0 }}>Riwayat Pencarian</h1>
            <p style={{ fontSize: 13, color: C.sub, marginTop: 4 }}>
              {items.length} pencarian tersimpan
            </p>
          </div>
          <button
            onClick={() => setItems([])}
            style={{
              display: "flex", alignItems: "center", gap: 6, padding: "8px 16px", borderRadius: 10,
              border: `1px solid ${C.red}30`, background: C.redLight, fontSize: 13,
              color: C.red, cursor: "pointer", fontWeight: 500,
            }}
          >
            {icons.trashAll} Hapus Semua
          </button>
        </div>

        {/* Filter search */}
        <div style={{
          display: "flex", alignItems: "center", gap: 8, background: C.white,
          border: `1px solid ${C.border}`, borderRadius: 10, padding: "9px 14px", marginBottom: 20,
        }}>
          <span style={{ color: C.muted, display: "flex" }}>{icons.search}</span>
          <input
            value={searchFilter}
            onChange={(e) => setSearchFilter(e.target.value)}
            placeholder="Filter riwayat pencarian..."
            style={{
              flex: 1, border: "none", outline: "none", fontSize: 13,
              color: C.text, background: "transparent",
            }}
          />
          {searchFilter && (
            <button onClick={() => setSearchFilter("")} style={{
              border: "none", background: "transparent", cursor: "pointer", color: C.muted, fontSize: 12,
            }}>
              ✕
            </button>
          )}
        </div>

        {/* Grouped by date */}
        {filtered.length > 0 ? (
          <div>
            <div style={{ fontSize: 11, fontWeight: 600, color: C.muted, textTransform: "uppercase", letterSpacing: "0.5px", marginBottom: 12 }}>
              Terbaru
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
              {filtered.map((item) => (
                <HistoryRow
                  key={item.id}
                  item={item}
                  onDelete={() => deleteItem(item.id)}
                  onRerun={() => {}}
                />
              ))}
            </div>
          </div>
        ) : (
          <div style={{
            textAlign: "center", padding: 60, marginTop: 40,
            background: C.white, border: `1px solid ${C.border}`, borderRadius: 16,
          }}>
            <div style={{ fontSize: 40 }}>🕐</div>
            <h3 style={{ fontSize: 16, fontWeight: 600, color: C.text, marginTop: 12 }}>
              Belum ada riwayat pencarian
            </h3>
            <p style={{ fontSize: 13, color: C.sub, marginTop: 6 }}>
              Mulai cari paper ilmiah dan riwayatmu akan muncul di sini.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
