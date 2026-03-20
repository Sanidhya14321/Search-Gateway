---
name: frontend
description: Build complete production-ready frontends — website, web app, SaaS, landing page, dashboard, React app. Generates all pages (Homepage, About, Services, Contact, Login, Signup) plus Navbar and Footer with a full design system, theme, and typography.
---

# Frontend Skill

Creates complete, modern, production-grade frontends. Every project gets all required
pages, a design system, theme, and professional typography — not just a single component.

---

## Step 0 — Read Reference Files First

Before writing any code, load the files relevant to the project:

| File | When to Read |
|------|-------------|
| `themes.md` | Always — pick the right theme for the project |
| `fonts.md` | Always — pair fonts to the chosen theme |
| `design-styles.md` | Always — choose a design style direction |
| `templates.md` | Always — use as structural scaffolding for each page |
| `mistakes.md` | Always — check before finalizing code |

---

## Step 1 — Understand the Project

Extract from the user's prompt:
- **Product/Service name** and what it does
- **Number of services/features** (determines services page card count — always dynamic)
- **Target audience** (consumer, B2B, developer, creative, etc.)
- **Tone** (professional, playful, minimal, bold, editorial)
- **Color preferences** (if any — otherwise pick from `themes.md`)

If any of the above are missing and the user hasn't explicitly said to proceed, ask ONE concise question to clarify the most important gap.

---

## Step 2 — Choose Design Direction

From `design-styles.md`, pick **one primary design style** that fits the product.  
Then from `themes.md`, pick **one theme** (or compose a new one using the theme factory rules).  
Then from `fonts.md`, assign a **font pairing** to the theme.

Document the choices as a comment block at the top of the main CSS/config file:
```
/* 
  Design Style: Neobrutalism
  Theme: midnight-ember
  Fonts: Display → Syne | Body → DM Sans
*/
```

---

## Step 3 — Project Structure

Always scaffold in this structure (React + Vite + TailwindCSS + shadcn/ui):

```
src/
├── components/
│   ├── layout/
│   │   ├── Navbar.tsx
│   │   └── Footer.tsx
│   ├── ui/           ← shadcn primitives (Button, Card, Input, etc.)
│   └── sections/     ← reusable section components
├── pages/
│   ├── HomePage.tsx
│   ├── AboutPage.tsx
│   ├── ServicesPage.tsx
│   ├── ContactPage.tsx
│   ├── LoginPage.tsx
│   └── SignupPage.tsx
├── lib/
│   ├── theme.ts      ← CSS variable tokens + theme export
│   └── utils.ts      ← cn(), formatters, helpers
├── styles/
│   └── globals.css   ← CSS variables, font imports, resets
└── App.tsx           ← Router setup
```

---

## Step 4 — Typography System (FIXED — Never Deviate)

Apply this type scale consistently everywhere. Import fonts from `fonts.md`.

```css
/* --- TYPE SCALE (rem-based, constant throughout app) --- */
--text-xs:   0.75rem;   /* 12px — captions, labels */
--text-sm:   0.875rem;  /* 14px — secondary body, nav links */
--text-base: 1rem;      /* 16px — primary body copy */
--text-lg:   1.125rem;  /* 18px — lead paragraphs */
--text-xl:   1.25rem;   /* 20px — card titles */
--text-2xl:  1.5rem;    /* 24px — section subtitles */
--text-3xl:  1.875rem;  /* 30px — section titles */
--text-4xl:  2.25rem;   /* 36px — page titles */
--text-5xl:  3rem;      /* 48px — hero subtitles */
--text-6xl:  3.75rem;   /* 60px — hero headlines */
--text-7xl:  4.5rem;    /* 72px — display / oversized hero */

/* --- LINE HEIGHTS --- */
--leading-tight:  1.2;
--leading-snug:   1.375;
--leading-normal: 1.5;
--leading-relaxed:1.625;

/* --- LETTER SPACING --- */
--tracking-tight:  -0.02em;
--tracking-normal:  0em;
--tracking-wide:    0.05em;
--tracking-widest:  0.1em;
```

**Rule**: Never use raw pixel font sizes. Always use CSS variables or Tailwind's `text-` scale mapped to these values.

---

