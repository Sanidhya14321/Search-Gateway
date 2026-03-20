---
name: frontend-animations
description: Professional animation playbook using Framer Motion and GSAP for frontend projects. Covers hero sequences, scroll-triggered reveals, page transitions, navbar, stagger grids, text animations, magnetic buttons, counter animations, parallax, SVG path drawing, and cursor effects. Always read this file when implementing any motion or interaction.
---

# Animations Playbook

Two-library system. Use the right tool for each job — never mix them on the same element.

| Use Framer Motion for | Use GSAP for |
|----------------------|-------------|
| Component mount/unmount | Complex multi-step timelines |
| Route page transitions | ScrollTrigger pinning & scrubbing |
| Hover & tap micro-interactions | SVG path drawing |
| Stagger grids / lists | Counter / number roll-up |
| Shared layout animations | Parallax layers |
| Simple scroll reveals | Magnetic cursor / distortion effects |
| Form field focus states | Large coordinated sequences |

---

## Setup

```bash
npm install framer-motion gsap @gsap/react
```

```tsx
// lib/animation.ts — shared easing constants used across both libraries

export const ease = {
  // Framer Motion easings
  smooth:    [0.25, 0.1, 0.25, 1],
  snappy:    [0.19, 1, 0.22, 1],
  bounce:    [0.34, 1.56, 0.64, 1],
  inOut:     [0.76, 0, 0.24, 1],
  // GSAP equivalents (string refs)
  gsapSmooth:  'power2.out',
  gsapSnappy:  'expo.out',
  gsapBounce:  'back.out(1.7)',
  gsapElastic: 'elastic.out(1, 0.4)',
} as const

export const duration = {
  instant: 0.1,
  fast:    0.25,
  base:    0.45,
  slow:    0.7,
  crawl:   1.1,
} as const
```

---

## 1. Page Transitions

Wrap routes in `AnimatePresence`. Every page exports a `<motion.div>` as its root.

```tsx
// App.tsx
import { AnimatePresence } from 'framer-motion'
import { useLocation } from 'react-router-dom'

export default function App() {
  const location = useLocation()
  return (
    <AnimatePresence mode="wait">
      <Routes location={location} key={location.pathname}>
        <Route path="/"         element={<HomePage />} />
        <Route path="/about"    element={<AboutPage />} />
        <Route path="/services" element={<ServicesPage />} />
        <Route path="/contact"  element={<ContactPage />} />
        <Route path="/login"    element={<LoginPage />} />
        <Route path="/signup"   element={<SignupPage />} />
      </Routes>
    </AnimatePresence>
  )
}
```

```tsx
// components/layout/PageWrapper.tsx
// Wrap every page's root div with this
import { motion } from 'framer-motion'

const variants = {
  initial: { opacity: 0, y: 16 },
  enter:   { opacity: 1, y: 0,  transition: { duration: 0.45, ease: [0.25, 0.1, 0.25, 1] } },
  exit:    { opacity: 0, y: -8, transition: { duration: 0.25, ease: [0.76, 0, 0.24, 1] } },
}

export default function PageWrapper({ children }: { children: React.ReactNode }) {
  return (
    <motion.div variants={variants} initial="initial" animate="enter" exit="exit">
      {children}
    </motion.div>
  )
}
```

Usage — wrap every page:
```tsx
export default function AboutPage() {
  return (
    <PageWrapper>
      <div className="pt-20"> ... </div>
    </PageWrapper>
  )
}
```

---

## 2. Hero Section Sequence (Framer Motion)

The hero is the most important animation. Run in strict order: badge → headline → subtext → CTA → visual.

