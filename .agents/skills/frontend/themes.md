---
name: frontend-themes
description: Theme factory for frontend projects. Contains 17 production-ready themes (dark, light, neobrutalist, glassmorphism, tonal) with full CSS variable token sets for colors, shadows, and border radii. Use when choosing or building a visual theme.
---

# Theme Factory

All themes follow this token contract. Apply as CSS custom properties in `:root` or a `[data-theme="name"]` selector.

## Token Contract

```css
/* Every theme must define ALL of these tokens */
--color-primary          /* Main brand color — buttons, links, accents */
--color-primary-hover    /* Darkened primary for hover/active states */
--color-primary-fg       /* Foreground on top of primary (usually white or very dark) */

--color-secondary        /* Supporting brand color — secondary buttons, tags */
--color-secondary-hover
--color-secondary-fg

--color-accent           /* Highlight / pop color — badges, underlines, decorative */
--color-accent-hover
--color-accent-fg

--color-background       /* Page/app background */
--color-surface          /* Card / panel background (slightly elevated from bg) */
--color-surface-2        /* Second elevation (modals, dropdowns) */
--color-border           /* Default border color */
--color-border-strong    /* Prominent borders (dividers, active outlines) */

--color-text             /* Primary readable text */
--color-text-muted       /* Secondary/placeholder text */
--color-text-subtle      /* Tertiary, disabled text */
--color-text-inverse     /* Text on dark/primary backgrounds */

--color-success          /* #22c55e family */
--color-warning          /* #f59e0b family */
--color-error            /* #ef4444 family */
--color-info             /* #3b82f6 family */

--color-overlay          /* Semi-transparent overlay for modals */
--shadow-sm              /* Subtle shadow */
--shadow-md              /* Card shadow */
--shadow-lg              /* Elevated panel shadow */
--radius-sm              /* 4px */
--radius-md              /* 8px */
--radius-lg              /* 12px */
--radius-xl              /* 16px */
--radius-full            /* 9999px */
```

---

## 🌑 Dark Themes

### midnight-ember
Obsidian background, ember/amber accent. Premium SaaS, dev tools, analytics.
```css
[data-theme="midnight-ember"] {
  --color-primary:        #f97316;
  --color-primary-hover:  #ea6d0a;
  --color-primary-fg:     #ffffff;
  --color-secondary:      #374151;
  --color-secondary-hover:#4b5563;
  --color-secondary-fg:   #f9fafb;
  --color-accent:         #fbbf24;
  --color-accent-hover:   #f59e0b;
  --color-accent-fg:      #1c1917;
  --color-background:     #0a0a0a;
  --color-surface:        #111111;
  --color-surface-2:      #1a1a1a;
  --color-border:         #1f1f1f;
  --color-border-strong:  #333333;
  --color-text:           #f4f4f5;
  --color-text-muted:     #a1a1aa;
  --color-text-subtle:    #71717a;
  --color-text-inverse:   #0a0a0a;
  --color-success:        #22c55e;
  --color-warning:        #f59e0b;
  --color-error:          #ef4444;
  --color-info:           #3b82f6;
  --color-overlay:        rgba(0,0,0,0.75);
  --shadow-sm:            0 1px 3px rgba(0,0,0,0.5);
  --shadow-md:            0 4px 16px rgba(0,0,0,0.6);
  --shadow-lg:            0 12px 40px rgba(0,0,0,0.7);
  --radius-sm: 4px; --radius-md: 8px; --radius-lg: 12px; --radius-xl: 16px; --radius-full: 9999px;
}
```

