import { useState } from "react";

const colors = {
  bg: "#FAFAFA",
  white: "#FFFFFF",
  border: "#E5E7EB",
  borderFocus: "#2563EB",
  text: "#111827",
  textSecondary: "#6B7280",
  textTertiary: "#9CA3AF",
  accent: "#2563EB",
  accentHover: "#1D4ED8",
  accentLight: "#EFF6FF",
  error: "#EF4444",
  inputBg: "#F9FAFB",
};

const Logo = () => (
  <div style={{ display: "flex", alignItems: "center", gap: 10, justifyContent: "center", marginBottom: 28 }}>
    <svg width="36" height="36" viewBox="0 0 32 32" fill="none">
      <rect width="32" height="32" rx="8" fill={colors.accent} />
      <path d="M10 10h4v12h-4zM18 10h4v8h-4z" fill="white" opacity="0.9" />
      <circle cx="20" cy="22" r="2" fill="white" opacity="0.9" />
    </svg>
    <div>
      <div style={{ fontSize: 18, fontWeight: 700, color: colors.text, letterSpacing: "-0.3px" }}>
        ResearchFinder
      </div>
      <div style={{ fontSize: 11, color: colors.textTertiary }}>AI-Powered Research Tool</div>
    </div>
  </div>
);

function InputField({ label, type = "text", placeholder, icon }) {
  const [focused, setFocused] = useState(false);
  return (
    <div style={{ marginBottom: 16 }}>
      <label style={{ fontSize: 13, fontWeight: 500, color: colors.text, display: "block", marginBottom: 6 }}>
        {label}
      </label>
      <div style={{ position: "relative" }}>
        {icon && (
          <span
            style={{
              position: "absolute",
              left: 12,
              top: "50%",
              transform: "translateY(-50%)",
              color: focused ? colors.accent : colors.textTertiary,
              display: "flex",
              transition: "color 0.15s",
            }}
          >
            {icon}
          </span>
        )}
        <input
          type={type}
          placeholder={placeholder}
          onFocus={() => setFocused(true)}
          onBlur={() => setFocused(false)}
          style={{
            width: "100%",
            padding: icon ? "10px 14px 10px 38px" : "10px 14px",
            border: `1.5px solid ${focused ? colors.borderFocus : colors.border}`,
            borderRadius: 10,
            fontSize: 13.5,
            background: colors.inputBg,
            outline: "none",
            color: colors.text,
            transition: "border-color 0.15s",
            boxSizing: "border-box",
          }}
        />
      </div>
    </div>
  );
}

function Divider() {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 12, margin: "20px 0" }}>
      <div style={{ flex: 1, height: 1, background: colors.border }} />
      <span style={{ fontSize: 12, color: colors.textTertiary }}>atau</span>
      <div style={{ flex: 1, height: 1, background: colors.border }} />
    </div>
  );
}

function LoginPage() {
  const emailIcon = (
    <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24">
      <rect x="2" y="4" width="20" height="16" rx="2" />
      <path d="m22 7-8.97 5.7a1.94 1.94 0 01-2.06 0L2 7" />
    </svg>
  );
  const passIcon = (
    <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24">
      <rect x="3" y="11" width="18" height="11" rx="2" />
      <path d="M7 11V7a5 5 0 0110 0v4" />
    </svg>
  );

  return (
    <div style={{ width: "100%", maxWidth: 380, margin: "0 auto" }}>
      <Logo />
      <div
        style={{
          background: colors.white,
          border: `1px solid ${colors.border}`,
          borderRadius: 16,
          padding: "32px 28px",
          boxShadow: "0 1px 3px rgba(0,0,0,0.04)",
        }}
      >
        <h2 style={{ fontSize: 18, fontWeight: 700, color: colors.text, margin: 0, textAlign: "center" }}>
          Selamat Datang Kembali
        </h2>
        <p style={{ fontSize: 13, color: colors.textSecondary, textAlign: "center", marginTop: 6, marginBottom: 24 }}>
          Masuk ke akun ResearchFinder kamu
        </p>

        <InputField label="Email" type="email" placeholder="nama@universitas.ac.id" icon={emailIcon} />
        <InputField label="Password" type="password" placeholder="Masukkan password" icon={passIcon} />

        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
          <label style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 13, color: colors.textSecondary, cursor: "pointer" }}>
            <input type="checkbox" style={{ accentColor: colors.accent }} />
            Ingat saya
          </label>
          <a href="#" style={{ fontSize: 13, color: colors.accent, textDecoration: "none", fontWeight: 500 }}>
            Lupa password?
          </a>
        </div>

        <button
          style={{
            width: "100%",
            padding: "11px 0",
            borderRadius: 10,
            border: "none",
            background: colors.accent,
            color: "white",
            fontSize: 14,
            fontWeight: 600,
            cursor: "pointer",
            transition: "background 0.15s",
          }}
        >
          Masuk
        </button>

        <Divider />

        <button
          style={{
            width: "100%",
            padding: "11px 0",
            borderRadius: 10,
            border: `1.5px solid ${colors.border}`,
            background: colors.white,
            color: colors.text,
            fontSize: 14,
            fontWeight: 500,
            cursor: "pointer",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: 8,
          }}
        >
          <svg width="16" height="16" viewBox="0 0 24 24">
            <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 01-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z" />
            <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
            <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
            <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
          </svg>
          Masuk dengan Google
        </button>
      </div>

      <p style={{ fontSize: 13, color: colors.textSecondary, textAlign: "center", marginTop: 20 }}>
        Belum punya akun?{" "}
        <a href="#" style={{ color: colors.accent, textDecoration: "none", fontWeight: 600 }}>Daftar gratis</a>
      </p>
    </div>
  );
}

