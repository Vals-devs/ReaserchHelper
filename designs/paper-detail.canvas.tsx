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
  back: <svg width="18" height="18" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24"><path d="M19 12H5m7-7l-7 7 7 7"/></svg>,
  doi: <svg width="14" height="14" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24"><path d="M10 13a5 5 0 007.54.54l3-3a5 5 0 00-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 00-7.54-.54l-3 3a5 5 0 007.07 7.07l1.71-1.71"/></svg>,
  cite: <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24"><path d="M3 21c3 0 7-1 7-8V5c0-1.25-.756-2.017-2-2H4c-1.25 0-2 .75-2 1.972V11c0 1.25.75 2 2 2 1 0 1 0 1 1v1c0 1-1 2-2 2s-1 .008-1 1.031V21z"/><path d="M15 21c3 0 7-1 7-8V5c0-1.25-.757-2.017-2-2h-4c-1.25 0-2 .75-2 1.972V11c0 1.25.75 2 2 2h.75c0 2.25.25 4-2.75 4v3z"/></svg>,
  save: <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24"><path d="M19 21l-7-5-7 5V5a2 2 0 012-2h10a2 2 0 012 2z"/></svg>,
  sparkle: <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24"><path d="M12 3v1m0 16v1m-8-9H3m18 0h-1m-2.636-6.364l-.707.707M6.343 17.657l-.707.707m0-12.728l.707.707m11.314 11.314l.707.707M12 8a4 4 0 100 8 4 4 0 000-8z"/></svg>,
  related: <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><path d="M8 12h8m-4-4v8"/></svg>,
  explain: <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/></svg>,
  check: <svg width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg>,
  arrow: <svg width="14" height="14" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24"><path d="M5 12h14m-7-7l7 7-7 7"/></svg>,
};

const paper = {
  title: "Attention Is All You Need",
  authors: ["Ashish Vaswani", "Noam Shazeer", "Niki Parmar", "Jakob Uszkoreit", "Llion Jones", "Aidan N. Gomez"],
  year: 2017, source: "Semantic Scholar", citations: 89432, doi: "10.48550/arXiv.1706.03762",
  fields: ["Machine Learning", "NLP", "Deep Learning"],
  abstract: "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks that include an encoder and a decoder. The best performing models also connect the encoder and decoder through an attention mechanism. We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely. Experiments on two machine translation tasks show these models to be superior in quality while being more parallelizable and requiring significantly less time to train.",
  url: "https://arxiv.org/abs/1706.03762",
};

const aiSummary = {
  ringkasan: "Paper ini memperkenalkan Transformer, arsitektur neural network baru yang sepenuhnya berbasis mekanisme attention tanpa menggunakan recurrence atau convolution. Model ini menunjukkan performa superior pada tugas machine translation dan lebih mudah diparalelkan.",
  keyFindings: [
    "Self-attention mechanism dapat menggantikan recurrence untuk sequence modeling",
    "Multi-head attention memungkinkan model fokus pada berbagai representasi secara paralel",
    "Positional encoding digunakan untuk mempertahankan informasi urutan tanpa recurrence",
    "Transformer mencapai state-of-the-art pada WMT 2014 English-German translation",
  ],
  methodology: "Arsitektur encoder-decoder dengan multi-head self-attention, positional encoding, dan feed-forward layers. Dilatih pada dataset machine translation WMT 2014.",
};

const relatedPapers = [
  { title: "BERT: Pre-training of Deep Bidirectional Transformers", authors: "Devlin et al.", year: 2018, citations: 67231 },
  { title: "GPT-2: Language Models are Unsupervised Multitask Learners", authors: "Radford et al.", year: 2019, citations: 12543 },
  { title: "Vision Transformer (ViT)", authors: "Dosovitskiy et al.", year: 2020, citations: 23456 },
  { title: "T5: Exploring the Limits of Transfer Learning", authors: "Raffel et al.", year: 2019, citations: 8932 },
];

function SourceBadge({ source }: { source: string }) {
  return (
    <span style={{ fontSize: 10, fontWeight: 600, padding: "3px 10px", borderRadius: 20, background: C.accentLight, color: C.accent }}>
      {source}
    </span>
  );
}

