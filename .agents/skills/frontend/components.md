---
name: frontend-components
description: Component sourcing playbook for production frontends. Covers shadcn/ui, 21st.dev (via live SDK doc fetch), ReactBits, Radix UI, Magic UI, Aceternity UI, and custom patterns. Defines which components to pull from which source, how to install them, and replication patterns for every library. Always read this before choosing or building any UI component.
---

# Component Sources Playbook

## How Component Sourcing Works

Three sourcing modes — evaluated in this order every time a component is needed:

| Priority | Mode | How | When |
|---------|------|-----|------|
| **1** | **21st SDK Live Fetch** | Fetch `https://21st.dev/agents/llms.txt` → follow links to exact component docs | Always available — no MCP, no API key needed |
| **2** | **shadcn CLI** | `npx shadcn@latest add [component]` | Component exists in shadcn registry |
| **3** | **Pattern Replication** | Build from the style patterns in this file | When live fetch isn't needed or component isn't in registries |
| **4** | **Custom** | Built from scratch using design tokens | Unique requirements nothing above covers |

---

## 21st SDK — Live Component Fetching

No MCP server needed. Fetch live docs directly via URL at the time of building.

### Step-by-step protocol for any 21st.dev component

**1. Fetch the entry point first:**
```
GET https://21st.dev/agents/llms.txt
```
This returns the full index of available components and their doc URLs.

**2. Navigate to the specific component doc:**
- Doc URLs follow the pattern: `https://21st.dev/agents/docs/[component-name]`
- **Always convert to Markdown version** by inserting `md/` in the path:
  - `https://21st.dev/agents/docs/hero-section` → `https://21st.dev/agents/docs/md/hero-section`
  - `https://21st.dev/agents/docs/pricing-card` → `https://21st.dev/agents/docs/md/pricing-card`

**3. Read only the section needed** — avoid fetching `llms-full.txt` unless the component isn't findable from `llms.txt` links, as it's very large.

**4. Implement exactly as documented** — adapt colors to `var(--color-*)` tokens, adapt fonts to `var(--font-*)` tokens.

### When to use 21st SDK fetch

