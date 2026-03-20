---
name: frontend-fonts
description: Google Fonts catalog for frontend projects. Contains 14 curated display+body+mono pairings with @import strings, Tailwind config entries, and a theme-to-font quick reference matrix. Use when selecting and applying typography to a frontend project.
---

# Fonts Reference

All fonts are loaded via Google Fonts `@import`. Each font pairing includes:
- **Display font** — headlines, hero, section titles (text-4xl and above)
- **Body font** — paragraphs, descriptions, UI text (text-base to text-3xl)
- **Mono font** — code, tags, labels (always use one of the mono options below)

---

## Usage Pattern

```css
/* globals.css — always place @import at the very top */
@import url('https://fonts.googleapis.com/css2?family=DISPLAY_FONT:wght@400;600;700;800&family=BODY_FONT:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
  --font-display: 'DISPLAY_FONT', sans-serif;
  --font-body:    'BODY_FONT', sans-serif;
  --font-mono:    'JetBrains Mono', monospace;
}
```

```tsx
// tailwind.config.ts
fontFamily: {
  display: ['var(--font-display)'],
  body:    ['var(--font-body)'],
  mono:    ['var(--font-mono)'],
}
```

---

## Font Pairings Catalog

### Pairing 01 — Editorial Authority
**Display**: Playfair Display | **Body**: Lato  
Character: Refined, trustworthy, editorial  
Best for: `paper-white`, `warm-cream`, `slate-sage`

```css
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700;800&family=Lato:wght@300;400;700&family=JetBrains+Mono:wght@400&display=swap');
--font-display: 'Playfair Display', serif;
--font-body:    'Lato', sans-serif;
```

---

### Pairing 02 — Modern Geometric
**Display**: Syne | **Body**: DM Sans  
Character: Contemporary, confident, tech-forward  
Best for: `midnight-ember`, `slate-charcoal`, `neon-void`

```css
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');
--font-display: 'Syne', sans-serif;
--font-body:    'DM Sans', sans-serif;
```

---

### Pairing 03 — Swiss Precision
**Display**: Barlow Condensed | **Body**: Barlow  
Character: Technical, systematic, clean  
Best for: `brutal-sun`, `brutal-electric`, `cloud-blue`

```css
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700;800&family=Barlow:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');
--font-display: 'Barlow Condensed', sans-serif;
--font-body:    'Barlow', sans-serif;
```

---

### Pairing 04 — Luxury Serif
**Display**: Cormorant Garamond | **Body**: Nunito  
Character: Elegant, luxurious, sophisticated  
Best for: `rose-petal`, `lavender-dusk`, `warm-cream`

```css
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500;600;700&family=Nunito:wght@300;400;500;600&family=JetBrains+Mono:wght@400&display=swap');
--font-display: 'Cormorant Garamond', serif;
--font-body:    'Nunito', sans-serif;
```

---

### Pairing 05 — Brutalist Impact
**Display**: Bebas Neue | **Body**: IBM Plex Sans  
Character: Raw, powerful, unapologetic  
Best for: `brutal-sun`, `brutal-electric`, `midnight-ember`

```css
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=IBM+Plex+Sans:wght@300;400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap');
--font-display: 'Bebas Neue', sans-serif;
--font-body:    'IBM Plex Sans', sans-serif;
--font-mono:    'IBM Plex Mono', monospace;
```

---

### Pairing 06 — Organic Warmth
**Display**: Fraunces | **Body**: Source Sans 3  
Character: Warm, human, approachable  
Best for: `warm-cream`, `forest-dark`, `mint-fresh`

```css
@import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,wght@0,400;0,600;0,700;1,400&family=Source+Sans+3:wght@300;400;600&family=JetBrains+Mono:wght@400&display=swap');
--font-display: 'Fraunces', serif;
--font-body:    'Source Sans 3', sans-serif;
```

---

### Pairing 07 — Futuristic Tech
**Display**: Orbitron | **Body**: Exo 2  
Character: Sci-fi, futuristic, gaming, crypto  
Best for: `neon-void`, `deep-ocean`, `glass-aurora`

```css
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;700;900&family=Exo+2:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');
--font-display: 'Orbitron', sans-serif;
--font-body:    'Exo 2', sans-serif;
```

---

### Pairing 08 — Contemporary Neutral
**Display**: Plus Jakarta Sans | **Body**: Mulish  
Character: Versatile, professional, friendly SaaS  
Best for: `cloud-blue`, `slate-charcoal`, `lavender-dusk`

```css
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Mulish:wght@300;400;500;600&family=JetBrains+Mono:wght@400&display=swap');
--font-display: 'Plus Jakarta Sans', sans-serif;
--font-body:    'Mulish', sans-serif;
```

---