## Step 5 — Required Pages & Their Anatomy

Use `templates.md` for full structural templates. This is the summary contract:

### 🏠 HomePage (Hero Page)
- **Hero**: Full-viewport section — headline (text-6xl/7xl), subheadline, CTA button(s), hero visual
- **Social Proof Strip**: Logos / stats / trust badges
- **Features Overview**: 3–6 cards/items (icon + title + description)
- **How It Works**: 3-step process section
- **Testimonials**: At least 2–3 testimonial cards
- **Final CTA**: Conversion-focused banner + button
- Footer teaser or direct footer

### 👤 AboutPage
- **Hero**: Page title + brand story paragraph
- **Mission / Vision**: Two-column with icon accents
- **Team Section**: Grid of team members (placeholder-ready)
- **Values**: 4-item icon grid
- **Timeline**: Milestones (optional, include if product has history)

### ⚙️ ServicesPage (Dynamic)
- Read number of services from user input
- **Hero**: Short headline + description
- **Services Grid**: Cards rendered from a `services[]` array — always data-driven, never hardcoded in JSX
- Each card: icon, title, short description, optional "Learn More" link
- **Why Us**: Differentiator section below the grid
- **CTA**: "Get Started" or "Contact Us" banner

### 📬 ContactPage
- **Two-column layout**: Form (left) + Contact Info panel (right)
- Form fields: Name, Email, Subject, Message, Submit button
- Use shadcn `Input`, `Textarea`, `Button`, `Label`
- Contact panel: address, email, phone, social links
- Optional: embedded map placeholder

### 🔐 LoginPage
- Centered card layout (max-w-md)
- Logo + headline
- Email + Password fields
- "Forgot password?" link
- Submit button (full-width, primary)
- Divider + OAuth buttons (Google, GitHub optional)
- "Don't have an account? Sign up" link

### 📝 SignupPage
- Same card layout as Login
- Name + Email + Password + Confirm Password
- Terms & conditions checkbox (shadcn Checkbox)
- Submit button
- "Already have an account? Log in" link

### 🧭 Navbar
- Logo (left) + Nav links (center/right) + CTA button (right)
- Mobile: hamburger → slide-in drawer (shadcn Sheet)
- Sticky with subtle backdrop-blur on scroll
- Active link indicator using route match

### 🦶 Footer
- 4-column grid: Brand + Links col 1 + Links col 2 + Newsletter/Social
- Bottom bar: © + privacy + terms links
- Dark background variant (even on light themes)

---

## Step 6 — Component Sources

> **Always read `components.md` before choosing or building any component.**

**Quick priority order:**

| Priority | Source | When |
|---------|--------|------|
| 1 | **21st.dev SDK fetch** | Premium sections — hero, pricing, features, CTA. Fetch `https://21st.dev/agents/llms.txt` first, then the specific component doc via `/agents/docs/md/[name]` |
| 2 | **shadcn/ui CLI** | Standard primitives — Button, Card, Input, Sheet, Dialog, Tabs, etc. `npx shadcn@latest add [component]` |
| 3 | **ReactBits patterns** | Interactive effects — Typewriter, Tilt card, Spotlight hover, Grid background |
| 4 | **Magic UI / Aceternity patterns** | Hero wow-factor — Aurora bg, Grain overlay, Border beam, 3D flip card |
| 5 | **Radix UI** | Headless accessible primitives when shadcn doesn't cover it |
| 6 | **Custom** | Built from scratch using design tokens only — last resort |

**21st SDK fetch — always follow this protocol:**
```
1. fetch https://21st.dev/agents/llms.txt            ← entry point, find component links
2. Convert doc URL: /agents/docs/X → /agents/docs/md/X   ← always use md/ path
3. fetch that URL                                    ← get full component source
4. Adapt: hardcoded colors → var(--color-*) tokens
          hardcoded fonts  → var(--font-*) tokens
          hardcoded radius → var(--radius-*) tokens
```

See `components.md` for full patterns, replication recipes, and the component × page mapping table.

---

## Step 7 — Animation & Motion

> **Always read `animations.md` before writing any animation code.**
> It contains the full playbook — copy-ready patterns for every page and interaction.