Use it when the user asks for any of these (not exhaustive — always check `llms.txt` for what's available):

```
Hero sections           Pricing cards / tables    Feature showcases
CTA blocks              Testimonial cards          Stats / metrics sections
Auth forms (styled)     Navbars (advanced)         Footer variants
Timeline components     Step indicators            Comparison tables
```

### Example fetch flow in practice

```
User: "Build me a pricing section"

1. fetch https://21st.dev/agents/llms.txt          → find pricing-related doc links
2. fetch https://21st.dev/agents/docs/md/pricing   → get full component source + usage
3. Implement the component, replacing any hardcoded
   colors/fonts with CSS variable tokens
4. Install any peer dependencies listed in the docs
```

---

## Component Library Reference

### 1. shadcn/ui
**Style**: Clean, neutral, highly composable. Designed to be copied into your project and owned.  
**Install**: `npx shadcn@latest add [component-name]`  
**Docs**: https://ui.shadcn.com/docs/components

**Component catalogue — always use these before building custom:**

| Component | Install command | Use for |
|-----------|----------------|---------|
| Button | `add button` | All CTAs, form submits |
| Input | `add input` | All text fields |
| Textarea | `add textarea` | Message fields, descriptions |
| Label | `add label` | Form labels |
| Card | `add card` | Feature cards, service cards, pricing |
| Badge | `add badge` | Tags, status, announcements |
| Avatar | `add avatar` | User avatars, team members |
| Separator | `add separator` | Dividers, "or" between OAuth options |
| Sheet | `add sheet` | Mobile nav drawer |
| Dialog | `add dialog` | Modals, confirmations |
| Dropdown Menu | `add dropdown-menu` | Nav dropdowns, action menus |
| Checkbox | `add checkbox` | Terms agreement, filters |
| Select | `add select` | Dropdowns, country/role pickers |
| Tabs | `add tabs` | Pricing toggles, content sections |
| Accordion | `add accordion` | FAQ sections |
| Toast | `add sonner` | Success/error notifications |
| Tooltip | `add tooltip` | Icon labels, help text |
| Skeleton | `add skeleton` | Loading states |
| Progress | `add progress` | File upload, onboarding steps |
| Popover | `add popover` | Date pickers, info overlays |
| Command | `add command` | Search bars, command palettes |
| Navigation Menu | `add navigation-menu` | Complex multi-level navbars |
| Carousel | `add carousel` | Testimonial sliders |
| Toggle | `add toggle` | Theme switcher, view mode |

**Customization rule**: After installing, always restyle using CSS variables — never hardcode colors inside the component file.

```tsx
// ✅ Correct — theme-aware
<Button className="bg-[var(--color-primary)] text-[var(--color-primary-fg)]">

// ❌ Wrong — breaks theming
<Button className="bg-blue-600 text-white">
```

---

### 2. 21st.dev
**Style**: Premium, modern, production-polished. Heavy use of gradients, glass effects, micro-animations.  
**Best for**: Hero sections, pricing cards, feature showcases, CTA blocks, auth pages  
**With SDK fetch**: `fetch https://21st.dev/agents/llms.txt` → find the component → fetch `/agents/docs/md/[name]`  
**Without fetch**: Replicate using the patterns below

**Pattern: Gradient Border Card**
```tsx
// 21st.dev style — glowing gradient border on hover
export function GradientBorderCard({ children }: { children: React.ReactNode }) {
  return (
    <div className="relative group rounded-[var(--radius-xl)] p-px bg-gradient-to-br from-transparent via-transparent to-transparent hover:from-[var(--color-primary)] hover:via-[var(--color-accent)] hover:to-[var(--color-primary)] transition-all duration-500">
      <div className="relative rounded-[var(--radius-xl)] bg-[var(--color-surface)] p-6 h-full">
        {children}
      </div>
    </div>
  )
}
```

**Pattern: Shimmer Button**
```tsx
export function ShimmerButton({ children, className }: { children: React.ReactNode; className?: string }) {
  return (
    <button
      className={cn(
        'relative inline-flex items-center justify-center overflow-hidden rounded-[var(--radius-full)] px-6 py-3 font-semibold text-[var(--color-primary-fg)]',
        'bg-[var(--color-primary)] transition-all duration-300',
        'before:absolute before:inset-0 before:-translate-x-full before:bg-gradient-to-r before:from-transparent before:via-white/20 before:to-transparent',
        'hover:before:translate-x-full before:transition-transform before:duration-700',
        className
      )}
    >
      {children}
    </button>
  )
}
```

**Pattern: Glow Card (dark themes)**
```tsx
export function GlowCard({ children, glowColor = 'var(--color-primary)' }: GlowCardProps) {
  return (
    <div
      className="relative rounded-[var(--radius-xl)] border border-[var(--color-border)] bg-[var(--color-surface)] p-6 transition-all duration-300 hover:border-[var(--color-primary)]"
      style={{
        boxShadow: `0 0 0 0 ${glowColor}00`,
        transition: 'box-shadow 0.3s ease, border-color 0.3s ease',
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.boxShadow = `0 0 30px 4px color-mix(in srgb, ${glowColor} 25%, transparent)`
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.boxShadow = `0 0 0 0 ${glowColor}00`
      }}
    >
      {children}
    </div>
  )
}
```

**Pattern: Animated Gradient Text**
```tsx
export function GradientText({ children, className }: { children: React.ReactNode; className?: string }) {
  return (
    <span
      className={cn('bg-clip-text text-transparent animate-gradient-x', className)}
      style={{
        backgroundImage: 'linear-gradient(90deg, var(--color-primary), var(--color-accent), var(--color-primary))',
        backgroundSize: '200% auto',
      }}
    >
      {children}
    </span>
  )
}

// globals.css
// @keyframes gradient-x { 0%, 100% { background-position: 0% center } 50% { background-position: 100% center } }
// .animate-gradient-x { animation: gradient-x 4s ease infinite; }
```

**Pattern: Glass Card**
```tsx
export function GlassCard({ children, className }: { children: React.ReactNode; className?: string }) {
  return (
    <div
      className={cn(
        'rounded-[var(--radius-xl)] border border-white/10 p-6',
        'bg-white/5 backdrop-blur-xl',
        'shadow-[0_8px_32px_rgba(0,0,0,0.3)]',
        className
      )}
    >
      {children}
    </div>
  )
}
```

---

### 3. ReactBits
**Style**: Animated, expressive, scroll-driven. Focuses on interaction quality over visual decoration.  
**Docs**: https://www.reactbits.dev  
**Best for**: Scroll animations, text effects, interactive backgrounds, creative transitions

**Pattern: Typewriter Effect**
```tsx
import { useEffect, useState } from 'react'

export function Typewriter({ words, speed = 80, deleteSpeed = 40, pause = 1800 }: TypewriterProps) {
  const [text, setText] = useState('')
  const [wordIndex, setWordIndex] = useState(0)
  const [isDeleting, setIsDeleting] = useState(false)

  useEffect(() => {
    const current = words[wordIndex]
    const timeout = setTimeout(() => {
      if (!isDeleting) {
        setText(current.slice(0, text.length + 1))
        if (text.length === current.length) {
          setTimeout(() => setIsDeleting(true), pause)
        }
      } else {
        setText(current.slice(0, text.length - 1))
        if (text.length === 0) {
          setIsDeleting(false)
          setWordIndex((i) => (i + 1) % words.length)
        }
      }
    }, isDeleting ? deleteSpeed : speed)
    return () => clearTimeout(timeout)
  }, [text, isDeleting, wordIndex, words, speed, deleteSpeed, pause])

  return (
    <span>
      {text}
      <span className="animate-pulse text-[var(--color-primary)]">|</span>
    </span>
  )
}

// Usage in hero:
<h1>We build <Typewriter words={['faster', 'smarter', 'better']} /></h1>
```

**Pattern: Animated Background Grid**
```tsx
// Dot grid or line grid background — ReactBits style
export function GridBackground({ variant = 'dots' }: { variant?: 'dots' | 'lines' }) {
  const style =
    variant === 'dots'
      ? {
          backgroundImage: 'radial-gradient(circle, color-mix(in srgb, var(--color-text) 15%, transparent) 1px, transparent 1px)',
          backgroundSize: '28px 28px',
        }
      : {
          backgroundImage:
            'linear-gradient(color-mix(in srgb, var(--color-border) 60%, transparent) 1px, transparent 1px), linear-gradient(90deg, color-mix(in srgb, var(--color-border) 60%, transparent) 1px, transparent 1px)',
          backgroundSize: '40px 40px',
        }

  return (
    <div className="absolute inset-0 -z-10" style={style}>
      {/* Fade to background at edges */}
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-[var(--color-background)]" />
    </div>
  )
}

// Usage:
<section className="relative overflow-hidden">
  <GridBackground variant="dots" />
  <HeroContent />
</section>
```

**Pattern: Tilt Card**
```tsx
import { useRef, MouseEvent } from 'react'
import { motion, useMotionValue, useSpring, useTransform } from 'framer-motion'

export function TiltCard({ children }: { children: React.ReactNode }) {
  const ref = useRef<HTMLDivElement>(null)
  const x = useMotionValue(0)
  const y = useMotionValue(0)
  const springX = useSpring(x, { stiffness: 200, damping: 20 })
  const springY = useSpring(y, { stiffness: 200, damping: 20 })
  const rotateX = useTransform(springY, [-0.5, 0.5], ['8deg', '-8deg'])
  const rotateY = useTransform(springX, [-0.5, 0.5], ['-8deg', '8deg'])

  const handleMouseMove = (e: MouseEvent<HTMLDivElement>) => {
    const rect = ref.current?.getBoundingClientRect()
    if (!rect) return
    x.set((e.clientX - rect.left) / rect.width - 0.5)
    y.set((e.clientY - rect.top) / rect.height - 0.5)
  }

  return (
    <motion.div
      ref={ref}
      style={{ rotateX, rotateY, transformStyle: 'preserve-3d', perspective: 1000 }}
      onMouseMove={handleMouseMove}
      onMouseLeave={() => { x.set(0); y.set(0) }}
      className="cursor-pointer"
    >
      {children}
    </motion.div>
  )
}
```

**Pattern: Spotlight Hover**
```tsx
import { useRef, MouseEvent } from 'react'

export function SpotlightCard({ children, className }: { children: React.ReactNode; className?: string }) {
  const ref = useRef<HTMLDivElement>(null)

  const handleMouseMove = (e: MouseEvent<HTMLDivElement>) => {
    const el = ref.current
    if (!el) return
    const rect = el.getBoundingClientRect()
    el.style.setProperty('--x', `${e.clientX - rect.left}px`)
    el.style.setProperty('--y', `${e.clientY - rect.top}px`)
  }

  return (
    <div
      ref={ref}
      onMouseMove={handleMouseMove}
      className={cn('relative overflow-hidden rounded-[var(--radius-xl)] border border-[var(--color-border)] bg-[var(--color-surface)] p-6', className)}
      style={{
        background: `radial-gradient(400px circle at var(--x, 50%) var(--y, 50%), color-mix(in srgb, var(--color-primary) 8%, transparent), transparent 60%), var(--color-surface)`,
      }}
    >
      {children}
    </div>
  )
}
```

---

### 4. Magic UI
**Style**: Particle effects, beam animations, sparkles, orbit rings — heavy on wow-factor visual effects.  
**Docs**: https://magicui.design  
**Best for**: Hero backgrounds, feature highlights, loading states, empty states

**Pattern: Beam / Border Beam**
```tsx
import { useEffect, useRef } from 'react'

export function BorderBeam({ size = 200, duration = 12, colorFrom = 'var(--color-primary)', colorTo = 'var(--color-accent)' }: BorderBeamProps) {
  return (
    <div
      className="absolute inset-0 rounded-[inherit] pointer-events-none overflow-hidden"
      style={{ '--beam-size': `${size}px`, '--beam-duration': `${duration}s` } as React.CSSProperties}
    >
      <div
        className="absolute inset-0"
        style={{
          background: `conic-gradient(from 0deg, transparent 0deg, ${colorFrom} 60deg, ${colorTo} 120deg, transparent 180deg)`,
          borderRadius: 'inherit',
          animation: `spin ${duration}s linear infinite`,
          WebkitMask: 'linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0)',
          WebkitMaskComposite: 'xor',
          maskComposite: 'exclude',
          padding: '1px',
        }}
      />
    </div>
  )
}

// globals.css: @keyframes spin { from { transform: rotate(0deg) } to { transform: rotate(360deg) } }

// Usage:
<div className="relative">
  <BorderBeam />
  <Card>Premium content here</Card>
</div>
```

**Pattern: Animated Noise / Grain Overlay**
```tsx
// Adds film grain texture — subtle, adds depth to solid backgrounds
export function GrainOverlay({ opacity = 0.04 }: { opacity?: number }) {
  return (
    <div
      className="pointer-events-none fixed inset-0 z-[999]"
      style={{
        opacity,
        backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E")`,
      }}
    />
  )
}