```tsx
import { motion } from 'framer-motion'

// Orchestrated stagger — parent controls child timing
const heroContainer = {
  hidden: {},
  show: {
    transition: {
      delayChildren:   0.1,
      staggerChildren: 0.12,
    },
  },
}

const heroItem = {
  hidden: { opacity: 0, y: 28, filter: 'blur(4px)' },
  show:   {
    opacity: 1, y: 0, filter: 'blur(0px)',
    transition: { duration: 0.65, ease: [0.19, 1, 0.22, 1] },
  },
}

const heroCta = {
  hidden: { opacity: 0, scale: 0.94 },
  show:   {
    opacity: 1, scale: 1,
    transition: { duration: 0.5, ease: [0.34, 1.56, 0.64, 1] },
  },
}

export function HeroSection() {
  return (
    <motion.div
      className="max-w-4xl"
      variants={heroContainer}
      initial="hidden"
      animate="show"
    >
      {/* Badge */}
      <motion.div variants={heroItem}>
        <Badge>✦ New — announcing v2.0</Badge>
      </motion.div>

      {/* Headline — split into lines for per-line animation */}
      <motion.h1
        className="text-[var(--text-6xl)] lg:text-[var(--text-7xl)] font-display font-bold mt-6"
        variants={heroItem}
      >
        The platform built{' '}
        <span className="text-[var(--color-primary)]">for scale</span>
      </motion.h1>

      {/* Subheadline */}
      <motion.p
        className="mt-6 text-[var(--text-xl)] text-[var(--color-text-muted)] max-w-2xl"
        variants={heroItem}
      >
        One sentence explaining what the product does and who benefits.
      </motion.p>

      {/* CTA group */}
      <motion.div className="mt-10 flex gap-4 flex-wrap" variants={heroCta}>
        <Button size="lg">Get started free</Button>
        <Button size="lg" variant="outline">See demo</Button>
      </motion.div>

      {/* Trust line */}
      <motion.p
        className="mt-5 text-sm text-[var(--color-text-subtle)]"
        variants={heroItem}
      >
        No credit card required · Cancel anytime
      </motion.p>
    </motion.div>
  )
}
```

---

## 3. Word-by-Word Headline Reveal (GSAP)

For hero headlines that split into individual words and animate in.

```tsx
import { useEffect, useRef } from 'react'
import { gsap } from 'gsap'

export function AnimatedHeadline({ text }: { text: string }) {
  const ref = useRef<HTMLHeadingElement>(null)

  useEffect(() => {
    if (!ref.current) return
    const words = ref.current.querySelectorAll('.word')

    gsap.fromTo(words,
      { opacity: 0, y: 40, rotateX: -30 },
      {
        opacity: 1, y: 0, rotateX: 0,
        duration: 0.7,
        ease: 'expo.out',
        stagger: 0.07,
        delay: 0.2,
      }
    )
  }, [])

  return (
    <h1
      ref={ref}
      className="text-[var(--text-6xl)] lg:text-[var(--text-7xl)] font-display font-bold"
      style={{ perspective: 800 }}
    >
      {text.split(' ').map((word, i) => (
        <span
          key={i}
          className="word inline-block mr-[0.25em] overflow-hidden"
          style={{ display: 'inline-block' }}
        >
          {word}
        </span>
      ))}
    </h1>
  )
}
```

---

## 4. Scroll-Triggered Section Reveals (GSAP ScrollTrigger)

```tsx
import { useEffect, useRef } from 'react'
import { gsap } from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

gsap.registerPlugin(ScrollTrigger)

export function useScrollReveal(selector = '.reveal') {
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const ctx = gsap.context(() => {
      gsap.utils.toArray<HTMLElement>(selector).forEach((el) => {
        gsap.fromTo(el,
          { opacity: 0, y: 48 },
          {
            opacity: 1, y: 0,
            duration: 0.75,
            ease: 'power3.out',
            scrollTrigger: {
              trigger: el,
              start:   'top 88%',
              end:     'top 60%',
              toggleActions: 'play none none none',
            },
          }
        )
      })
    }, containerRef)

    return () => ctx.revert()
  }, [])

  return containerRef
}

// Usage in any section:
export function FeaturesSection() {
  const ref = useScrollReveal()
  return (
    <section ref={ref} className="section">
      <div className="container">
        <h2 className="reveal text-[var(--text-4xl)] font-display font-bold mb-12">Features</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {FEATURES.map(f => (
            <div key={f.title} className="reveal">
              <FeatureCard {...f} />
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
```

---

## 5. Stagger Grid (Framer Motion)

For feature cards, service cards, team members — any repeated grid.