Two-library system. Install both:
```bash
npm install framer-motion gsap @gsap/react
```

**Rule — use the right tool:**

| Framer Motion | GSAP |
|--------------|------|
| Page transitions (`AnimatePresence`) | Word-by-word headline splits |
| Hero stagger sequences | ScrollTrigger parallax + pinning |
| `whileInView` scroll reveals | Animated number counters |
| Hover / tap micro-interactions | SVG path drawing |
| `layoutId` nav indicator | Magnetic button effect |
| Stagger grids | Large coordinated timelines |

**Page → animation mapping (quick ref):**

| Page | Key animations |
|------|---------------|
| All pages | Page transition (#1 in animations.md), scroll progress bar (#15) |
| Navbar | Slide-down entrance + `layoutId` active indicator (#7) |
| Hero | Orchestrated stagger (#2), word reveal (#3), SVG underline (#11), magnetic CTA (#9) |
| Features / Services | Stagger grid (#5), card hover lift (#8) |
| Stats / Social Proof | Animated counters (#6), logo marquee (#12) |
| About | Parallax bg layers (#10), counters (#6) |
| Contact / Auth | Animated floating labels (#14) |
| FAQ | Accordion expand/collapse (#13) |

**Non-negotiable rules:**
- Only animate `transform` and `opacity` — never `width`, `height`, `margin`, `top`
- Always `viewport={{ once: true }}` on `whileInView`
- Always clean up GSAP with `ctx.revert()` in `useEffect` return
- Always honor `prefers-reduced-motion` — see animations.md for the pattern

---

## Step 8 — Responsive Rules

| Breakpoint | Behavior |
|-----------|----------|
| `sm` 640px | Single column, stack everything |
| `md` 768px | Two-column layouts appear |
| `lg` 1024px | Full layout, navbar links visible |
| `xl` 1280px | Max content width kicks in |

- **Max content width**: `max-w-7xl mx-auto px-4 sm:px-6 lg:px-8`
- **Hero text**: clamp from text-4xl (mobile) → text-7xl (desktop)
- **Grid**: always `grid-cols-1 sm:grid-cols-2 lg:grid-cols-3`

---

## Step 9 — Final Checklist Before Delivering

Before presenting code, verify against `mistakes.md`. Also check:

- [ ] All 8 pages/components are created (Home, About, Services, Contact, Login, Signup, Navbar, Footer)
- [ ] CSS variables for theme tokens are defined in `globals.css`
- [ ] Font imports added to `globals.css` via Google Fonts `@import`
- [ ] Services page uses a data array (not hardcoded JSX)
- [ ] Navbar has mobile responsive drawer
- [ ] No raw color hex codes in JSX — only CSS variables or Tailwind tokens
- [ ] No raw pixel font sizes — only the type scale variables
- [ ] All shadcn components imported correctly
- [ ] Router configured in `App.tsx` with all routes
- [ ] Design style + theme + font pairing commented at top of `globals.css`
- [ ] `AnimatePresence` wraps `<Routes>` for page transitions
- [ ] `framer-motion` and `gsap` both installed
- [ ] Hero has orchestrated stagger sequence (not just a single fade)
- [ ] `viewport={{ once: true }}` on every `whileInView`
- [ ] GSAP `ctx.revert()` cleanup in every `useEffect` that uses GSAP
- [ ] `prefers-reduced-motion` handled in `globals.css`
- [ ] Cross-check all items in the Mistakes Log (`mistakes.md`)

---

## Reference Files

- **`components.md`** — Component sourcing playbook: 21st SDK fetch protocol, shadcn catalogue, ReactBits/Magic UI/Aceternity patterns, decision tree, component × page mapping
- **`animations.md`** — Full animation playbook: 15 ready-to-use patterns for Framer Motion + GSAP
- **`themes.md`** — Full theme factory: 17 predefined themes with color tokens
- **`fonts.md`** — Google Fonts catalog with theme pairings and `@import` strings
- **`templates.md`** — Full JSX/TSX scaffolds for every required page
- **`design-styles.md`** — Visual style catalog: Minimalism, Brutalism, Neobrutalism, Swiss, Editorial, etc.
- **`mistakes.md`** — Known failure patterns to actively avoid