/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ["class"],
  content: [
    "./index.html",
    "./src/**/*.{ts,tsx,js,jsx}",
  ],
  theme: {
    extend: {
      colors: {
        // RaahPay Design System — Light Fintech Premium
        primary: {
          DEFAULT: "#4F46E5",
          50: "#EEF2FF",
          100: "#E0E7FF",
          200: "#C7D2FE",
          300: "#A5B4FC",
          400: "#818CF8",
          500: "#6366F1",
          600: "#4F46E5",
          700: "#4338CA",
          800: "#3730A3",
          900: "#312E81",
        },
        accent: "#F59E0B",       // Amber CTA / highlights
        success: "#10B981",
        warning: "#F59E0B",
        danger: "#EF4444",
        surface: {
          DEFAULT: "#F8FAFC",    // page bg
          card: "#FFFFFF",       // card bg
          elevated: "#F1F5F9",   // slightly raised
          glass: "rgba(255,255,255,0.75)",
        },
        ink: {
          DEFAULT: "#0F172A",   // primary text
          muted: "#475569",     // secondary text
          faint: "#94A3B8",     // placeholder / labels
        },
        border: {
          DEFAULT: "#E2E8F0",
          strong: "#CBD5E1",
        },
      },
      fontFamily: {
        heading: ["DM Sans", "Inter", "sans-serif"],
        body: ["DM Sans", "Inter", "sans-serif"],
      },
      backgroundImage: {
        "hero-mesh": "radial-gradient(ellipse 80% 50% at 50% -20%, rgba(99,102,241,0.15), transparent), radial-gradient(ellipse 60% 40% at 80% 60%, rgba(245,158,11,0.08), transparent)",
        "card-gradient": "linear-gradient(135deg, rgba(255,255,255,0.9) 0%, rgba(248,250,252,0.95) 100%)",
      },
      boxShadow: {
        "card":   "0 1px 3px rgba(0,0,0,0.06), 0 4px 16px rgba(0,0,0,0.04)",
        "card-hover": "0 4px 24px rgba(79,70,229,0.12), 0 1px 4px rgba(0,0,0,0.06)",
        "glow":   "0 0 24px rgba(99,102,241,0.25)",
        "glow-amber": "0 0 20px rgba(245,158,11,0.25)",
        "inner-ring": "inset 0 0 0 1px rgba(99,102,241,0.15)",
      },
      animation: {
        "fade-in": "fadeIn 0.3s ease-in-out",
        "slide-up": "slideUp 0.4s ease-out",
        pulse: "pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        "shimmer": "shimmer 2s linear infinite",
      },
      keyframes: {
        fadeIn: {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        slideUp: {
          "0%": { opacity: "0", transform: "translateY(12px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        shimmer: {
          "0%": { backgroundPosition: "-200% 0" },
          "100%": { backgroundPosition: "200% 0" },
        },
      },
      backdropBlur: {
        xs: "4px",
      },
    },
  },
  plugins: [],
};