### Pairing 09 — High-Fashion
**Display**: Big Shoulders Display | **Body**: Work Sans  
Character: Bold, fashion-forward, editorial  
Best for: `rose-petal`, `brutal-electric`, `paper-white`

```css
@import url('https://fonts.googleapis.com/css2?family=Big+Shoulders+Display:wght@500;700;900&family=Work+Sans:wght@300;400;500;600&family=JetBrains+Mono:wght@400&display=swap');
--font-display: 'Big Shoulders Display', sans-serif;
--font-body:    'Work Sans', sans-serif;
```

---

### Pairing 10 — Startup Energy
**Display**: Clash Display | **Body**: Satoshi  
⚠️ These are premium fonts — use fallbacks: Outfit (Display) + Figtree (Body) as Google Fonts alternatives

```css
/* Google Fonts alternative for Startup Energy */
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700;800&family=Figtree:wght@300;400;500;600&family=JetBrains+Mono:wght@400&display=swap');
--font-display: 'Outfit', sans-serif;
--font-body:    'Figtree', sans-serif;
```

---

### Pairing 11 — Medical / Trust
**Display**: Libre Baskerville | **Body**: Open Sans  
Character: Authoritative, trustworthy, clinical clarity  
Best for: `cloud-blue`, `mint-fresh`, `paper-white`

```css
@import url('https://fonts.googleapis.com/css2?family=Libre+Baskerville:wght@400;700&family=Open+Sans:wght@300;400;600&family=JetBrains+Mono:wght@400&display=swap');
--font-display: 'Libre Baskerville', serif;
--font-body:    'Open Sans', sans-serif;
```

---

### Pairing 12 — Creative Studio
**Display**: Abril Fatface | **Body**: Karla  
Character: Expressive, creative, agency-like  
Best for: `sunset-coral`, `rose-petal`, `brutal-sun`

```css
@import url('https://fonts.googleapis.com/css2?family=Abril+Fatface&family=Karla:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400&display=swap');
--font-display: 'Abril Fatface', serif;
--font-body:    'Karla', sans-serif;
```

---

### Pairing 13 — Clean Corporate
**Display**: Raleway | **Body**: Roboto  
Character: Professional, safe, widely accessible  
Best for: `slate-sage`, `cloud-blue`, any enterprise project

```css
@import url('https://fonts.googleapis.com/css2?family=Raleway:wght@400;500;600;700;800&family=Roboto:wght@300;400;500&family=Roboto+Mono:wght@400&display=swap');
--font-display: 'Raleway', sans-serif;
--font-body:    'Roboto', sans-serif;
--font-mono:    'Roboto Mono', monospace;
```

---

### Pairing 14 — Nature & Wellness
**Display**: Josefin Sans | **Body**: Hind  
Character: Earthy, calm, wellness-forward  
Best for: `forest-dark`, `mint-fresh`, `warm-cream`

```css
@import url('https://fonts.googleapis.com/css2?family=Josefin+Sans:wght@300;400;600;700&family=Hind:wght@300;400;500;600&family=JetBrains+Mono:wght@400&display=swap');
--font-display: 'Josefin Sans', sans-serif;
--font-body:    'Hind', sans-serif;
```

---

## Mono Fonts Reference

Always pick one for `--font-mono`:

| Font | Import |
|------|--------|
| JetBrains Mono | `family=JetBrains+Mono:wght@400;500` |
| IBM Plex Mono | `family=IBM+Plex+Mono:wght@400;500` |
| Roboto Mono | `family=Roboto+Mono:wght@400` |
| Fira Code | `family=Fira+Code:wght@400;500` |
| Source Code Pro | `family=Source+Code+Pro:wght@400;500` |

---

## Theme → Font Pairing Quick Reference

| Theme | Recommended Pairing |
|-------|-------------------|
| `midnight-ember` | Pairing 02 (Syne / DM Sans) |
| `deep-ocean` | Pairing 08 (Plus Jakarta Sans / Mulish) |
| `neon-void` | Pairing 07 (Orbitron / Exo 2) |
| `slate-charcoal` | Pairing 02 or 08 |
| `forest-dark` | Pairing 06 (Fraunces / Source Sans 3) |
| `paper-white` | Pairing 01 (Playfair Display / Lato) |
| `cloud-blue` | Pairing 08 or 11 |
| `warm-cream` | Pairing 06 or 01 |
| `rose-petal` | Pairing 04 (Cormorant / Nunito) |
| `mint-fresh` | Pairing 14 (Josefin Sans / Hind) |
| `brutal-sun` | Pairing 05 (Bebas Neue / IBM Plex) |
| `brutal-electric` | Pairing 03 (Barlow Condensed / Barlow) |
| `lavender-dusk` | Pairing 04 or 08 |
| `slate-sage` | Pairing 01 or 13 |
| `sunset-coral` | Pairing 12 (Abril Fatface / Karla) |
| `glass-aurora` | Pairing 07 or 02 |