// Add once in App.tsx:
<GrainOverlay opacity={0.035} />
```

---

### 5. Aceternity UI
**Style**: Spotlight effects, 3D card flips, moving borders, aurora backgrounds.  
**Docs**: https://ui.aceternity.com  
**Best for**: Hero sections, dark theme projects, portfolios, landing pages with high visual impact

**Pattern: Aurora Background**
```tsx
export function AuroraBackground({ children }: { children: React.ReactNode }) {
  return (
    <div className="relative overflow-hidden bg-[var(--color-background)]">
      {/* Aurora blobs */}
      <div className="absolute -top-40 -left-40 w-[600px] h-[600px] rounded-full opacity-20 blur-[120px] bg-[var(--color-primary)] animate-aurora-1" />
      <div className="absolute -top-20 right-0 w-[500px] h-[500px] rounded-full opacity-15 blur-[100px] bg-[var(--color-accent)] animate-aurora-2" />
      <div className="absolute top-1/2 left-1/3 w-[400px] h-[400px] rounded-full opacity-10 blur-[80px] bg-[var(--color-secondary)] animate-aurora-3" />
      {children}
    </div>
  )
}

/*
globals.css:
@keyframes aurora-1 { 0%,100% { transform: translate(0,0) scale(1) } 50% { transform: translate(80px, 40px) scale(1.1) } }
@keyframes aurora-2 { 0%,100% { transform: translate(0,0) scale(1) } 50% { transform: translate(-60px, 60px) scale(0.95) } }
@keyframes aurora-3 { 0%,100% { transform: translate(0,0) scale(1) } 50% { transform: translate(40px,-80px) scale(1.05) } }
.animate-aurora-1 { animation: aurora-1 8s ease-in-out infinite; }
.animate-aurora-2 { animation: aurora-2 10s ease-in-out infinite; }
.animate-aurora-3 { animation: aurora-3 12s ease-in-out infinite; }
*/
```

**Pattern: 3D Flip Card**
```tsx
export function FlipCard({ front, back }: { front: React.ReactNode; back: React.ReactNode }) {
  return (
    <div className="group h-64 [perspective:1000px]">
      <div className="relative h-full transition-all duration-700 [transform-style:preserve-3d] group-hover:[transform:rotateY(180deg)]">
        {/* Front */}
        <div className="absolute inset-0 rounded-[var(--radius-xl)] bg-[var(--color-surface)] border border-[var(--color-border)] p-6 [backface-visibility:hidden]">
          {front}
        </div>
        {/* Back */}
        <div className="absolute inset-0 rounded-[var(--radius-xl)] bg-[var(--color-primary)] p-6 [backface-visibility:hidden] [transform:rotateY(180deg)]">
          {back}
        </div>
      </div>
    </div>
  )
}
```

---

### 6. Radix UI Primitives
**Style**: Headless — zero visual opinions. You own 100% of the styling.  
**Install**: `npm install @radix-ui/react-[primitive]`  
**Use when**: shadcn doesn't have what you need but you want accessible, well-tested behavior

```tsx
// Commonly needed Radix primitives not covered by shadcn
import * as HoverCard from '@radix-ui/react-hover-card'
import * as Collapsible from '@radix-ui/react-collapsible'
import * as ScrollArea from '@radix-ui/react-scroll-area'
import * as VisuallyHidden from '@radix-ui/react-visually-hidden'
import * as Portal from '@radix-ui/react-portal'
```

---

## Decision Tree — Which Source to Use?

```
Need a component?
│
├─ Is it a premium section (hero, pricing, CTA, feature showcase)?
│   └─ Fetch from 21st.dev ──────────────────────────────────────────────────────────┐
│       1. fetch https://21st.dev/agents/llms.txt                                    │
│       2. Find component link → convert to /md/ path                                │
│       3. Fetch that URL → implement with CSS variable theming                      │
│       └─ If not found in llms.txt → use patterns from §21st.dev above ◄────────────┘
│
├─ Is it a standard UI primitive?
│   └─ Is it in shadcn? ────────────────────────────────────────────────────────────►
│       (Button, Card, Input, Badge, Sheet, Dialog, Tabs, etc.)                       Use shadcn CLI
│       npx shadcn@latest add [component]
│
├─ Need an interactive / scroll effect?
│   └─ Use ReactBits patterns (Typewriter, Tilt, Spotlight, Grid bg)
│
├─ Need a dramatic hero background or wow-factor effect?
│   └─ Use Magic UI or Aceternity patterns (Aurora, Grain, BorderBeam, 3D Flip)
│
├─ Need accessible headless behavior shadcn doesn't cover?
│   └─ Use Radix UI primitive directly
│
└─ Nothing above fits? ────────────────────────────────────────────────────────────►
    Build custom using design tokens only
