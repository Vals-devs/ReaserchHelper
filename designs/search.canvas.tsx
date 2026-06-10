import { useState } from "react";

const C = {
  bg: "#FAFAFA", white: "#FFFFFF", border: "#E5E7EB", borderLight: "#F3F4F6",
  text: "#111827", sub: "#6B7280", muted: "#9CA3AF",
  accent: "#2563EB", accentLight: "#EFF6FF", accentBg: "#DBEAFE",
  green: "#059669", greenLight: "#ECFDF5",
  orange: "#D97706", orangeLight: "#FFFBEB",
  purple: "#7C3AED", purpleLight: "#F5F3FF",
  hover: "#F9FAFB",
};

const icon = {
  search: <svg width="18" height="18" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>,
  filter: <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24"><path d="M22 3H2l8 9.46V19l4 2v-8.54L22 3z"/></svg>,
  bookmark: <svg width="15" height="15" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24"><path d="M19 21l-7-5-7 5V5a2 2 0 012-2h10a2 2 0 012 2z"/></svg>,
  sparkle: <svg width="15" height="15" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24"><path d="M12 3v1m0 16v1m-8-9H3m18 0h-1m-2.636-6.364l-.707.707M6.343 17.657l-.707.707m0-12.728l.707.707m11.314 11.314l.707.707M12 8a4 4 0 100 8 4 4 0 000-8z"/></svg>,
  cite: <svg width="15" height="15" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24"><path d="M3 21c3 0 7-1 7-8V5c0-1.25-.756-2.017-2-2H4c-1.25 0-2 .75-2 1.972V11c0 1.25.75 2 2 2 1 0 1 0 1 1v1c0 1-1 2-2 2s-1 .008-1 1.031V21z"/><path d="M15 21c3 0 7-1 7-8V5c0-1.25-.757-2.017-2-2h-4c-1.25 0-2 .75-2 1.972V11c0 1.25.75 2 2 2h.75c0 2.25.25 4-2.75 4v3z"/></svg>,
  ext: <svg width="13" height="13" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24"><path d="M18 13v6a2 2 0 01-2 2H5a2 2 0 01-2-2V8a2 2 0 012-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>,
};

const papers = [
  {
    title: "Attention Is All You Need",
    authors: ["Ashish Vaswani", "Noam Shazeer", "Niki Parmar", "Jakob Uszkoreit"],
    year: 2017, source: "Semantic Scholar", citations: 89432,
    abstract: "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks that include an encoder and a decoder. The best performing models also connect the encoder and decoder through an attention mechanism. We propose a new simple network architecture, the Transformer, based solely on attention mechanisms...",
    fields: ["Machine Learning", "NLP"],
  },
  {
    title: "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding",
    authors: ["Jacob Devlin", "Ming-Wei Chang", "Kenton Lee", "Kristina Toutanova"],
    year: 2018, source: "arXiv", citations: 67231,
    abstract: "We introduce a new language representation model called BERT, which stands for Bidirectional Encoder Representations from Transformers. Unlike recent language representation models, BERT is designed to pre-train deep bidirectional representations from unlabeled text by jointly conditioning on both left and right context...",
    fields: ["NLP", "Deep Learning"],
  },
  {
    title: "Generative Adversarial Networks",
    authors: ["Ian Goodfellow", "Jean Pouget-Abadie", "Mehdi Mirza", "Bing Xu"],
    year: 2014, source: "Semantic Scholar", citations: 45891,
    abstract: "We propose a new framework for estimating generative models via an adversarial process, in which we simultaneously train two models: a generative model G that captures the data distribution, and a discriminative model D that estimates the probability that a sample came from the training data rather than G...",
    fields: ["Machine Learning", "Computer Vision"],
  },
];

const filterChips = [
  { label: "All Sources", active: true, color: C.accent, bg: C.accentLight },
  { label: "Semantic Scholar", active: false, color: C.sub, bg: C.hover },
  { label: "arXiv", active: false, color: C.sub, bg: C.hover },
  { label: "2020–2026", active: false, color: C.sub, bg: C.hover },
  { label: "Computer Science", active: true, color: C.accent, bg: C.accentLight },
];

