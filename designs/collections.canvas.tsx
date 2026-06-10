import { useState } from "react";

const C = {
  bg: "#FAFAFA", white: "#FFFFFF", border: "#E5E7EB", borderLight: "#F3F4F6",
  text: "#111827", sub: "#6B7280", muted: "#9CA3AF",
  accent: "#2563EB", accentLight: "#EFF6FF",
  green: "#059669", greenLight: "#ECFDF5",
  orange: "#D97706", orangeLight: "#FFFBEB",
  purple: "#7C3AED", purpleLight: "#F5F3FF",
  hover: "#F9FAFB",
};

const icons = {
  folder: <svg width="20" height="20" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24"><path d="M22 19a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2h5l2 3h9a2 2 0 012 2z"/></svg>,
  plus: <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>,
  paper: <svg width="15" height="15" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>,
  note: <svg width="15" height="15" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24"><path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>,
  export: <svg width="15" height="15" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>,
  trash: <svg width="14" height="14" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/></svg>,
  dots: <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24"><circle cx="12" cy="12" r="1"/><circle cx="12" cy="5" r="1"/><circle cx="12" cy="19" r="1"/></svg>,
  grid: <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>,
  list: <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24"><line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/></svg>,
  back: <svg width="18" height="18" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24"><path d="M19 12H5m7-7l-7 7 7 7"/></svg>,
  sparkle: <svg width="14" height="14" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24"><path d="M12 3v1m0 16v1m-8-9H3m18 0h-1M12 8a4 4 0 100 8 4 4 0 000-8z"/></svg>,
  highlight: <svg width="14" height="14" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24"><path d="M12 20h9M16.5 3.5a2.121 2.121 0 013 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>,
};

const collections = [
  { id: 1, name: "Skripsi - Deep Learning NLP", desc: "Paper-paper untuk bab 2 skripsi tentang transformer dan NLP", papers: 14, updated: "2 hari lalu", color: C.accent },
  { id: 2, name: "Computer Vision Survey", desc: "Kumpulan paper CNN, ViT, dan object detection", papers: 8, updated: "1 minggu lalu", color: C.purple },
  { id: 3, name: "Reinforcement Learning", desc: "Paper dasar RL dan deep RL untuk referensi", papers: 6, updated: "3 minggu lalu", color: C.green },
  { id: 4, name: "Research Methods", desc: "Paper tentang metodologi penelitian dan systematic review", papers: 5, updated: "1 bulan lalu", color: C.orange },
];

const detailPapers = [
  { title: "Attention Is All You Need", authors: "Vaswani et al.", year: 2017, notes: "Paper utama untuk bab 2. Arsitektur Transformer jadi fondasi semua model modern.", hasHighlight: true },
  { title: "BERT: Pre-training of Deep Bidirectional Transformers", authors: "Devlin et al.", year: 2018, notes: "Model pre-training pertama yang sukses untuk NLP. Penting untuk bagian related work.", hasHighlight: false },
  { title: "Language Models are Few-Shot Learners (GPT-3)", authors: "Brown et al.", year: 2020, notes: "", hasHighlight: true },
  { title: "T5: Exploring the Limits of Transfer Learning", authors: "Raffel et al.", year: 2019, notes: "Unified text-to-text framework, bagus untuk comparison.", hasHighlight: false },
];