```

---

## Component × Page Mapping

| Page | Source | Components |
|------|--------|-----------|
| **Navbar** | shadcn | `Sheet` (mobile drawer), `Button`, `Navigation Menu` |
| **Hero** | 21st.dev fetch + patterns | Hero section from 21st.dev; `AuroraBackground` or `GridBackground` (bg); `GradientText`; `ShimmerButton` (CTA) |
| **Features** | 21st.dev fetch + patterns | Feature section from 21st.dev; `GlowCard` (dark themes); `SpotlightCard`; `TiltCard` |
| **Social Proof** | patterns | Logo marquee (animations.md §12); `AnimatedStat` (animations.md §6) |
| **Testimonials** | shadcn | `Card` + `Avatar` + `Carousel` |
| **Pricing** | 21st.dev fetch | Pricing table from 21st.dev; `BorderBeam` on popular plan |
| **Services** | patterns | `GradientBorderCard` or `SpotlightCard` |
| **How It Works** | patterns + shadcn | Custom step layout; shadcn `Badge` for step numbers |
| **FAQ** | animations.md | Animated accordion (animations.md §13) — more control than shadcn Accordion |
| **Contact Form** | shadcn + animations.md | `Input`, `Textarea`, `Label`, `Button`; animated float labels (animations.md §14) |
| **Login / Signup** | shadcn + patterns | shadcn card + `Separator` + `ShimmerButton`; animated fields (animations.md §14) |
| **Footer** | custom + shadcn | Custom layout; shadcn `Separator` |

---

## Integration Quality Rules

Whether using 21st SDK fetch or pattern replication, always enforce these:

1. **Theme tokens always** — Replace any hardcoded colors from fetched/replicated components with `var(--color-*)` tokens. Same for fonts → `var(--font-*)`, radii → `var(--radius-*)`.
2. **Design style consistency** — A Neobrutalist project must not have glassmorphism cards. A Minimalist project must not have aurora backgrounds. Match the chosen design style from `design-styles.md`.
3. **Reduced-motion guards** — Every animated component must respect `prefers-reduced-motion`. See `animations.md` rules section.
4. **Mobile-first audit** — Many 21st.dev and ReactBits components are desktop-first. Always verify and fix at `sm` (640px) breakpoint.
5. **Keyboard accessibility** — Custom interactive components must have: visible focus rings, correct `tabIndex`, `onKeyDown` handlers for Enter/Space/Escape where applicable.
6. **No marketing copy** — When fetching from 21st.dev, implement only the component structure and interactions — never carry over placeholder text verbatim.
7. **Peer dependencies** — Always install any peer deps listed in the 21st.dev component docs before using the component.