### deep-ocean
Deep navy, teal accents. Fintech, data platforms, enterprise.
```css
[data-theme="deep-ocean"] {
  --color-primary:        #0ea5e9;
  --color-primary-hover:  #0284c7;
  --color-primary-fg:     #ffffff;
  --color-secondary:      #1e3a5f;
  --color-secondary-hover:#1e4976;
  --color-secondary-fg:   #e0f2fe;
  --color-accent:         #06d6a0;
  --color-accent-hover:   #05b386;
  --color-accent-fg:      #003d2e;
  --color-background:     #030f1e;
  --color-surface:        #071629;
  --color-surface-2:      #0d2035;
  --color-border:         #112b45;
  --color-border-strong:  #1e4976;
  --color-text:           #e2f0ff;
  --color-text-muted:     #7fb3d3;
  --color-text-subtle:    #4a7d9e;
  --color-text-inverse:   #030f1e;
  --color-success:        #10b981;
  --color-warning:        #f59e0b;
  --color-error:          #f43f5e;
  --color-info:           #38bdf8;
  --color-overlay:        rgba(3,15,30,0.8);
  --shadow-sm:            0 1px 3px rgba(0,0,0,0.6);
  --shadow-md:            0 4px 16px rgba(0,0,0,0.7);
  --shadow-lg:            0 12px 40px rgba(0,0,0,0.8);
  --radius-sm: 4px; --radius-md: 8px; --radius-lg: 12px; --radius-xl: 16px; --radius-full: 9999px;
}
```

### neon-void
Pure black, electric purple/pink accents. Crypto, gaming, creative tech.
```css
[data-theme="neon-void"] {
  --color-primary:        #a855f7;
  --color-primary-hover:  #9333ea;
  --color-primary-fg:     #ffffff;
  --color-secondary:      #1f1235;
  --color-secondary-hover:#2a1a4a;
  --color-secondary-fg:   #f0e6ff;
  --color-accent:         #ec4899;
  --color-accent-hover:   #db2777;
  --color-accent-fg:      #ffffff;
  --color-background:     #000000;
  --color-surface:        #0d0d0d;
  --color-surface-2:      #161616;
  --color-border:         #1a0a2e;
  --color-border-strong:  #3b1f6e;
  --color-text:           #f5e6ff;
  --color-text-muted:     #c084fc;
  --color-text-subtle:    #7c3aed;
  --color-text-inverse:   #000000;
  --color-success:        #22c55e;
  --color-warning:        #fbbf24;
  --color-error:          #f43f5e;
  --color-info:           #818cf8;
  --color-overlay:        rgba(0,0,0,0.85);
  --shadow-sm:            0 1px 3px rgba(168,85,247,0.2);
  --shadow-md:            0 4px 16px rgba(168,85,247,0.3);
  --shadow-lg:            0 12px 40px rgba(168,85,247,0.4);
  --radius-sm: 4px; --radius-md: 8px; --radius-lg: 12px; --radius-xl: 16px; --radius-full: 9999px;
}
```

### slate-charcoal
Charcoal grey, cool blue primary. B2B SaaS, project management tools.
```css
[data-theme="slate-charcoal"] {
  --color-primary:        #6366f1;
  --color-primary-hover:  #4f46e5;
  --color-primary-fg:     #ffffff;
  --color-secondary:      #334155;
  --color-secondary-hover:#475569;
  --color-secondary-fg:   #f1f5f9;
  --color-accent:         #22d3ee;
  --color-accent-hover:   #06b6d4;
  --color-accent-fg:      #0c1a20;
  --color-background:     #0f1117;
  --color-surface:        #1a1d27;
  --color-surface-2:      #22263a;
  --color-border:         #2a2d3e;
  --color-border-strong:  #404565;
  --color-text:           #e2e8f0;
  --color-text-muted:     #94a3b8;
  --color-text-subtle:    #64748b;
  --color-text-inverse:   #0f1117;
  --color-success:        #10b981;
  --color-warning:        #f59e0b;
  --color-error:          #ef4444;
  --color-info:           #3b82f6;
  --color-overlay:        rgba(15,17,23,0.8);
  --shadow-sm:            0 1px 3px rgba(0,0,0,0.4);
  --shadow-md:            0 4px 16px rgba(0,0,0,0.5);
  --shadow-lg:            0 12px 40px rgba(0,0,0,0.6);
  --radius-sm: 4px; --radius-md: 8px; --radius-lg: 12px; --radius-xl: 16px; --radius-full: 9999px;
}
```