export default function PaperDetailDesign() {
  const [summaryOpen, setSummaryOpen] = useState(true);

  return (
    <div style={{ fontFamily: "'Inter', -apple-system, sans-serif", background: C.bg, minHeight: "100vh", display: "flex" }}>
      {/* Sidebar placeholder */}
      <div style={{ width: 240, borderRight: `1px solid ${C.border}`, background: C.white, padding: 20, position: "fixed", height: "100vh" }}>
        <div style={{ fontSize: 15, fontWeight: 700, color: C.text }}>ResearchFinder</div>
      </div>

      <div style={{ marginLeft: 240, flex: 1, padding: "28px 40px" }}>
        {/* Back */}
        <button style={{
          display: "flex", alignItems: "center", gap: 6, border: "none", background: "transparent",
          fontSize: 13, color: C.sub, cursor: "pointer", marginBottom: 20, padding: 0,
        }}>
          {icons.back} Kembali ke hasil pencarian
        </button>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 380px", gap: 28, alignItems: "start" }}>
          {/* Left: Paper Info */}
          <div>
            {/* Header Card */}
            <div style={{ background: C.white, border: `1px solid ${C.border}`, borderRadius: 14, padding: "28px 32px" }}>
              <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 14 }}>
                <SourceBadge source={paper.source} />
                <span style={{ fontSize: 12, color: C.muted }}>{paper.year}</span>
                {paper.fields.map((f) => (
                  <span key={f} style={{ fontSize: 11, padding: "2px 10px", borderRadius: 6, background: C.greenLight, color: C.green, fontWeight: 500 }}>
                    {f}
                  </span>
                ))}
              </div>

              <h1 style={{ fontSize: 22, fontWeight: 700, color: C.text, margin: 0, lineHeight: 1.35 }}>
                {paper.title}
              </h1>

              <div style={{ fontSize: 13.5, color: C.sub, marginTop: 12, lineHeight: 1.6 }}>
                {paper.authors.join(", ")}
              </div>

              {/* Stats */}
              <div style={{ display: "flex", gap: 16, marginTop: 18, paddingTop: 18, borderTop: `1px solid ${C.borderLight}` }}>
                <div style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 13, color: C.sub }}>
                  {icons.cite} <strong style={{ color: C.text }}>{paper.citations.toLocaleString()}</strong> sitasi
                </div>
                <div style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 13, color: C.accent }}>
                  {icons.doi} DOI: {paper.doi}
                </div>
              </div>

              {/* Actions */}
              <div style={{ display: "flex", gap: 8, marginTop: 18 }}>
                <button style={{ display: "flex", alignItems: "center", gap: 6, padding: "9px 16px", borderRadius: 10, border: `1px solid ${C.border}`, background: C.white, fontSize: 13, color: C.sub, cursor: "pointer", fontWeight: 500 }}>
                  {icons.save} Simpan ke Koleksi
                </button>
                <button style={{ display: "flex", alignItems: "center", gap: 6, padding: "9px 16px", borderRadius: 10, border: "none", background: C.accentLight, fontSize: 13, color: C.accent, cursor: "pointer", fontWeight: 600 }}>
                  {icons.related} Find Related
                </button>
                <button style={{ display: "flex", alignItems: "center", gap: 6, padding: "9px 16px", borderRadius: 10, border: `1px solid ${C.border}`, background: C.white, fontSize: 13, color: C.sub, cursor: "pointer", fontWeight: 500 }}>
                  {icons.explain} Jelaskan Teks
                </button>
              </div>
            </div>

            {/* Abstract */}
            <div style={{ background: C.white, border: `1px solid ${C.border}`, borderRadius: 14, padding: "24px 32px", marginTop: 16 }}>
              <h2 style={{ fontSize: 15, fontWeight: 700, color: C.text, margin: 0, marginBottom: 12 }}>Abstrak</h2>
              <p style={{ fontSize: 14, color: C.sub, lineHeight: 1.75, margin: 0 }}>
                {paper.abstract}
              </p>
            </div>

            {/* Related Papers */}
            <div style={{ background: C.white, border: `1px solid ${C.border}`, borderRadius: 14, padding: "24px 32px", marginTop: 16 }}>
              <h2 style={{ fontSize: 15, fontWeight: 700, color: C.text, margin: 0, marginBottom: 16 }}>Paper Terkait</h2>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
                {relatedPapers.map((p) => (
                  <div key={p.title} style={{
                    padding: "14px 16px", borderRadius: 10, border: `1px solid ${C.border}`,
                    background: C.hover, cursor: "pointer", transition: "border-color 0.15s",
                  }}>
                    <div style={{ fontSize: 13, fontWeight: 600, color: C.text, lineHeight: 1.4, marginBottom: 6 }}>
                      {p.title}
                    </div>
                    <div style={{ fontSize: 11.5, color: C.muted }}>{p.authors} · {p.year}</div>
                    <div style={{ fontSize: 11.5, color: C.sub, marginTop: 4, display: "flex", alignItems: "center", gap: 4 }}>
                      {icons.cite} {p.citations.toLocaleString()}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Right: AI Summary Panel */}
          <div style={{ position: "sticky", top: 28 }}>
            <div style={{ background: C.white, border: `1px solid ${C.border}`, borderRadius: 14, overflow: "hidden" }}>
              {/* Header */}
              <button
                onClick={() => setSummaryOpen(!summaryOpen)}
                style={{
                  width: "100%", display: "flex", alignItems: "center", justifyContent: "space-between",
                  padding: "18px 22px", border: "none", background: `linear-gradient(135deg, ${C.accentLight}, ${C.purpleLight})`,
                  cursor: "pointer",
                }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                  <span style={{ color: C.accent, display: "flex" }}>{icons.sparkle}</span>
                  <span style={{ fontSize: 14, fontWeight: 700, color: C.text }}>AI Summary</span>
                  <span style={{ fontSize: 10, fontWeight: 600, padding: "2px 8px", borderRadius: 20, background: C.accent, color: "white" }}>
                    Groq
                  </span>
                </div>
                <span style={{ fontSize: 18, color: C.sub, transform: summaryOpen ? "rotate(180deg)" : "rotate(0)", transition: "0.2s" }}>
                  ▾
                </span>
              </button>

              {summaryOpen && (
                <div style={{ padding: "20px 22px" }}>
                  {/* Ringkasan */}
                  <div style={{ marginBottom: 18 }}>
                    <div style={{ fontSize: 11, fontWeight: 600, color: C.muted, textTransform: "uppercase", letterSpacing: "0.5px", marginBottom: 8 }}>
                      Ringkasan
                    </div>
                    <p style={{ fontSize: 13, color: C.text, lineHeight: 1.7, margin: 0 }}>
                      {aiSummary.ringkasan}
                    </p>
                  </div>

                  {/* Key Findings */}
                  <div style={{ marginBottom: 18 }}>
                    <div style={{ fontSize: 11, fontWeight: 600, color: C.muted, textTransform: "uppercase", letterSpacing: "0.5px", marginBottom: 10 }}>
                      Temuan Utama
                    </div>
                    <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                      {aiSummary.keyFindings.map((f, i) => (
                        <div key={i} style={{ display: "flex", gap: 8, alignItems: "flex-start" }}>
                          <span style={{ color: C.green, marginTop: 2, flexShrink: 0 }}>{icons.check}</span>
                          <span style={{ fontSize: 12.5, color: C.text, lineHeight: 1.5 }}>{f}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Methodology */}
                  <div style={{
                    padding: "14px 16px", borderRadius: 10, background: C.orangeLight,
                    border: `1px solid #FDE68A`,
                  }}>
                    <div style={{ fontSize: 11, fontWeight: 600, color: C.orange, marginBottom: 6 }}>
                      Metodologi
                    </div>
                    <p style={{ fontSize: 12.5, color: C.text, lineHeight: 1.6, margin: 0 }}>
                      {aiSummary.methodology}
                    </p>
                  </div>

                  <button style={{
                    width: "100%", marginTop: 16, padding: "10px 0", borderRadius: 10,
                    border: `1px solid ${C.border}`, background: C.white, fontSize: 13,
                    color: C.sub, cursor: "pointer", fontWeight: 500,
                  }}>
                    Regenerate Summary
                  </button>
                </div>
              )}
            </div>

            {/* Plain Language Explainer */}
            <div style={{ background: C.white, border: `1px solid ${C.border}`, borderRadius: 14, padding: "20px 22px", marginTop: 14 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 14 }}>
                {icons.explain}
                <span style={{ fontSize: 14, fontWeight: 700, color: C.text }}>Jelaskan Teks</span>
              </div>
              <textarea
                placeholder="Paste bagian paper yang ingin dijelaskan..."
                rows={3}
                style={{
                  width: "100%", padding: "10px 14px", borderRadius: 10,
                  border: `1px solid ${C.border}`, fontSize: 13, background: C.hover,
                  resize: "none", outline: "none", color: C.text, boxSizing: "border-box",
                  fontFamily: "'Inter', sans-serif",
                }}
              />
              <div style={{ display: "flex", gap: 6, marginTop: 10 }}>
                <button style={{
                  padding: "7px 14px", borderRadius: 8, border: "none",
                  background: C.accent, color: "white", fontSize: 12, fontWeight: 600, cursor: "pointer",
                }}>
                  Jelaskan (ID)
                </button>
                <button style={{
                  padding: "7px 14px", borderRadius: 8, border: `1px solid ${C.border}`,
                  background: C.white, color: C.sub, fontSize: 12, fontWeight: 500, cursor: "pointer",
                }}>
                  Explain (EN)
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
