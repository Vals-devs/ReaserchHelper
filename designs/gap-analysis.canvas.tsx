import { useState } from "react";

const C = {
  bg: "#FAFAFA", white: "#FFFFFF", border: "#E5E7EB", borderLight: "#F3F4F6",
  text: "#111827", sub: "#6B7280", muted: "#9CA3AF",
  accent: "#2563EB", accentLight: "#EFF6FF",
  green: "#059669", greenLight: "#ECFDF5",
  orange: "#D97706", orangeLight: "#FFFBEB",
  purple: "#7C3AED", purpleLight: "#F5F3FF",
  red: "#DC2626", redLight: "#FEF2F2",
  hover: "#F9FAFB",
};

const icons = {
  sparkle: <svg width="18" height="18" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24"><path d="M12 3v1m0 16v1m-8-9H3m18 0h-1m-2.636-6.364l-.707.707M6.343 17.657l-.707.707m0-12.728l.707.707m11.314 11.314l.707.707M12 8a4 4 0 100 8 4 4 0 000-8z"/></svg>,
  topic: <svg width="20" height="20" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24"><path d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/></svg>,
  method: <svg width="20" height="20" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24"><path d="M14.7 6.3a1 1 0 000 1.4l1.6 1.6a1 1 0 001.4 0l3.77-3.77a6 6 0 01-7.94 7.94l-6.91 6.91a2.12 2.12 0 01-3-3l6.91-6.91a6 6 0 017.94-7.94l-3.76 3.76z"/></svg>,
  gap: <svg width="20" height="20" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><path d="M12 8v4m0 4h.01"/></svg>,
  suggest: <svg width="20" height="20" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24"><path d="M5 12h14m-7-7l7 7-7 7"/></svg>,
  check: <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg>,
  paper: <svg width="15" height="15" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>,
  loader: <svg width="20" height="20" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24"><path d="M12 2v4m0 12v4m-7.07-3.93l2.83-2.83m8.48-8.48l2.83-2.83M2 12h4m12 0h4M4.93 4.93l2.83 2.83m8.48 8.48l2.83 2.83"/></svg>,
};

const allPapers = [
  { id: 1, title: "Attention Is All You Need", authors: "Vaswani et al.", year: 2017, selected: true },
  { id: 2, title: "BERT: Pre-training of Deep Bidirectional Transformers", authors: "Devlin et al.", year: 2018, selected: true },
  { id: 3, title: "Language Models are Few-Shot Learners (GPT-3)", authors: "Brown et al.", year: 2020, selected: true },
  { id: 4, title: "T5: Exploring the Limits of Transfer Learning", authors: "Raffel et al.", year: 2019, selected: false },
  { id: 5, title: "Generative Adversarial Networks", authors: "Goodfellow et al.", year: 2014, selected: false },
  { id: 6, title: "Deep Residual Learning for Image Recognition", authors: "He et al.", year: 2015, selected: true },
  { id: 7, title: "An Image is Worth 16x16 Words (ViT)", authors: "Dosovitskiy et al.", year: 2020, selected: true },
  { id: 8, title: "CLIP: Learning Transferable Visual Models", authors: "Radford et al.", year: 2021, selected: false },
];