### forest-dark
Dark greens, earth accents. Sustainability, nature, eco products.
```css
[data-theme="forest-dark"] {
  --color-primary:        #16a34a;
  --color-primary-hover:  #15803d;
  --color-primary-fg:     #ffffff;
  --color-secondary:      #1a2e1c;
  --color-secondary-hover:#223823;
  --color-secondary-fg:   #dcfce7;
  --color-accent:         #84cc16;
  --color-accent-hover:   #65a30d;
  --color-accent-fg:      #1a2500;
  --color-background:     #071209;
  --color-surface:        #0f1f12;
  --color-surface-2:      #162b1a;
  --color-border:         #1e3820;
  --color-border-strong:  #2d5230;
  --color-text:           #dcfce7;
  --color-text-muted:     #86efac;
  --color-text-subtle:    #4ade80;
  --color-text-inverse:   #071209;
  --color-success:        #22c55e;
  --color-warning:        #fbbf24;
  --color-error:          #f43f5e;
  --color-info:           #22d3ee;
  --color-overlay:        rgba(7,18,9,0.8);
  --shadow-sm:            0 1px 3px rgba(0,0,0,0.5);
  --shadow-md:            0 4px 16px rgba(0,0,0,0.6);
  --shadow-lg:            0 12px 40px rgba(0,0,0,0.7);
  --radius-sm: 4px; --radius-md: 8px; --radius-lg: 12px; --radius-xl: 16px; --radius-full: 9999px;
}
```

---

## ☀️ Light Themes

### paper-white
Clean white, deep ink. Editorial, blogs, documentation, minimal SaaS.
```css
[data-theme="paper-white"] {
  --color-primary:        #18181b;
  --color-primary-hover:  #3f3f46;
  --color-primary-fg:     #ffffff;
  --color-secondary:      #f4f4f5;
  --color-secondary-hover:#e4e4e7;
  --color-secondary-fg:   #18181b;
  --color-accent:         #e11d48;
  --color-accent-hover:   #be123c;
  --color-accent-fg:      #ffffff;
  --color-background:     #ffffff;
  --color-surface:        #fafafa;
  --color-surface-2:      #f4f4f5;
  --color-border:         #e4e4e7;
  --color-border-strong:  #a1a1aa;
  --color-text:           #18181b;
  --color-text-muted:     #52525b;
  --color-text-subtle:    #a1a1aa;
  --color-text-inverse:   #ffffff;
  --color-success:        #16a34a;
  --color-warning:        #d97706;
  --color-error:          #dc2626;
  --color-info:           #2563eb;
  --color-overlay:        rgba(0,0,0,0.5);
  --shadow-sm:            0 1px 3px rgba(0,0,0,0.08);
  --shadow-md:            0 4px 16px rgba(0,0,0,0.1);
  --shadow-lg:            0 12px 40px rgba(0,0,0,0.12);
  --radius-sm: 4px; --radius-md: 8px; --radius-lg: 12px; --radius-xl: 16px; --radius-full: 9999px;
}
```

### cloud-blue
Soft white, sky blue primary. Healthcare, productivity, consumer apps.
```css
[data-theme="cloud-blue"] {
  --color-primary:        #2563eb;
  --color-primary-hover:  #1d4ed8;
  --color-primary-fg:     #ffffff;
  --color-secondary:      #eff6ff;
  --color-secondary-hover:#dbeafe;
  --color-secondary-fg:   #1e3a8a;
  --color-accent:         #0ea5e9;
  --color-accent-hover:   #0284c7;
  --color-accent-fg:      #ffffff;
  --color-background:     #f8faff;
  --color-surface:        #ffffff;
  --color-surface-2:      #f0f6ff;
  --color-border:         #e0ecff;
  --color-border-strong:  #bfdbfe;
  --color-text:           #1e293b;
  --color-text-muted:     #475569;
  --color-text-subtle:    #94a3b8;
  --color-text-inverse:   #ffffff;
  --color-success:        #16a34a;
  --color-warning:        #d97706;
  --color-error:          #dc2626;
  --color-info:           #2563eb;
  --color-overlay:        rgba(0,0,0,0.4);
  --shadow-sm:            0 1px 3px rgba(37,99,235,0.08);
  --shadow-md:            0 4px 16px rgba(37,99,235,0.1);
  --shadow-lg:            0 12px 40px rgba(37,99,235,0.15);
  --radius-sm: 4px; --radius-md: 8px; --radius-lg: 12px; --radius-xl: 16px; --radius-full: 9999px;
}
```

