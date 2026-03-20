---
name: frontend-design-styles
description: Catalog of 13 web design styles — Minimalism, Brutalism, Neobrutalism, Swiss/International, Editorial, Glassmorphism, Neumorphism, Material, Constructivism, Skeuomorphism, Maximalism, Hand-drawn, Dark Premium. Each includes visual hallmarks, CSS patterns, reference brands, and a project-type matrix.
---

# Design Styles Catalog

Reference for all major web design styles. Use this to pick the design direction in Step 2 of SKILL.md.
For each project, commit to **one primary style** and optionally blend with a **secondary style**.

---

## 1. Minimalism

**Core philosophy**: Remove everything that doesn't serve a purpose. Every element earns its place.

**Visual hallmarks**:
- Generous white space (padding/margin much larger than typical)
- Monochromatic or 2-color palette
- Single typeface family (vary weight, not face)
- No decorative elements — borders, dividers, shadows only when functional
- Typography carries the design (size contrast, weight contrast)
- Grid-strict, highly ordered layouts

**CSS patterns**:
```css
/* Huge section padding */
padding: 120px 0;
/* Ultra-thin borders only */
border: 1px solid rgba(0,0,0,0.06);
/* No decorative shadows */
/* Generous letter-spacing on labels */
letter-spacing: 0.12em; text-transform: uppercase;
```

**Best themes**: `paper-white`, `warm-cream`, `slate-sage`  
**Best fonts**: Pairings 01, 08, 13  
**Reference brands**: Apple, Muji, Stripe (early), Linear

---

## 2. Brutalism

**Core philosophy**: Expose the raw structure. Nothing is hidden or prettified.

**Visual hallmarks**:
- Strong black borders on everything (1–3px solid black)
- Pure black text on white — or inverted
- No border radius (or near-zero)
- Oversized, confrontational typography
- Elements feel like they're placed with a ruler and no padding
- Intentional "unfinished" or "no-design" aesthetic

**CSS patterns**:
```css
border: 2px solid #000;
border-radius: 0;
box-shadow: none;
background: #fff;
color: #000;
font-weight: 900;
```

**Best themes**: `brutal-sun`, `paper-white` (modified)  
**Best fonts**: Pairing 05 (Bebas Neue), Pairing 03 (Barlow Condensed)  
**Reference brands**: Bloomberg Businessweek, Balenciaga (web), early Craigslist as anti-aesthetic

---

## 3. Neobrutalism

**Core philosophy**: Brutalism's structure meets playful color and offset shadows.