```tsx
import { motion } from 'framer-motion'

const grid = {
  hidden: {},
  show: { transition: { staggerChildren: 0.08, delayChildren: 0.1 } },
}

const card = {
  hidden: { opacity: 0, y: 32, scale: 0.96 },
  show:   {
    opacity: 1, y: 0, scale: 1,
    transition: { duration: 0.5, ease: [0.19, 1, 0.22, 1] },
  },
}

export function StaggerGrid({ items }: { items: CardItem[] }) {
  return (
    <motion.div
      className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6"
      variants={grid}
      initial="hidden"
      whileInView="show"
      viewport={{ once: true, margin: '-60px' }}
    >
      {items.map((item) => (
        <motion.div key={item.id} variants={card}>
          <Card className="h-full hover:shadow-[var(--shadow-md)] transition-shadow">
            <CardContent className="p-6">
              <span className="text-3xl mb-4 block">{item.icon}</span>
              <h3 className="text-[var(--text-xl)] font-display font-semibold mb-2">{item.title}</h3>
              <p className="text-[var(--color-text-muted)] text-sm">{item.description}</p>
            </CardContent>
          </Card>
        </motion.div>
      ))}
    </motion.div>
  )
}
```

---

## 6. Animated Number / Counter (GSAP)

For stats, social proof strips, metrics sections.

```tsx
import { useEffect, useRef } from 'react'
import { gsap } from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

gsap.registerPlugin(ScrollTrigger)

interface StatProps {
  end: number
  suffix?: string   // e.g. 'K+', '%', 'x'
  prefix?: string   // e.g. '$'
  label: string
  decimals?: number
}

export function AnimatedStat({ end, suffix = '', prefix = '', label, decimals = 0 }: StatProps) {
  const numRef = useRef<HTMLSpanElement>(null)

  useEffect(() => {
    const el = numRef.current
    if (!el) return

    const obj = { val: 0 }

    gsap.to(obj, {
      val: end,
      duration: 1.8,
      ease: 'power2.out',
      scrollTrigger: { trigger: el, start: 'top 85%', once: true },
      onUpdate: () => {
        el.textContent = prefix + obj.val.toFixed(decimals) + suffix
      },
    })
  }, [end, suffix, prefix, decimals])

  return (
    <div className="text-center">
      <p className="text-[var(--text-5xl)] font-display font-bold text-[var(--color-primary)]">
        {prefix}<span ref={numRef}>0</span>{suffix}
      </p>
      <p className="text-sm text-[var(--color-text-muted)] mt-1">{label}</p>
    </div>
  )
}

// Usage:
<div className="grid grid-cols-2 md:grid-cols-4 gap-8">
  <AnimatedStat end={99.9} suffix="%" label="Uptime SLA" decimals={1} />
  <AnimatedStat end={500}  suffix="+"  label="Customers" />
  <AnimatedStat end={10}   suffix="x"  label="Faster" />
  <AnimatedStat end={24}   suffix="/7" label="Support" />
</div>
```

---

## 7. Navbar Animations

```tsx
import { motion, useScroll, useTransform } from 'framer-motion'

// Slide-down entrance on mount
const navVariants = {
  hidden: { y: -72, opacity: 0 },
  show:   { y: 0, opacity: 1, transition: { duration: 0.5, ease: [0.19, 1, 0.22, 1] } },
}

// Active link underline — Framer layoutId for smooth slide between links
function NavLink({ href, label, isActive }: NavLinkProps) {
  return (
    <Link to={href} className="relative px-4 py-2 text-sm font-medium">
      {isActive && (
        <motion.span
          layoutId="nav-indicator"
          className="absolute inset-0 rounded-[var(--radius-md)] bg-[var(--color-secondary)]"
          transition={{ type: 'spring', bounce: 0.2, duration: 0.4 }}
        />
      )}
      <span className="relative z-10">{label}</span>
    </Link>
  )
}

export function Navbar() {
  return (
    <motion.header
      variants={navVariants}
      initial="hidden"
      animate="show"
      className="fixed top-0 left-0 right-0 z-50 ..."
    >
      <nav className="flex items-center gap-1">
        {NAV_LINKS.map(link => (
          <NavLink key={link.href} {...link} isActive={isActive(link.href)} />
        ))}
      </nav>
    </motion.header>
  )
}
```

---

## 8. Hover Micro-interactions (Framer Motion)