function SourceBadge({ source }: { source: string }) {
  const isArxiv = source === "arXiv";
  return (
    <span style={{
      fontSize: 10, fontWeight: 600, padding: "2px 8px", borderRadius: 20,
      background: isArxiv ? C.purpleLight : C.accentLight,
      color: isArxiv ? C.purple : C.accent,
    }}>
      {source}
    </span>
  );
}

function PaperCard({ paper }: { paper: typeof papers[0] }) {
  return (
    <div style={{
      background: C.white, border: `1px solid ${C.border}`, borderRadius: 12,
      padding: "20px 24px", transition: "box-shadow 0.15s, border-color 0.15s",
      cursor: "pointer",
    }}>
      {/* Top row */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 12 }}>
        <div style={{ flex: 1 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 6 }}>
            <SourceBadge source={paper.source} />
            <span style={{ fontSize: 11, color: C.muted }}>{paper.year}</span>
          </div>
          <h3 style={{ fontSize: 15, fontWeight: 700, color: C.text, margin: 0, lineHeight: 1.4 }}>
            {paper.title}
          </h3>
        </div>
        <div style={{
          display: "flex", alignItems: "center", gap: 4, fontSize: 12,
          color: C.sub, background: C.hover, padding: "4px 10px", borderRadius: 8, whiteSpace: "nowrap",
        }}>
          {icon.cite} {paper.citations.toLocaleString()}
        </div>
      </div>

      {/* Authors */}
      <div style={{ fontSize: 12.5, color: C.sub, marginTop: 8, lineHeight: 1.5 }}>
        {paper.authors.join(", ")}
      </div>

      {/* Abstract */}
      <p style={{
        fontSize: 13, color: C.sub, marginTop: 10, lineHeight: 1.65,
        display: "-webkit-box", WebkitLineClamp: 3, WebkitBoxOrient: "vertical",
        overflow: "hidden", margin: "10px 0 0",
      }}>
        {paper.abstract}
      </p>

      {/* Fields */}
      <div style={{ display: "flex", flexWrap: "wrap", gap: 6, marginTop: 12 }}>
        {paper.fields.map((f) => (
          <span key={f} style={{
            fontSize: 11, padding: "3px 10px", borderRadius: 6,
            background: C.greenLight, color: C.green, fontWeight: 500,
          }}>
            {f}
          </span>
        ))}
      </div>

      {/* Actions */}
      <div style={{
        display: "flex", alignItems: "center", gap: 8, marginTop: 16,
        paddingTop: 14, borderTop: `1px solid ${C.borderLight}`,
      }}>
        <button style={{
          display: "flex", alignItems: "center", gap: 6, padding: "7px 14px", borderRadius: 8,
          border: `1px solid ${C.border}`, background: C.white, fontSize: 12,
          color: C.sub, cursor: "pointer", fontWeight: 500,
        }}>
          {icon.bookmark} Simpan
        </button>
        <button style={{
          display: "flex", alignItems: "center", gap: 6, padding: "7px 14px", borderRadius: 8,
          border: "none", background: C.accentLight, fontSize: 12,
          color: C.accent, cursor: "pointer", fontWeight: 600,
        }}>
          {icon.sparkle} Summarize
        </button>
        <button style={{
          display: "flex", alignItems: "center", gap: 6, padding: "7px 14px", borderRadius: 8,
          border: `1px solid ${C.border}`, background: C.white, fontSize: 12,
          color: C.sub, cursor: "pointer", fontWeight: 500,
        }}>
          {icon.ext} Buka Paper
        </button>
      </div>
    </div>
  );
}