const analysisResult = {
  topik: [
    { name: "Transformer Architecture", count: 5, desc: "Dominan di 5 dari 7 paper. Arsitektur ini menjadi fondasi model NLP dan vision modern." },
    { name: "Pre-training & Transfer Learning", count: 4, desc: "Strategi pre-training pada data besar lalu fine-tuning untuk tugas spesifik." },
    { name: "Self-Attention Mechanism", count: 3, desc: "Mekanisme inti yang memungkinkan pemrosesan paralel dan long-range dependencies." },
  ],
  metodologi: [
    { name: "Supervised Fine-tuning", freq: "Sering", desc: "Pre-train di data besar, fine-tune di data task-specific." },
    { name: "Large-scale Pre-training", freq: "Sering", desc: "Training pada corpus besar (web text, ImageNet) tanpa label." },
    { name: "Ablation Study", freq: "Sedang", desc: "Hampir semua paper menggunakan ablation untuk validasi desain." },
  ],
  gaps: [
    { title: "Efisiensi komputasi model besar", desc: "Sebagian besar paper fokus pada performa, belum banyak yang mengeksplorasi efisiensi inference dan training cost.", priority: "Tinggi" },
    { title: "Cross-modal transfer learning", desc: "Transfer knowledge antar modalitas (teks ↔ gambar ↔ audio) masih terbatas dieksplorasi.", priority: "Tinggi" },
    { title: "Low-resource language adaptation", desc: "Adaptasi model pre-training untuk bahasa dengan data terbatas, termasuk bahasa Indonesia.", priority: "Sedang" },
    { title: "Interpretability & explainability", desc: "Memahami keputusan model transformer secara mendalam masih area yang terbuka.", priority: "Sedang" },
  ],
  saran: [
    "Investigasi metode pruning/distillation untuk model transformer bahasa Indonesia",
    "Eksplorasi cross-modal learning untuk tugas multilingual + multimodal",
    "Pengembangan efficient attention mechanism untuk deployment di edge devices",
    "Studi komprehensif tentang interpretability pada model NLP bahasa Indonesia",
  ],
};

function PaperSelector() {
  const [papers, setPapers] = useState(allPapers);
  const selectedCount = papers.filter((p) => p.selected).length;

  const toggle = (id: number) => {
    setPapers(papers.map((p) => p.id === id ? { ...p, selected: !p.selected } : p));
  };

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
        <div>
          <h1 style={{ fontSize: 22, fontWeight: 700, color: C.text, margin: 0 }}>Research Gap Analysis</h1>
          <p style={{ fontSize: 13, color: C.sub, marginTop: 4 }}>
            Pilih 3–10 paper dari koleksi kamu untuk dianalisis celah penelitiannya
          </p>
        </div>
        <div style={{
          display: "flex", alignItems: "center", gap: 8, padding: "8px 16px", borderRadius: 10,
          background: selectedCount >= 3 ? C.accentLight : C.hover,
          border: `1px solid ${selectedCount >= 3 ? C.accent : C.border}`,
        }}>
          <span style={{ fontSize: 13, fontWeight: 600, color: selectedCount >= 3 ? C.accent : C.muted }}>
            {selectedCount} / 10 dipilih
          </span>
        </div>
      </div>

      {/* Progress bar */}
      <div style={{ height: 4, borderRadius: 4, background: C.borderLight, marginBottom: 24 }}>
        <div style={{
          height: "100%", borderRadius: 4,
          width: `${(selectedCount / 10) * 100}%`,
          background: selectedCount >= 3 ? C.accent : C.muted,
          transition: "width 0.3s, background 0.3s",
        }} />
      </div>

      {/* Paper grid */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10, marginBottom: 24 }}>
        {papers.map((p) => (
          <div
            key={p.id}
            onClick={() => toggle(p.id)}
            style={{
              display: "flex", alignItems: "center", gap: 12,
              padding: "14px 18px", borderRadius: 12,
              border: `1.5px solid ${p.selected ? C.accent : C.border}`,
              background: p.selected ? C.accentLight : C.white,
              cursor: "pointer", transition: "all 0.15s",
            }}
          >
            <div style={{
              width: 22, height: 22, borderRadius: 6,
              border: `2px solid ${p.selected ? C.accent : C.border}`,
              background: p.selected ? C.accent : "transparent",
              display: "flex", alignItems: "center", justifyContent: "center",
              color: "white", flexShrink: 0, transition: "all 0.15s",
            }}>
              {p.selected && <svg width="12" height="12" fill="none" stroke="currentColor" strokeWidth="2.5" viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg>}
            </div>
            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{ fontSize: 13, fontWeight: 600, color: C.text, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                {p.title}
              </div>
              <div style={{ fontSize: 11.5, color: C.sub, marginTop: 2 }}>{p.authors} · {p.year}</div>
            </div>
          </div>
        ))}
      </div>

      {/* Analyze button */}
      <button
        disabled={selectedCount < 3}
        style={{
          display: "flex", alignItems: "center", gap: 8, padding: "12px 28px", borderRadius: 12,
          border: "none", fontSize: 14, fontWeight: 600, cursor: selectedCount >= 3 ? "pointer" : "not-allowed",
          background: selectedCount >= 3 ? C.accent : C.borderLight,
          color: selectedCount >= 3 ? "white" : C.muted,
          transition: "all 0.2s",
        }}
      >
        {icons.sparkle} Analisis Research Gap ({selectedCount} paper)
      </button>
    </div>
  );
}