### warm-cream
Warm off-white, earthy tones. Lifestyle, food, wellness, boutique brands.
```css
[data-theme="warm-cream"] {
  --color-primary:        #92400e;
  --color-primary-hover:  #78350f;
  --color-primary-fg:     #ffffff;
  --color-secondary:      #fef3c7;
  --color-secondary-hover:#fde68a;
  --color-secondary-fg:   #78350f;
  --color-accent:         #d97706;
  --color-accent-hover:   #b45309;
  --color-accent-fg:      #ffffff;
  --color-background:     #fffbf5;
  --color-surface:        #fefce8;
  --color-surface-2:      #fef9ec;
  --color-border:         #f3e5c8;
  --color-border-strong:  #d6b896;
  --color-text:           #2c1a09;
  --color-text-muted:     #6b4c2a;
  --color-text-subtle:    #a97c50;
  --color-text-inverse:   #fffbf5;
  --color-success:        #15803d;
  --color-warning:        #b45309;
  --color-error:          #b91c1c;
  --color-info:           #0369a1;
  --color-overlay:        rgba(0,0,0,0.4);
  --shadow-sm:            0 1px 3px rgba(92,64,14,0.1);
  --shadow-md:            0 4px 16px rgba(92,64,14,0.12);
  --shadow-lg:            0 12px 40px rgba(92,64,14,0.15);
  --radius-sm: 4px; --radius-md: 8px; --radius-lg: 12px; --radius-xl: 16px; --radius-full: 9999px;
}
```

### rose-petal
Soft white, rose/pink tones. Beauty, fashion, events, wellness.
```css
[data-theme="rose-petal"] {
  --color-primary:        #e11d48;
  --color-primary-hover:  #be123c;
  --color-primary-fg:     #ffffff;
  --color-secondary:      #fff1f2;
  --color-secondary-hover:#ffe4e6;
  --color-secondary-fg:   #881337;
  --color-accent:         #f472b6;
  --color-accent-hover:   #ec4899;
  --color-accent-fg:      #ffffff;
  --color-background:     #fff9fb;
  --color-surface:        #ffffff;
  --color-surface-2:      #fff1f2;
  --color-border:         #ffe4e6;
  --color-border-strong:  #fda4af;
  --color-text:           #1c0a0e;
  --color-text-muted:     #6d2839;
  --color-text-subtle:    #be7187;
  --color-text-inverse:   #ffffff;
  --color-success:        #16a34a;
  --color-warning:        #d97706;
  --color-error:          #dc2626;
  --color-info:           #7c3aed;
  --color-overlay:        rgba(0,0,0,0.4);
  --shadow-sm:            0 1px 3px rgba(225,29,72,0.08);
  --shadow-md:            0 4px 16px rgba(225,29,72,0.1);
  --shadow-lg:            0 12px 40px rgba(225,29,72,0.14);
  --radius-sm: 4px; --radius-md: 8px; --radius-lg: 12px; --radius-xl: 16px; --radius-full: 9999px;
}
```