```tsx
// Card lift
<motion.div
  whileHover={{ y: -6, boxShadow: 'var(--shadow-lg)' }}
  whileTap={{ scale: 0.98 }}
  transition={{ type: 'spring', stiffness: 400, damping: 22 }}
>
  <Card>...</Card>
</motion.div>

// Button press
<motion.button
  whileHover={{ scale: 1.03 }}
  whileTap={{ scale: 0.97 }}
  transition={{ type: 'spring', stiffness: 500, damping: 28 }}
>
  Get started
</motion.button>

// Icon spin on hover
<motion.span whileHover={{ rotate: 15 }} transition={{ type: 'spring', stiffness: 300 }}>
  <ArrowRight className="w-4 h-4" />
</motion.span>

// Underline slide — CSS approach (no JS needed, most performant)
// Apply to nav links, footer links, inline text links
.link-underline {
  background-image: linear-gradient(var(--color-primary), var(--color-primary));
  background-size: 0% 2px;
  background-repeat: no-repeat;
  background-position: left bottom;
  transition: background-size 0.3s ease;
}
.link-underline:hover { background-size: 100% 2px; }
```

---

## 9. Magnetic Button (GSAP)

High-impact CTA interaction — button follows the cursor slightly when nearby.

```tsx
import { useRef } from 'react'
import { gsap } from 'gsap'

export function MagneticButton({ children, className }: { children: React.ReactNode; className?: string }) {
  const ref = useRef<HTMLButtonElement>(null)

  const handleMouseMove = (e: React.MouseEvent) => {
    const el = ref.current
    if (!el) return
    const rect = el.getBoundingClientRect()
    const cx = rect.left + rect.width  / 2
    const cy = rect.top  + rect.height / 2
    const dx = (e.clientX - cx) * 0.35
    const dy = (e.clientY - cy) * 0.35

    gsap.to(el, { x: dx, y: dy, duration: 0.4, ease: 'power2.out' })
  }

  const handleMouseLeave = () => {
    gsap.to(ref.current, { x: 0, y: 0, duration: 0.6, ease: 'elastic.out(1, 0.4)' })
  }

  return (
    <button
      ref={ref}
      className={className}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
    >
      {children}
    </button>
  )
}

// Usage — wrap your primary CTA:
<MagneticButton className="btn-primary">Get started free</MagneticButton>
```

---

## 10. Parallax Layers (GSAP ScrollTrigger)

For hero backgrounds, decorative shapes, full bleed images.

```tsx
import { useEffect, useRef } from 'react'
import { gsap } from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

gsap.registerPlugin(ScrollTrigger)

export function ParallaxHero() {
  const sectionRef = useRef<HTMLElement>(null)
  const bgRef      = useRef<HTMLDivElement>(null)
  const shapeRef   = useRef<HTMLDivElement>(null)
  const contentRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const ctx = gsap.context(() => {
      // Background moves slower than scroll (depth effect)
      gsap.to(bgRef.current, {
        yPercent: 30,
        ease: 'none',
        scrollTrigger: { trigger: sectionRef.current, start: 'top top', end: 'bottom top', scrub: true },
      })

      // Decorative shape moves opposite direction
      gsap.to(shapeRef.current, {
        yPercent: -20,
        rotate: 15,
        ease: 'none',
        scrollTrigger: { trigger: sectionRef.current, start: 'top top', end: 'bottom top', scrub: 1.5 },
      })

      // Content moves slightly faster (pull-up feel)
      gsap.to(contentRef.current, {
        yPercent: -10,
        ease: 'none',
        scrollTrigger: { trigger: sectionRef.current, start: 'top top', end: 'bottom top', scrub: 0.5 },
      })
    }, sectionRef)

    return () => ctx.revert()
  }, [])

  return (
    <section ref={sectionRef} className="relative min-h-screen overflow-hidden">
      {/* Background layer */}
      <div ref={bgRef} className="absolute inset-0 -z-20 bg-gradient-to-br from-[var(--color-background)] to-[var(--color-surface)]" />
      {/* Decorative shape */}
      <div ref={shapeRef} className="absolute top-20 right-10 -z-10 w-64 h-64 rounded-full bg-[var(--color-primary)] opacity-10 blur-3xl" />
      {/* Content */}
      <div ref={contentRef} className="container relative z-10 pt-40">
        <HeroContent />
      </div>
    </section>
  )
}
```

---

## 11. SVG Path Drawing (GSAP)

For logo reveals, decorative underlines, icon animations.