export default function SearchDesign() {
  const [query, setQuery] = useState("transformer neural network");
  const [showResults, setShowResults] = useState(true);

  return (
    <div style={{ fontFamily: "'Inter', -apple-system, sans-serif", background: C.bg, minHeight: "100vh", display: "flex" }}>
      {/* Sidebar placeholder */}
      <div style={{ width: 240, borderRight: `1px solid ${C.border}`, background: C.white, padding: 20, position: "fixed", height: "100vh" }}>
        <div style={{ fontSize: 15, fontWeight: 700, color: C.text }}>ResearchFinder</div>
        <div style={{ marginTop: 24, fontSize: 13, color: C.accent, fontWeight: 600 }}>🔍 Search Papers</div>
        <div style={{ marginTop: 8, fontSize: 13, color: C.sub }}>Collections</div>
        <div style={{ marginTop: 8, fontSize: 13, color: C.sub }}>History</div>
        <div style={{ marginTop: 8, fontSize: 13, color: C.sub }}>Gap Analysis</div>
      </div>

      {/* Main */}
      <div style={{ marginLeft: 240, flex: 1, padding: "32px 40px" }}>
        {/* Header */}
        <div style={{ marginBottom: 28 }}>
          <h1 style={{ fontSize: 22, fontWeight: 700, color: C.text, margin: 0 }}>Search Papers</h1>
          <p style={{ fontSize: 13, color: C.sub, marginTop: 4 }}>
            Cari dari Semantic Scholar dan arXiv secara bersamaan
          </p>
        </div>

        {/* Search Bar */}
        <div style={{
          display: "flex", alignItems: "center", gap: 10, background: C.white,
          border: `1.5px solid ${C.border}`, borderRadius: 14, padding: "14px 20px",
          boxShadow: "0 1px 4px rgba(0,0,0,0.04)",
        }}>
          <span style={{ color: C.muted, display: "flex" }}>{icon.search}</span>
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Cari paper berdasarkan judul, keyword, atau topik..."
            style={{
              flex: 1, border: "none", outline: "none", fontSize: 15,
              color: C.text, background: "transparent",
            }}
          />
          <button
            onClick={() => setShowResults(true)}
            style={{
              padding: "8px 20px", borderRadius: 10, border: "none",
              background: C.accent, color: "white", fontSize: 13,
              fontWeight: 600, cursor: "pointer",
            }}
          >
            Cari
          </button>
        </div>

        {/* Filter Chips */}
        <div style={{ display: "flex", flexWrap: "wrap", gap: 8, marginTop: 16, alignItems: "center" }}>
          <span style={{ display: "flex", alignItems: "center", color: C.muted, marginRight: 4 }}>{icon.filter}</span>
          {filterChips.map((chip) => (
            <span key={chip.label} style={{
              padding: "6px 14px", borderRadius: 20, fontSize: 12, fontWeight: 500,
              background: chip.active ? chip.bg : C.white,
              color: chip.active ? chip.color : C.sub,
              border: `1px solid ${chip.active ? "transparent" : C.border}`,
              cursor: "pointer",
            }}>
              {chip.label}
            </span>
          ))}
        </div>

        {/* Results count */}
        {showResults && (
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: 24, marginBottom: 16 }}>
            <span style={{ fontSize: 13, color: C.sub }}>
              Menampilkan <strong style={{ color: C.text }}>3 hasil</strong> untuk "{query}"
            </span>
            <select style={{
              padding: "6px 12px", borderRadius: 8, border: `1px solid ${C.border}`,
              fontSize: 12, color: C.sub, background: C.white, cursor: "pointer",
            }}>
              <option>Urutkan: Relevansi</option>
              <option>Sitasi terbanyak</option>
              <option>Terbaru</option>
            </select>
          </div>
        )}

        {/* Paper List */}
        {showResults && (
          <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
            {papers.map((p) => <PaperCard key={p.title} paper={p} />)}
          </div>
        )}

        {/* Empty state toggle */}
        {!showResults && (
          <div style={{
            textAlign: "center", padding: 60, marginTop: 40,
            background: C.white, border: `1px solid ${C.border}`, borderRadius: 16,
          }}>
            <div style={{ fontSize: 48 }}>📄</div>
            <h3 style={{ fontSize: 16, fontWeight: 600, color: C.text, marginTop: 12 }}>
              Mulai pencarian paper ilmiah
            </h3>
            <p style={{ fontSize: 13, color: C.sub, marginTop: 6 }}>
              Ketik topik atau keyword untuk menemukan paper dari Semantic Scholar dan arXiv
            </p>
            <button
              onClick={() => setShowResults(true)}
              style={{
                marginTop: 16, padding: "10px 24px", borderRadius: 10, border: "none",
                background: C.accent, color: "white", fontSize: 13, fontWeight: 600, cursor: "pointer",
              }}
            >
              Coba contoh pencarian
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