function RegisterPage() {
  const userIcon = (
    <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24">
      <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2" /><circle cx="12" cy="7" r="4" />
    </svg>
  );
  const emailIcon = (
    <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24">
      <rect x="2" y="4" width="20" height="16" rx="2" />
      <path d="m22 7-8.97 5.7a1.94 1.94 0 01-2.06 0L2 7" />
    </svg>
  );
  const passIcon = (
    <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24">
      <rect x="3" y="11" width="18" height="11" rx="2" />
      <path d="M7 11V7a5 5 0 0110 0v4" />
    </svg>
  );
  const instIcon = (
    <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24">
      <path d="M22 10v6M2 10l10-5 10 5-10 5z" /><path d="M6 12v5c3 3 9 3 12 0v-5" />
    </svg>
  );

  return (
    <div style={{ width: "100%", maxWidth: 400, margin: "0 auto" }}>
      <Logo />
      <div
        style={{
          background: colors.white,
          border: `1px solid ${colors.border}`,
          borderRadius: 16,
          padding: "32px 28px",
          boxShadow: "0 1px 3px rgba(0,0,0,0.04)",
        }}
      >
        <h2 style={{ fontSize: 18, fontWeight: 700, color: colors.text, margin: 0, textAlign: "center" }}>
          Buat Akun Baru
        </h2>
        <p style={{ fontSize: 13, color: colors.textSecondary, textAlign: "center", marginTop: 6, marginBottom: 24 }}>
          Mulai perjalanan riset kamu di sini
        </p>

        <InputField label="Nama Lengkap" placeholder="Ival Permana" icon={userIcon} />
        <InputField label="Email" type="email" placeholder="nama@universitas.ac.id" icon={emailIcon} />
        <InputField label="Password" type="password" placeholder="Minimal 8 karakter" icon={passIcon} />
        <InputField label="Institusi / Universitas" placeholder="Universitas Indonesia" icon={instIcon} />

        {/* Research Interests */}
        <div style={{ marginBottom: 20 }}>
          <label style={{ fontSize: 13, fontWeight: 500, color: colors.text, display: "block", marginBottom: 6 }}>
            Minat Riset <span style={{ color: colors.textTertiary, fontWeight: 400 }}>(opsional)</span>
          </label>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
            {["Machine Learning", "NLP", "Computer Vision", "Data Science", "Cybersecurity", "IoT", "Software Engineering"].map((tag) => (
              <span
                key={tag}
                style={{
                  padding: "5px 12px",
                  borderRadius: 20,
                  border: `1px solid ${colors.border}`,
                  background: colors.inputBg,
                  fontSize: 12,
                  color: colors.textSecondary,
                  cursor: "pointer",
                }}
              >
                {tag}
              </span>
            ))}
          </div>
        </div>

        <button
          style={{
            width: "100%",
            padding: "11px 0",
            borderRadius: 10,
            border: "none",
            background: colors.accent,
            color: "white",
            fontSize: 14,
            fontWeight: 600,
            cursor: "pointer",
          }}
        >
          Daftar Sekarang
        </button>

        <p style={{ fontSize: 11, color: colors.textTertiary, textAlign: "center", marginTop: 14, lineHeight: 1.5 }}>
          Dengan mendaftar, kamu menyetujui{" "}
          <a href="#" style={{ color: colors.accent, textDecoration: "none" }}>Terms of Service</a>{" "}
          dan{" "}
          <a href="#" style={{ color: colors.accent, textDecoration: "none" }}>Privacy Policy</a>
        </p>
      </div>

      <p style={{ fontSize: 13, color: colors.textSecondary, textAlign: "center", marginTop: 20 }}>
        Sudah punya akun?{" "}
        <a href="#" style={{ color: colors.accent, textDecoration: "none", fontWeight: 600 }}>Masuk di sini</a>
      </p>
    </div>
  );
}

export default function AuthDesign() {
  const [page, setPage] = useState<"login" | "register">("login");

  return (
    <div
      style={{
        fontFamily: "'Inter', -apple-system, sans-serif",
        background: colors.bg,
        minHeight: "100vh",
        display: "flex",
        flexDirection: "column",
      }}
    >
      {/* Tab switcher */}
      <div style={{ display: "flex", justifyContent: "center", gap: 4, padding: "20px 0 0" }}>
        {(["login", "register"] as const).map((p) => (
          <button
            key={p}
            onClick={() => setPage(p)}
            style={{
              padding: "7px 20px",
              borderRadius: 8,
              border: "none",
              background: page === p ? colors.accent : "transparent",
              color: page === p ? "white" : colors.textSecondary,
              fontSize: 13,
              fontWeight: 600,
              cursor: "pointer",
            }}
          >
            {p === "login" ? "Login" : "Register"}
          </button>
        ))}
      </div>

      <div style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center", padding: "20px 16px" }}>
        {page === "login" ? <LoginPage /> : <RegisterPage />}
      </div>

      {/* Footer */}
      <div style={{ textAlign: "center", padding: "16px", fontSize: 12, color: colors.textTertiary }}>
        © 2026 ResearchFinder — Made for Indonesian researchers
      </div>
    </div>
  );
}