```tsx
import { useEffect, useRef } from 'react'
import { gsap } from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

gsap.registerPlugin(ScrollTrigger)

export function DrawnUnderline({ children }: { children: React.ReactNode }) {
  const svgRef = useRef<SVGPathElement>(null)

  useEffect(() => {
    const path = svgRef.current
    if (!path) return
    const length = path.getTotalLength()

    gsap.set(path, { strokeDasharray: length, strokeDashoffset: length })
    gsap.to(path, {
      strokeDashoffset: 0,
      duration: 0.9,
      ease: 'power2.inOut',
      scrollTrigger: { trigger: path, start: 'top 85%', once: true },
    })
  }, [])

  return (
    <span className="relative inline-block">
      {children}
      <svg
        className="absolute -bottom-1 left-0 w-full"
        viewBox="0 0 200 8" preserveAspectRatio="none"
        style={{ height: 8 }}
      >
        <path
          ref={svgRef}
          d="M2 6 C50 2, 100 2, 198 6"
          stroke="var(--color-accent)"
          strokeWidth="3"
          fill="none"
          strokeLinecap="round"
        />
      </svg>
    </span>
  )
}

// Usage in hero:
<h1>The platform <DrawnUnderline>built for you</DrawnUnderline></h1>
```

---

## 12. Horizontal Scroll Marquee (CSS + Framer Motion)

For logo strips, technology badges, social proof bars.

```tsx
import { motion } from 'framer-motion'

const LOGOS = ['Company A', 'Company B', 'Company C', 'Company D', 'Company E', 'Company F']

export function LogoMarquee() {
  // Duplicate for seamless loop
  const items = [...LOGOS, ...LOGOS]

  return (
    <div className="overflow-hidden py-6 border-y border-[var(--color-border)]">
      <motion.div
        className="flex gap-16 w-max"
        animate={{ x: ['0%', '-50%'] }}
        transition={{ duration: 20, ease: 'linear', repeat: Infinity }}
      >
        {items.map((logo, i) => (
          <span key={i} className="text-[var(--color-text-subtle)] font-display font-semibold text-lg whitespace-nowrap">
            {logo}
          </span>
        ))}
      </motion.div>
    </div>
  )
}
```

---

## 13. Accordion / FAQ Reveal (Framer Motion)

```tsx
import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Plus } from 'lucide-react'

interface FAQItem { question: string; answer: string }

export function AnimatedFAQ({ items }: { items: FAQItem[] }) {
  const [open, setOpen] = useState<number | null>(null)

  return (
    <div className="space-y-3">
      {items.map((item, i) => (
        <div key={i} className="border border-[var(--color-border)] rounded-[var(--radius-lg)] overflow-hidden">
          <button
            className="w-full flex items-center justify-between px-6 py-4 text-left font-medium"
            onClick={() => setOpen(open === i ? null : i)}
          >
            <span>{item.question}</span>
            <motion.span animate={{ rotate: open === i ? 45 : 0 }} transition={{ duration: 0.25 }}>
              <Plus className="w-5 h-5 text-[var(--color-text-muted)]" />
            </motion.span>
          </button>

          <AnimatePresence initial={false}>
            {open === i && (
              <motion.div
                key="content"
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1, transition: { height: { duration: 0.35, ease: [0.25, 0.1, 0.25, 1] }, opacity: { duration: 0.25, delay: 0.1 } } }}
                exit={{ height: 0, opacity: 0, transition: { height: { duration: 0.3 }, opacity: { duration: 0.15 } } }}
              >
                <div className="px-6 pb-5 text-[var(--color-text-muted)] text-sm leading-relaxed border-t border-[var(--color-border)]">
                  <div className="pt-4">{item.answer}</div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      ))}
    </div>
  )
}
```

---

## 14. Form Field Animations (Framer Motion)

Auth pages (Login/Signup) feel polished with these micro-interactions.

```tsx
import { motion } from 'framer-motion'
import { useState } from 'react'

export function AnimatedField({ id, label, type = 'text', placeholder }: FieldProps) {
  const [focused, setFocused] = useState(false)
  const [hasValue, setHasValue] = useState(false)

  return (
    <div className="relative">
      {/* Floating label */}
      <motion.label
        htmlFor={id}
        className="absolute left-3 text-[var(--color-text-subtle)] pointer-events-none origin-left"
        animate={{
          y:     focused || hasValue ? -22 : 14,
          scale: focused || hasValue ? 0.78 : 1,
          color: focused ? 'var(--color-primary)' : 'var(--color-text-subtle)',
        }}
        transition={{ duration: 0.2, ease: [0.25, 0.1, 0.25, 1] }}
      >
        {label}
      </motion.label>

      <input
        id={id}
        type={type}
        placeholder={focused ? placeholder : ''}
        onFocus={() => setFocused(true)}
        onBlur={(e) => { setFocused(false); setHasValue(e.target.value.length > 0) }}
        onChange={(e) => setHasValue(e.target.value.length > 0)}
        className="w-full pt-5 pb-2 px-3 bg-[var(--color-surface)] border rounded-[var(--radius-md)] outline-none text-[var(--color-text)] transition-colors"
        style={{ borderColor: focused ? 'var(--color-primary)' : 'var(--color-border)' }}
      />

      {/* Focus ring glow */}
      <motion.div
        className="absolute inset-0 rounded-[var(--radius-md)] pointer-events-none"
        animate={{ boxShadow: focused ? '0 0 0 3px color-mix(in srgb, var(--color-primary) 20%, transparent)' : '0 0 0 0px transparent' }}
        transition={{ duration: 0.2 }}
      />
    </div>
  )
}
```