function CollectionCard({ col, onClick }: { col: typeof collections[0]; onClick: () => void }) {
  return (
    <div
      onClick={onClick}
      style={{
        background: C.white, border: `1px solid ${C.border}`, borderRadius: 14,
        padding: "22px 24px", cursor: "pointer", transition: "border-color 0.15s, box-shadow 0.15s",
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div style={{
          width: 40, height: 40, borderRadius: 10, display: "flex", alignItems: "center", justifyContent: "center",
          background: `${col.color}12`, color: col.color,
        }}>
          {icons.folder}
        </div>
        <button style={{ border: "none", background: "transparent", cursor: "pointer", color: C.muted, padding: 0 }}>
          {icons.dots}
        </button>
      </div>
      <h3 style={{ fontSize: 14, fontWeight: 700, color: C.text, margin: "14px 0 6px", lineHeight: 1.3 }}>
        {col.name}
      </h3>
      <p style={{ fontSize: 12.5, color: C.sub, lineHeight: 1.5, margin: 0, minHeight: 36 }}>
        {col.desc}
      </p>
      <div style={{
        display: "flex", alignItems: "center", gap: 12, marginTop: 16, paddingTop: 14,
        borderTop: `1px solid ${C.borderLight}`, fontSize: 12, color: C.muted,
      }}>
        <span style={{ display: "flex", alignItems: "center", gap: 4 }}>{icons.paper} {col.papers} paper</span>
        <span>·</span>
        <span>{col.updated}</span>
      </div>
    </div>
  );
}

function CollectionsList() {
  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24 }}>
        <div>
          <h1 style={{ fontSize: 22, fontWeight: 700, color: C.text, margin: 0 }}>Collections</h1>
          <p style={{ fontSize: 13, color: C.sub, marginTop: 4 }}>Kelola koleksi paper ilmiah kamu</p>
        </div>
        <div style={{ display: "flex", gap: 8 }}>
          <div style={{ display: "flex", border: `1px solid ${C.border}`, borderRadius: 8, overflow: "hidden" }}>
            <button style={{ padding: "7px 10px", border: "none", background: C.accentLight, color: C.accent, cursor: "pointer" }}>{icons.grid}</button>
            <button style={{ padding: "7px 10px", border: "none", background: C.white, color: C.muted, cursor: "pointer" }}>{icons.list}</button>
          </div>
          <button style={{
            display: "flex", alignItems: "center", gap: 6, padding: "8px 16px", borderRadius: 10,
            border: "none", background: C.accent, color: "white", fontSize: 13, fontWeight: 600, cursor: "pointer",
          }}>
            {icons.plus} Koleksi Baru
          </button>
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 16 }}>
        {collections.map((col) => (
          <CollectionCard key={col.id} col={col} onClick={() => {}} />
        ))}

        {/* Add new card */}
        <div style={{
          border: `2px dashed ${C.border}`, borderRadius: 14, padding: "22px 24px",
          display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center",
          minHeight: 180, cursor: "pointer", gap: 8,
        }}>
          <div style={{ width: 40, height: 40, borderRadius: 10, background: C.hover, display: "flex", alignItems: "center", justifyContent: "center", color: C.muted }}>
            {icons.plus}
          </div>
          <span style={{ fontSize: 13, fontWeight: 500, color: C.muted }}>Buat Koleksi Baru</span>
        </div>
      </div>
    </div>
  );
}