### mint-fresh
Crisp white, mint/teal primary. Health, fintech, productivity.
```css
[data-theme="mint-fresh"] {
  --color-primary:        #0d9488;
  --color-primary-hover:  #0f766e;
  --color-primary-fg:     #ffffff;
  --color-secondary:      #f0fdfa;
  --color-secondary-hover:#ccfbf1;
  --color-secondary-fg:   #134e4a;
  --color-accent:         #34d399;
  --color-accent-hover:   #10b981;
  --color-accent-fg:      #064e3b;
  --color-background:     #f7fffe;
  --color-surface:        #ffffff;
  --color-surface-2:      #f0fdfa;
  --color-border:         #ccfbf1;
  --color-border-strong:  #99f6e4;
  --color-text:           #042f2e;
  --color-text-muted:     #0f5550;
  --color-text-subtle:    #5eead4;
  --color-text-inverse:   #ffffff;
  --color-success:        #059669;
  --color-warning:        #d97706;
  --color-error:          #dc2626;
  --color-info:           #0284c7;
  --color-overlay:        rgba(0,0,0,0.4);
  --shadow-sm:            0 1px 3px rgba(13,148,136,0.08);
  --shadow-md:            0 4px 16px rgba(13,148,136,0.12);
  --shadow-lg:            0 12px 40px rgba(13,148,136,0.16);
  --radius-sm: 4px; --radius-md: 8px; --radius-lg: 12px; --radius-xl: 16px; --radius-full: 9999px;
}
```

---

## 🔲 Neobrutalist / Bold Themes

### brutal-sun
Stark white, pure black, yellow accent. Neobrutalist SaaS, portfolios, agencies.
```css
[data-theme="brutal-sun"] {
  --color-primary:        #000000;
  --color-primary-hover:  #1a1a1a;
  --color-primary-fg:     #fde047;
  --color-secondary:      #fde047;
  --color-secondary-hover:#facc15;
  --color-secondary-fg:   #000000;
  --color-accent:         #ff6b35;
  --color-accent-hover:   #e85a24;
  --color-accent-fg:      #000000;
  --color-background:     #ffffff;
  --color-surface:        #fafafa;
  --color-surface-2:      #f0f0f0;
  --color-border:         #000000;
  --color-border-strong:  #000000;
  --color-text:           #000000;
  --color-text-muted:     #333333;
  --color-text-subtle:    #666666;
  --color-text-inverse:   #ffffff;
  --color-success:        #16a34a;
  --color-warning:        #d97706;
  --color-error:          #dc2626;
  --color-info:           #2563eb;
  --color-overlay:        rgba(0,0,0,0.6);
  --shadow-sm:            2px 2px 0px #000;
  --shadow-md:            4px 4px 0px #000;
  --shadow-lg:            8px 8px 0px #000;
  --radius-sm: 0px; --radius-md: 0px; --radius-lg: 2px; --radius-xl: 4px; --radius-full: 9999px;
}
```

### brutal-electric
White, electric blue, lime. High-energy agencies, startups, product launches.
```css
[data-theme="brutal-electric"] {
  --color-primary:        #2563eb;
  --color-primary-hover:  #1d4ed8;
  --color-primary-fg:     #ffffff;
  --color-secondary:      #a3e635;
  --color-secondary-hover:#84cc16;
  --color-secondary-fg:   #000000;
  --color-accent:         #f43f5e;
  --color-accent-hover:   #e11d48;
  --color-accent-fg:      #ffffff;
  --color-background:     #ffffff;
  --color-surface:        #f8fafc;
  --color-surface-2:      #eff6ff;
  --color-border:         #000000;
  --color-border-strong:  #000000;
  --color-text:           #000000;
  --color-text-muted:     #1e3a8a;
  --color-text-subtle:    #3b82f6;
  --color-text-inverse:   #ffffff;
  --color-success:        #16a34a;
  --color-warning:        #d97706;
  --color-error:          #dc2626;
  --color-info:           #2563eb;
  --color-overlay:        rgba(0,0,0,0.6);
  --shadow-sm:            3px 3px 0px #000;
  --shadow-md:            5px 5px 0px #000;
  --shadow-lg:            8px 8px 0px #000;
  --radius-sm: 0px; --radius-md: 2px; --radius-lg: 4px; --radius-xl: 6px; --radius-full: 9999px;
}
```

---

## 🌅 Mid-Range / Tonal Themes