---

## 15. Scroll Progress Indicator (Framer Motion)

Thin bar at the top of the page showing read progress — great for blog/about pages.

```tsx
import { motion, useScroll, useSpring } from 'framer-motion'

export function ScrollProgress() {
  const { scrollYProgress } = useScroll()
  const scaleX = useSpring(scrollYProgress, { stiffness: 120, damping: 25, restDelta: 0.001 })

  return (
    <motion.div
      className="fixed top-0 left-0 right-0 h-[3px] bg-[var(--color-primary)] origin-left z-[100]"
      style={{ scaleX }}
    />
  )
}
```

---

## Animation Rules — Never Break These

### Performance
- **Only animate** `transform` (translate, scale, rotate) and `opacity`. Never animate `width`, `height`, `top`, `left`, `margin`, or `padding` — these cause layout reflow.
- **Always** add `will-change: transform` via `style` prop on elements with complex GSAP animations.
- **Always** clean up GSAP with `ctx.revert()` in `useEffect` return — prevents memory leaks.
- **Never** run GSAP outside `useEffect` or `gsap.context()`.

### Framer Motion
- **Always** use `viewport={{ once: true }}` on `whileInView` — animations should not replay on scroll-up.
- **Always** use `AnimatePresence` when conditionally rendering animated elements.
- **Use `layoutId`** for shared element transitions (active nav indicator, modal open, card expand).
- **Prefer `type: 'spring'`** over `duration` for interactive elements (hover, tap) — feels physical.
- **Prefer `duration` + `ease`** for entrance/exit animations — gives precise editorial control.

### GSAP
- **Always** `gsap.registerPlugin(ScrollTrigger)` before using it — even if registered elsewhere.
- **Always** wrap GSAP code in `gsap.context(() => { ... }, ref)` — scoped, auto-cleaned.
- **Use `scrub: true`** for scroll-linked animations (parallax). Use `toggleActions` for triggered-once plays.
- **Never** target elements by class string in GSAP inside React — always use `ref` + `gsap.utils.toArray`.

### Accessibility
- **Always** respect `prefers-reduced-motion`:
```tsx
// In globals.css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}

// In Framer Motion
import { useReducedMotion } from 'framer-motion'
const reduced = useReducedMotion()
const variants = reduced
  ? { hidden: { opacity: 0 }, show: { opacity: 1 } }  // no y/scale movement
  : { hidden: { opacity: 0, y: 24 }, show: { opacity: 1, y: 0 } }
```

---

## Animation × Page Mapping

| Page / Component | Animations to Apply |
|-----------------|-------------------|
| **Navbar** | Slide-down entrance (#7), `layoutId` active indicator (#7) |
| **Hero** | Orchestrated stagger sequence (#2), word-by-word headline (#3), SVG underline (#11), magnetic CTA (#9) |
| **Social Proof Strip** | Logo marquee (#12), animated stats (#6) |
| **Features / Services Grid** | Stagger grid reveal (#5), card hover lift (#8) |
| **How It Works** | Scroll reveal with stagger (#4), step number count-up (#6) |
| **Testimonials** | Stagger grid (#5) |
| **About Hero** | Hero stagger (#2), parallax bg (#10) |
| **About Stats** | Animated counters (#6) |
| **Contact Form** | Animated field labels (#14), button hover (#8) |
| **Login / Signup** | Animated fields (#14), button magnetic (#9), page transition (#1) |
| **Footer** | Scroll reveal links (#4) |
| **All Pages** | Page transitions (#1), scroll progress (#15) |