function CollectionDetail({ onBack }: { onBack: () => void }) {
  return (
    <div>
      <button onClick={onBack} style={{
        display: "flex", alignItems: "center", gap: 6, border: "none", background: "transparent",
        fontSize: 13, color: C.sub, cursor: "pointer", marginBottom: 20, padding: 0,
      }}>
        {icons.back} Semua Collections
      </button>

      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 24 }}>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 6 }}>
            <div style={{ width: 36, height: 36, borderRadius: 10, background: `${C.accent}12`, color: C.accent, display: "flex", alignItems: "center", justifyContent: "center" }}>
              {icons.folder}
            </div>
            <h1 style={{ fontSize: 20, fontWeight: 700, color: C.text, margin: 0 }}>Skripsi - Deep Learning NLP</h1>
          </div>
          <p style={{ fontSize: 13, color: C.sub, margin: "6px 0 0 46px" }}>
            Paper-paper untuk bab 2 skripsi tentang transformer dan NLP · 14 paper
          </p>
        </div>
        <div style={{ display: "flex", gap: 8 }}>
          <button style={{
            display: "flex", alignItems: "center", gap: 6, padding: "8px 16px", borderRadius: 10,
            border: `1px solid ${C.border}`, background: C.white, fontSize: 13, color: C.sub, cursor: "pointer", fontWeight: 500,
          }}>
            {icons.sparkle} Gap Analysis
          </button>
          <button style={{
            display: "flex", alignItems: "center", gap: 6, padding: "8px 16px", borderRadius: 10,
            border: "none", background: C.accent, color: "white", fontSize: 13, fontWeight: 600, cursor: "pointer",
          }}>
            {icons.export} Export Bibliography
          </button>
        </div>
      </div>

      {/* Papers list */}
      <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
        {detailPapers.map((p, i) => (
          <div key={i} style={{
            background: C.white, border: `1px solid ${C.border}`, borderRadius: 12,
            padding: "18px 22px",
          }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
              <div style={{ flex: 1 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4 }}>
                  <span style={{ fontSize: 11, color: C.muted }}>{p.year}</span>
                  {p.hasHighlight && (
                    <span style={{ fontSize: 10, fontWeight: 600, padding: "2px 8px", borderRadius: 20, background: C.orangeLight, color: C.orange }}>
                      Has highlight
                    </span>
                  )}
                </div>
                <h3 style={{ fontSize: 14, fontWeight: 600, color: C.text, margin: 0 }}>{p.title}</h3>
                <div style={{ fontSize: 12.5, color: C.sub, marginTop: 4 }}>{p.authors}</div>
              </div>
              <div style={{ display: "flex", gap: 6 }}>
                <button style={{ padding: "6px 12px", borderRadius: 8, border: `1px solid ${C.border}`, background: C.white, fontSize: 11.5, color: C.sub, cursor: "pointer", display: "flex", alignItems: "center", gap: 4 }}>
                  {icons.note} Catatan
                </button>
                <button style={{ padding: "6px 12px", borderRadius: 8, border: `1px solid ${C.border}`, background: C.white, fontSize: 11.5, color: C.sub, cursor: "pointer", display: "flex", alignItems: "center", gap: 4 }}>
                  {icons.highlight} Highlight
                </button>
                <button style={{ padding: "6px 10px", borderRadius: 8, border: `1px solid ${C.border}`, background: C.white, fontSize: 11.5, color: C.muted, cursor: "pointer", display: "flex" }}>
                  {icons.trash}
                </button>
              </div>
            </div>

            {p.notes && (
              <div style={{
                marginTop: 12, padding: "10px 14px", borderRadius: 8, background: C.hover,
                borderLeft: `3px solid ${C.accent}`, fontSize: 12.5, color: C.sub, lineHeight: 1.5,
              }}>
                📝 {p.notes}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

export default function CollectionsDesign() {
  const [view, setView] = useState<"list" | "detail">("list");

  return (
    <div style={{ fontFamily: "'Inter', -apple-system, sans-serif", background: C.bg, minHeight: "100vh", display: "flex" }}>
      {/* Sidebar placeholder */}
      <div style={{ width: 240, borderRight: `1px solid ${C.border}`, background: C.white, padding: 20, position: "fixed", height: "100vh" }}>
        <div style={{ fontSize: 15, fontWeight: 700, color: C.text }}>ResearchFinder</div>
        <div style={{ marginTop: 24, fontSize: 13, color: C.sub }}>Search Papers</div>
        <div style={{ marginTop: 8, fontSize: 13, color: C.accent, fontWeight: 600 }}>📚 Collections</div>
        <div style={{ marginTop: 8, fontSize: 13, color: C.sub }}>History</div>
      </div>

      <div style={{ marginLeft: 240, flex: 1, padding: "28px 40px" }}>
        {view === "list" ? (
          <div>
            <CollectionsList />
            <div style={{ marginTop: 32, padding: 20, background: C.white, border: `1px solid ${C.border}`, borderRadius: 12, textAlign: "center" }}>
              <button onClick={() => setView("detail")} style={{
                padding: "9px 20px", borderRadius: 10, border: `1px solid ${C.border}`,
                background: C.hover, fontSize: 13, color: C.sub, cursor: "pointer",
              }}>
                Lihat Collection Detail →
              </button>
            </div>
          </div>
        ) : (
          <CollectionDetail onBack={() => setView("list")} />
        )}
      </div>
    </div>
  );
}