**Visual hallmarks**:
- Hard offset drop shadows (4px 4px 0 #000 or color)
- Bold border outlines
- Flat, punchy fill colors (yellow, electric blue, lime, coral)
- Near-zero border radius
- Large, bold sans-serif type
- Overlapping or stacked layout elements

**CSS patterns**:
```css
border: 2px solid #000;
border-radius: 4px;
box-shadow: 4px 4px 0px #000;
transition: transform 0.1s, box-shadow 0.1s;
/* Hover lift: */
&:hover { transform: translate(-2px,-2px); box-shadow: 6px 6px 0px #000; }
```

**Best themes**: `brutal-sun`, `brutal-electric`  
**Best fonts**: Pairing 05, Pairing 09 (Big Shoulders Display)  
**Reference brands**: Figma (some elements), Gumroad, Monzo (cards)

---

## 4. Swiss / International Style

**Core philosophy**: Grid systems, mathematical spacing, objectivity through order.

**Visual hallmarks**:
- Strict grid — always snapped, always aligned
- Asymmetric but balanced layouts
- Strong typographic hierarchy (weight + size, not decoration)
- Red, black, white palette OR very restrained color
- Flush-left text (ragged right)
- Photography used as a grid element, not decoration

**CSS patterns**:
```css
/* CSS Grid with explicit columns */
grid-template-columns: repeat(12, 1fr);
/* Consistent baseline rhythm */
line-height: 1.5;
/* Thin, precise dividers */
border-top: 1px solid currentColor;
/* Color as accent only */
```

**Best themes**: `paper-white`, `brutal-sun`  
**Best fonts**: Pairing 03 (Barlow), Pairing 08, Pairing 13  
**Reference brands**: Swiss Airlines, Helvetica-era print, Braun products

---

## 5. Editorial Style

**Core philosophy**: Borrow from magazine/newspaper layout. Content is king, layout creates drama.

**Visual hallmarks**:
- Variable column spans (hero content bleeds, body is columnar)
- Pull quotes at oversized scale (text-5xl+)
- Large numbering and drop caps
- Mixed serif (headline) + sans-serif (body) with clear editorial contrast
- Black-and-white photography with single-color accents
- Horizontal rules, section numbering
- Datelines, category labels, bylines as design elements

**CSS patterns**:
```css
/* Pull quote */
font-size: var(--text-5xl);
font-style: italic;
border-left: 4px solid var(--color-accent);
padding-left: 2rem;
/* Section label */
text-transform: uppercase;
letter-spacing: 0.15em;
font-size: var(--text-xs);
font-weight: 700;
```

**Best themes**: `paper-white`, `warm-cream`, `midnight-ember`  
**Best fonts**: Pairing 01 (Playfair + Lato), Pairing 06, Pairing 12  
**Reference brands**: The New Yorker, NYT, Monocle, Kinfolk magazine

---

## 6. Glassmorphism

**Core philosophy**: Depth and translucency. Elements feel like frosted glass layers.

**Visual hallmarks**:
- `backdrop-filter: blur()` on cards/panels
- Semi-transparent backgrounds: `rgba(255,255,255,0.08)` on dark themes
- Subtle gradient borders: `border: 1px solid rgba(255,255,255,0.15)`
- Dark, gradient-rich backgrounds (purple nebula, aurora, deep navy)
- Glowing accent colors with diffuse shadows
- Rounded corners (radius-lg to radius-xl)

**CSS patterns**:
```css
.glass-card {
  background: rgba(255,255,255,0.06);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255,255,255,0.12);
  border-radius: var(--radius-xl);
  box-shadow: 0 8px 32px rgba(0,0,0,0.3);
}
```

**Best themes**: `glass-aurora`, `neon-void`, `deep-ocean`  
**Best fonts**: Pairing 02, Pairing 07, Pairing 08  
**Reference brands**: Apple (macOS UI), Stripe (recent), early iOS design

---

## 7. Neumorphism / Soft UI

**Core philosophy**: UI elements appear extruded from the background — soft, tactile.

**Visual hallmarks**:
- Monochromatic palette (background and elements same hue family)
- Dual shadow technique: light shadow top-left, dark shadow bottom-right
- No borders, depth achieved purely by shadow
- Pastel or mid-range tones only (too dark or light kills the effect)
- Subtle, calm interactions

**CSS patterns**:
```css
.neumorphic {
  background: #e0e5ec;
  border-radius: 12px;
  box-shadow: 9px 9px 16px rgba(163,177,198,0.6), -9px -9px 16px rgba(255,255,255,0.8);
}
.neumorphic-inset {
  box-shadow: inset 9px 9px 16px rgba(163,177,198,0.6), inset -9px -9px 16px rgba(255,255,255,0.8);
}
```

**Best themes**: Custom (requires specific single-hue background)  
**Best fonts**: Pairing 08, Pairing 14  
**Reference brands**: Dribbble explorations, some fintech apps

---

## 8. Material Design (Google's)

**Core philosophy**: Digital paper. Elevation through shadow. Motion is choreographed.

**Visual hallmarks**:
- Cards as primary container metaphor
- Elevation via box-shadow (dp system: 0dp, 2dp, 4dp, 8dp, 16dp)
- FAB (Floating Action Button) for primary action
- Ripple effects on clicks
- Primary + secondary color system, surface colors
- Roboto or sans-serif with specific weight scale

**CSS patterns**:
```css
/* Material elevation levels */
--elevation-1: 0 1px 3px rgba(0,0,0,.12), 0 1px 2px rgba(0,0,0,.24);
--elevation-2: 0 3px 6px rgba(0,0,0,.15), 0 2px 4px rgba(0,0,0,.12);
--elevation-3: 0 10px 20px rgba(0,0,0,.15), 0 3px 6px rgba(0,0,0,.10);
```

**Best themes**: `cloud-blue`, `mint-fresh`  
**Best fonts**: Pairing 13 (Raleway + Roboto)

---

## 9. Constructivism / Bauhaus-Inspired

**Core philosophy**: Art serves function. Geometry, primary colors, strong diagonals.

**Visual hallmarks**:
- Primary colors: red, yellow, blue + black + white only
- Strong geometric shapes as design elements (circles, rectangles, diagonal lines)
- Diagonal layouts, rotated text
- Sans-serif only, condensed or wide variants
- Asymmetric but balanced compositions
- Elements intersect and overlap purposefully

**CSS patterns**:
```css
/* Diagonal divider */
clip-path: polygon(0 0, 100% 0, 100% 85%, 0 100%);
/* Rotated accent text */
transform: rotate(-90deg);
/* Bold geometric shape */
.shape { width: 200px; height: 200px; background: #e11d48; border-radius: 50%; }
```

**Best themes**: `brutal-electric`, custom primary-colors-only  
**Best fonts**: Pairing 03, Pairing 05, Pairing 09

---

## 10. Skeuomorphism (Modern Micro-Skeuomorphism)

**Core philosophy**: UI elements visually reference their real-world counterparts.

**Visual hallmarks**:
- Textures: paper, wood, metal, leather
- Realistic shadows and lighting (directional)
- Buttons look pressable (3D depth)
- Icons look like physical objects
- Warmth and tactility over flatness
- Modern interpretation: subtle textures on flat design (noise overlay, grain)

**CSS patterns**:
```css
/* Noise grain overlay */
.grain::after {
  content: '';
  position: fixed; inset: 0;
  background-image: url("data:image/svg+xml,..."); /* SVG noise */
  opacity: 0.04;
  pointer-events: none;
}
/* Subtle paper texture */
background-color: #fffbf5;
background-image: url("noise.png");
```

**Best themes**: `warm-cream`, `paper-white`  
**Best fonts**: Pairing 01, Pairing 06

---

## 11. Maximalism

**Core philosophy**: More is more. Richness, abundance, controlled chaos.

**Visual hallmarks**:
- Multiple typefaces (2–3)
- Rich color palette (4–5 colors in harmony)
- Dense layouts — little white space
- Layered backgrounds (gradients + images + color)
- Decorative borders, ornamental elements
- Bold patterns, textures, illustrations
- Animation everywhere

**CSS patterns**:
```css
background: linear-gradient(135deg, #f97316, #a855f7, #0ea5e9);
/* Or mesh gradient */
background: radial-gradient(at 40% 20%, #f97316 0px, transparent 50%),
            radial-gradient(at 80% 0%, #a855f7 0px, transparent 50%),
            radial-gradient(at 0% 50%, #0ea5e9 0px, transparent 50%);
```

**Best themes**: `neon-void`, `glass-aurora`, `sunset-coral`  
**Best fonts**: Mix pairings 07 + 12, or 09 + 04

---

## 12. Hand-Drawn / Illustration Style

**Core philosophy**: Imperfection signals humanity. Personality over polish.

**Visual hallmarks**:
- Sketchy borders (SVG path with wobble)
- Hand-drawn icons and illustrations
- Marker/crayon textures
- Organic, non-grid layouts
- Handwriting fonts for accents
- Bright, slightly "off" colors (slightly desaturated or oversaturated)

**CSS patterns**:
```css
/* Sketchy border via SVG background */
border: 0;
background-image: url("squiggle-border.svg");
/* Wavy underline */
text-decoration: underline wavy #f97316;
```

**Best themes**: `warm-cream`, custom bright/playful  
**Best fonts**: Pairing 12, display: 'Caveat' (Google Fonts handwriting), body: Karla

---

## 13. Dark Mode Premium

**Core philosophy**: Darkness as luxury. Depth, glow, controlled highlights.

**Visual hallmarks**:
- True black or very dark grey backgrounds
- Glowing colored accents (not flat)
- Gradient text (especially on headings)
- Subtle grid or dot patterns in background
- Frosted glass cards
- Neon or electric accent colors

**CSS patterns**:
```css
/* Gradient text */
background: linear-gradient(90deg, #f97316, #fbbf24);
-webkit-background-clip: text;
-webkit-text-fill-color: transparent;
/* Glow effect */
box-shadow: 0 0 20px rgba(249,115,22,0.4);
/* Dot grid bg */
background-image: radial-gradient(circle, rgba(255,255,255,0.08) 1px, transparent 1px);
background-size: 24px 24px;
```

**Best themes**: `midnight-ember`, `neon-void`, `deep-ocean`, `glass-aurora`  
**Best fonts**: Pairings 02, 07, 08

---

## Style × Project Matrix

| Project Type | Primary Style | Avoid |
|-------------|--------------|-------|
| Dev tool / SaaS | Minimalism or Dark Premium | Maximalism, Hand-drawn |
| Agency / Studio | Neobrutalism or Editorial | Neumorphism |
| E-commerce | Minimalism or Material | Brutalism |
| Gaming / Crypto | Dark Premium or Glassmorphism | Swiss Style |
| Healthcare | Minimalism or Material | Brutalism, Maximalism |
| Fashion / Beauty | Editorial or Maximalism | Brutalism |
| Fintech | Swiss Style or Dark Premium | Hand-drawn, Maximalism |
| Portfolio | Neobrutalism or Constructivism | Material, Neumorphism |
| Food / Lifestyle | Maximalism or Hand-drawn | Swiss, Dark Premium |
| Education | Material or Minimalism | Neobrutalism |

---

## Blending Styles

Effective secondary style blends:
- **Minimalism + Editorial** → Clean structure with typographic drama (NYT, Stripe)
- **Neobrutalism + Dark Premium** → Bold outlines with dark bg and color glow
- **Glassmorphism + Minimalism** → Frosted glass on very sparse dark layout
- **Swiss + Constructivism** → Maximum grid rigor with geometric color blocks
- **Material + Glassmorphism** → Elevated cards with frosted translucency

Avoid blending:
- Neumorphism + Glassmorphism (competing depth systems)
- Maximalism + Swiss Style (philosophical contradiction)
- Hand-drawn + Dark Premium (tone mismatch)