### lavender-dusk
Light lavender bg, deep violet primary. Creative tools, design platforms, AI products.
```css
[data-theme="lavender-dusk"] {
  --color-primary:        #7c3aed;
  --color-primary-hover:  #6d28d9;
  --color-primary-fg:     #ffffff;
  --color-secondary:      #ede9fe;
  --color-secondary-hover:#ddd6fe;
  --color-secondary-fg:   #4c1d95;
  --color-accent:         #f0abfc;
  --color-accent-hover:   #e879f9;
  --color-accent-fg:      #3b0764;
  --color-background:     #f5f3ff;
  --color-surface:        #ffffff;
  --color-surface-2:      #ede9fe;
  --color-border:         #ddd6fe;
  --color-border-strong:  #a78bfa;
  --color-text:           #1e0042;
  --color-text-muted:     #5b21b6;
  --color-text-subtle:    #8b5cf6;
  --color-text-inverse:   #ffffff;
  --color-success:        #16a34a;
  --color-warning:        #d97706;
  --color-error:          #dc2626;
  --color-info:           #7c3aed;
  --color-overlay:        rgba(30,0,66,0.4);
  --shadow-sm:            0 1px 3px rgba(124,58,237,0.1);
  --shadow-md:            0 4px 16px rgba(124,58,237,0.15);
  --shadow-lg:            0 12px 40px rgba(124,58,237,0.2);
  --radius-sm: 4px; --radius-md: 8px; --radius-lg: 14px; --radius-xl: 20px; --radius-full: 9999px;
}
```

### slate-sage
Warm grey background, sage green primary. Consulting, professional services, agencies.
```css
[data-theme="slate-sage"] {
  --color-primary:        #4d7c5f;
  --color-primary-hover:  #3d6450;
  --color-primary-fg:     #ffffff;
  --color-secondary:      #ecf0ec;
  --color-secondary-hover:#d8e5d8;
  --color-secondary-fg:   #1a3024;
  --color-accent:         #a3c4a8;
  --color-accent-hover:   #86af8d;
  --color-accent-fg:      #0f2016;
  --color-background:     #f5f5f0;
  --color-surface:        #ffffff;
  --color-surface-2:      #ecf0ec;
  --color-border:         #d8e0d8;
  --color-border-strong:  #a0b4a0;
  --color-text:           #1a2a1e;
  --color-text-muted:     #3d5a43;
  --color-text-subtle:    #7a9e82;
  --color-text-inverse:   #ffffff;
  --color-success:        #16a34a;
  --color-warning:        #d97706;
  --color-error:          #dc2626;
  --color-info:           #2563eb;
  --color-overlay:        rgba(0,0,0,0.4);
  --shadow-sm:            0 1px 3px rgba(77,124,95,0.08);
  --shadow-md:            0 4px 16px rgba(77,124,95,0.1);
  --shadow-lg:            0 12px 40px rgba(77,124,95,0.14);
  --radius-sm: 4px; --radius-md: 8px; --radius-lg: 12px; --radius-xl: 16px; --radius-full: 9999px;
}
```

### sunset-coral
Warm white, coral/orange primary. E-commerce, food, energetic consumer brands.
```css
[data-theme="sunset-coral"] {
  --color-primary:        #f24f3b;
  --color-primary-hover:  #dc3626;
  --color-primary-fg:     #ffffff;
  --color-secondary:      #fff4f2;
  --color-secondary-hover:#ffe8e5;
  --color-secondary-fg:   #7f1d0e;
  --color-accent:         #fb923c;
  --color-accent-hover:   #f97316;
  --color-accent-fg:      #431407;
  --color-background:     #fffaf9;
  --color-surface:        #ffffff;
  --color-surface-2:      #fff4f2;
  --color-border:         #ffe0db;
  --color-border-strong:  #fca49d;
  --color-text:           #1c0a08;
  --color-text-muted:     #7f2d1e;
  --color-text-subtle:    #c1604e;
  --color-text-inverse:   #ffffff;
  --color-success:        #16a34a;
  --color-warning:        #d97706;
  --color-error:          #dc2626;
  --color-info:           #2563eb;
  --color-overlay:        rgba(0,0,0,0.4);
  --shadow-sm:            0 1px 3px rgba(242,79,59,0.1);
  --shadow-md:            0 4px 16px rgba(242,79,59,0.12);
  --shadow-lg:            0 12px 40px rgba(242,79,59,0.16);
  --radius-sm: 4px; --radius-md: 8px; --radius-lg: 12px; --radius-xl: 16px; --radius-full: 9999px;
}
```