function AnalysisResult() {
  return (
    <div style={{ marginTop: 32 }}>
      <div style={{
        display: "flex", alignItems: "center", gap: 10, padding: "14px 20px", borderRadius: 12,
        background: `linear-gradient(135deg, ${C.accentLight}, ${C.purpleLight})`,
        border: `1px solid ${C.accent}30`, marginBottom: 24,
      }}>
        <span style={{ color: C.accent }}>{icons.sparkle}</span>
        <div>
          <div style={{ fontSize: 14, fontWeight: 700, color: C.text }}>Analisis Selesai</div>
          <div style={{ fontSize: 12, color: C.sub }}>Berdasarkan 5 paper yang dipilih · Powered by Groq (Gemma 2 9B)</div>
        </div>
      </div>

      {/* 1. Topik Dominan */}
      <div style={{ background: C.white, border: `1px solid ${C.border}`, borderRadius: 14, padding: "24px 28px", marginBottom: 16 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 18 }}>
          <div style={{ width: 32, height: 32, borderRadius: 8, background: C.accentLight, color: C.accent, display: "flex", alignItems: "center", justifyContent: "center" }}>{icons.topic}</div>
          <h2 style={{ fontSize: 15, fontWeight: 700, color: C.text, margin: 0 }}>Topik yang Sudah Banyak Diteliti</h2>
        </div>
        {analysisResult.topik.map((t, i) => (
          <div key={i} style={{ marginBottom: i < analysisResult.topik.length - 1 ? 14 : 0, display: "flex", gap: 12, alignItems: "flex-start" }}>
            <span style={{
              fontSize: 11, fontWeight: 700, padding: "3px 10px", borderRadius: 20,
              background: C.accentLight, color: C.accent, whiteSpace: "nowrap",
            }}>
              {t.count} paper
            </span>
            <div>
              <div style={{ fontSize: 13.5, fontWeight: 600, color: C.text }}>{t.name}</div>
              <div style={{ fontSize: 12.5, color: C.sub, marginTop: 3, lineHeight: 1.5 }}>{t.desc}</div>
            </div>
          </div>
        ))}
      </div>

      {/* 2. Metodologi */}
      <div style={{ background: C.white, border: `1px solid ${C.border}`, borderRadius: 14, padding: "24px 28px", marginBottom: 16 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 18 }}>
          <div style={{ width: 32, height: 32, borderRadius: 8, background: C.purpleLight, color: C.purple, display: "flex", alignItems: "center", justifyContent: "center" }}>{icons.method}</div>
          <h2 style={{ fontSize: 15, fontWeight: 700, color: C.text, margin: 0 }}>Metodologi yang Dominan</h2>
        </div>
        {analysisResult.metodologi.map((m, i) => (
          <div key={i} style={{ marginBottom: i < analysisResult.metodologi.length - 1 ? 14 : 0, display: "flex", gap: 12, alignItems: "flex-start" }}>
            <span style={{
              fontSize: 11, fontWeight: 700, padding: "3px 10px", borderRadius: 20,
              background: m.freq === "Sering" ? C.purpleLight : C.hover,
              color: m.freq === "Sering" ? C.purple : C.sub,
            }}>
              {m.freq}
            </span>
            <div>
              <div style={{ fontSize: 13.5, fontWeight: 600, color: C.text }}>{m.name}</div>
              <div style={{ fontSize: 12.5, color: C.sub, marginTop: 3, lineHeight: 1.5 }}>{m.desc}</div>
            </div>
          </div>
        ))}
      </div>

      {/* 3. Celah Penelitian */}
      <div style={{ background: C.white, border: `1px solid ${C.border}`, borderRadius: 14, padding: "24px 28px", marginBottom: 16 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 18 }}>
          <div style={{ width: 32, height: 32, borderRadius: 8, background: C.redLight, color: C.red, display: "flex", alignItems: "center", justifyContent: "center" }}>{icons.gap}</div>
          <h2 style={{ fontSize: 15, fontWeight: 700, color: C.text, margin: 0 }}>Celah Penelitian yang Teridentifikasi</h2>
        </div>
        {analysisResult.gaps.map((g, i) => (
          <div key={i} style={{
            marginBottom: 12, padding: "14px 18px", borderRadius: 10,
            border: `1px solid ${g.priority === "Tinggi" ? "#FECACA" : C.border}`,
            background: g.priority === "Tinggi" ? C.redLight : C.hover,
          }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 6 }}>
              <span style={{ fontSize: 13.5, fontWeight: 600, color: C.text }}>{g.title}</span>
              <span style={{
                fontSize: 10, fontWeight: 700, padding: "2px 8px", borderRadius: 20,
                background: g.priority === "Tinggi" ? C.red : C.orange, color: "white",
              }}>
                Prioritas {g.priority}
              </span>
            </div>
            <p style={{ fontSize: 12.5, color: C.sub, lineHeight: 1.6, margin: 0 }}>{g.desc}</p>
          </div>
        ))}
      </div>

      {/* 4. Saran Topik */}
      <div style={{ background: C.white, border: `1px solid ${C.border}`, borderRadius: 14, padding: "24px 28px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 18 }}>
          <div style={{ width: 32, height: 32, borderRadius: 8, background: C.greenLight, color: C.green, display: "flex", alignItems: "center", justifyContent: "center" }}>{icons.suggest}</div>
          <h2 style={{ fontSize: 15, fontWeight: 700, color: C.text, margin: 0 }}>Saran Topik Riset Lanjutan</h2>
        </div>
        {analysisResult.saran.map((s, i) => (
          <div key={i} style={{
            display: "flex", gap: 10, alignItems: "flex-start", marginBottom: 12,
            padding: "12px 16px", borderRadius: 10, background: C.greenLight,
            border: `1px solid #A7F3D0`,
          }}>
            <span style={{
              fontSize: 11, fontWeight: 700, width: 22, height: 22, borderRadius: "50%",
              background: C.green, color: "white", display: "flex", alignItems: "center", justifyContent: "center",
              flexShrink: 0,
            }}>
              {i + 1}
            </span>
            <span style={{ fontSize: 13, color: C.text, lineHeight: 1.5 }}>{s}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

export default function GapAnalysisDesign() {
  const [showResult, setShowResult] = useState(true);

  return (
    <div style={{ fontFamily: "'Inter', -apple-system, sans-serif", background: C.bg, minHeight: "100vh", display: "flex" }}>
      {/* Sidebar placeholder */}
      <div style={{ width: 240, borderRight: `1px solid ${C.border}`, background: C.white, padding: 20, position: "fixed", height: "100vh" }}>
        <div style={{ fontSize: 15, fontWeight: 700, color: C.text }}>ResearchFinder</div>
        <div style={{ marginTop: 24, fontSize: 13, color: C.sub }}>Search Papers</div>
        <div style={{ marginTop: 8, fontSize: 13, color: C.sub }}>Collections</div>
        <div style={{ marginTop: 8, fontSize: 13, color: C.accent, fontWeight: 600 }}>💡 Gap Analysis</div>
      </div>

      <div style={{ marginLeft: 240, flex: 1, padding: "28px 40px", maxWidth: 900 }}>
        <PaperSelector />
        <div style={{ marginTop: 20 }}>
          <button onClick={() => setShowResult(!showResult)} style={{
            padding: "8px 16px", borderRadius: 8, border: `1px solid ${C.border}`,
            background: C.hover, fontSize: 12, color: C.sub, cursor: "pointer",
          }}>
            {showResult ? "Sembunyikan" : "Tampilkan"} contoh hasil analisis
          </button>
        </div>
        {showResult && <AnalysisResult />}
      </div>
    </div>
  );
}