---

## 🪟 Glassmorphism Themes

### glass-aurora
Dark navy base, frosted glass cards, aurora gradient accents.
```css
[data-theme="glass-aurora"] {
  --color-primary:        #8b5cf6;
  --color-primary-hover:  #7c3aed;
  --color-primary-fg:     #ffffff;
  --color-secondary:      rgba(139,92,246,0.15);
  --color-secondary-hover:rgba(139,92,246,0.25);
  --color-secondary-fg:   #e9d5ff;
  --color-accent:         #06b6d4;
  --color-accent-hover:   #0891b2;
  --color-accent-fg:      #ffffff;
  --color-background:     #08051a;
  --color-surface:        rgba(255,255,255,0.05);
  --color-surface-2:      rgba(255,255,255,0.08);
  --color-border:         rgba(255,255,255,0.08);
  --color-border-strong:  rgba(255,255,255,0.16);
  --color-text:           #f1e8ff;
  --color-text-muted:     #a78bfa;
  --color-text-subtle:    #6d28d9;
  --color-text-inverse:   #000000;
  --color-success:        #22c55e;
  --color-warning:        #fbbf24;
  --color-error:          #f43f5e;
  --color-info:           #38bdf8;
  --color-overlay:        rgba(8,5,26,0.8);
  --shadow-sm:            0 2px 8px rgba(139,92,246,0.2);
  --shadow-md:            0 8px 24px rgba(139,92,246,0.25);
  --shadow-lg:            0 20px 60px rgba(139,92,246,0.3);
  --radius-sm: 8px; --radius-md: 12px; --radius-lg: 16px; --radius-xl: 24px; --radius-full: 9999px;
}
/* Glass card mixin — apply manually: backdrop-filter: blur(12px); border: 1px solid var(--color-border) */
```

---

## 📋 Theme Selection Guide

| Project Type | Recommended Theme |
|-------------|------------------|
| SaaS / Dev Tool | `midnight-ember`, `slate-charcoal` |
| Fintech / Enterprise | `deep-ocean`, `cloud-blue` |
| Crypto / Gaming | `neon-void`, `glass-aurora` |
| Healthcare / Productivity | `mint-fresh`, `cloud-blue` |
| Agency / Portfolio | `brutal-sun`, `brutal-electric`, `paper-white` |
| E-commerce / Consumer | `sunset-coral`, `warm-cream` |
| Beauty / Fashion | `rose-petal`, `lavender-dusk` |
| Eco / Sustainability | `forest-dark`, `slate-sage` |
| AI / Creative Tool | `lavender-dusk`, `neon-void` |
| Consulting / Professional | `slate-sage`, `paper-white` |

---

## 🏭 Theme Factory — Creating Custom Themes

If no preset matches, create a new theme following this checklist:
1. Start with a **base background** — decide if light, dark, or tinted
2. Pick **primary** = main call-to-action color (high contrast against bg)
3. Pick **accent** = decorative pop, should complement primary (not compete)
4. Derive **surface** = background + 5–8% lighter/darker
5. Derive **text** = highest possible contrast against background (WCAG AA min)
6. Derive **text-muted** = ~50% luminance between text and background
7. Set **border** = background + 12–15% shift
8. Shadows: dark themes use rgba(0,0,0,…), light themes match primary hue at low opacity
9. Neobrutalist themes: set `--radius-sm/md/lg/xl` to 0 or near-0 and `--shadow-*` to flat offset shadows