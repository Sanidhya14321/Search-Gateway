---
name: frontend-templates
description: Full TSX/CSS scaffolding for all required frontend pages and components — globals.css, App.tsx router, Navbar (with mobile drawer), Footer, HomePage, AboutPage, ServicesPage, ContactPage, LoginPage, SignupPage, and theme.ts. Always customize to the chosen theme and design style, never output verbatim.
---

# Page Templates

Full structural scaffolding for every required page. These are starting skeletons — always adapt to the
chosen theme, design style, and project context. Never output templates verbatim; always customize.

**Table of Contents**
1. [globals.css](#globals)
2. [App.tsx + Router](#app)
3. [Navbar](#navbar)
4. [Footer](#footer)
5. [HomePage](#home)
6. [AboutPage](#about)
7. [ServicesPage](#services)
8. [ContactPage](#contact)
9. [LoginPage](#login)
10. [SignupPage](#signup)
11. [theme.ts](#theme)

---

## 1. globals.css {#globals}

```css
/* ═══════════════════════════════════════════
   DESIGN SYSTEM: [THEME NAME] × [STYLE]
   Fonts: [DISPLAY] / [BODY]
   ═══════════════════════════════════════════ */

/* 1. Font Import — from fonts.md */
@import url('https://fonts.googleapis.com/css2?family=DISPLAY_FONT:wght@400;600;700;800&family=BODY_FONT:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

/* 2. Theme tokens — from themes.md */
:root {
  /* ← paste selected theme here */

  /* Type scale */
  --text-xs:   0.75rem;
  --text-sm:   0.875rem;
  --text-base: 1rem;
  --text-lg:   1.125rem;
  --text-xl:   1.25rem;
  --text-2xl:  1.5rem;
  --text-3xl:  1.875rem;
  --text-4xl:  2.25rem;
  --text-5xl:  3rem;
  --text-6xl:  3.75rem;
  --text-7xl:  4.5rem;

  /* Line heights */
  --leading-tight:   1.2;
  --leading-snug:    1.375;
  --leading-normal:  1.5;
  --leading-relaxed: 1.625;

  /* Letter spacing */
  --tracking-tight:   -0.02em;
  --tracking-normal:   0em;
  --tracking-wide:     0.05em;
  --tracking-widest:   0.1em;

  /* Font families */
  --font-display: 'DISPLAY_FONT', sans-serif;
  --font-body:    'BODY_FONT', sans-serif;
  --font-mono:    'JetBrains Mono', monospace;
}

/* 3. Reset & Base */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html {
  font-size: 16px;
  scroll-behavior: smooth;
  -webkit-font-smoothing: antialiased;
}

body {
  font-family: var(--font-body);
  font-size: var(--text-base);
  line-height: var(--leading-normal);
  color: var(--color-text);
  background-color: var(--color-background);
}

h1, h2, h3, h4, h5, h6 {
  font-family: var(--font-display);
  line-height: var(--leading-tight);
  letter-spacing: var(--tracking-tight);
  color: var(--color-text);
}

a { color: inherit; text-decoration: none; }
img, video { max-width: 100%; display: block; }
button { cursor: pointer; font-family: inherit; }

/* 4. Layout utilities */
.container { max-width: 1280px; margin: 0 auto; padding: 0 1.5rem; }
@media (min-width: 640px)  { .container { padding: 0 2rem; } }
@media (min-width: 1024px) { .container { padding: 0 2.5rem; } }

.section { padding: 6rem 0; }
@media (max-width: 768px) { .section { padding: 4rem 0; } }

/* 5. Scrollbar (optional — matches theme) */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--color-background); }
::-webkit-scrollbar-thumb { background: var(--color-border-strong); border-radius: 3px; }
```

---

## 2. App.tsx + Router {#app}

```tsx
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Navbar from '@/components/layout/Navbar'
import Footer from '@/components/layout/Footer'
import HomePage from '@/pages/HomePage'
import AboutPage from '@/pages/AboutPage'
import ServicesPage from '@/pages/ServicesPage'
import ContactPage from '@/pages/ContactPage'
import LoginPage from '@/pages/LoginPage'
import SignupPage from '@/pages/SignupPage'

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen flex flex-col">
        <Navbar />
        <main className="flex-1">
          <Routes>
            <Route path="/"          element={<HomePage />} />
            <Route path="/about"     element={<AboutPage />} />
            <Route path="/services"  element={<ServicesPage />} />
            <Route path="/contact"   element={<ContactPage />} />
            <Route path="/login"     element={<LoginPage />} />
            <Route path="/signup"    element={<SignupPage />} />
          </Routes>
        </main>
        <Footer />
      </div>
    </BrowserRouter>
  )
}
```

---

## 3. Navbar {#navbar}

```tsx
import { useState, useEffect } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { Menu, X } from 'lucide-react'
import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

const NAV_LINKS = [
  { label: 'Home',     href: '/' },
  { label: 'About',    href: '/about' },
  { label: 'Services', href: '/services' },
  { label: 'Contact',  href: '/contact' },
]

export default function Navbar() {
  const [scrolled, setScrolled] = useState(false)
  const [open, setOpen] = useState(false)
  const location = useLocation()

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20)
    window.addEventListener('scroll', onScroll)
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  const isActive = (href: string) =>
    href === '/' ? location.pathname === '/' : location.pathname.startsWith(href)

  return (
    <header
      className={cn(
        'fixed top-0 left-0 right-0 z-50 transition-all duration-300',
        scrolled
          ? 'bg-[var(--color-surface)]/90 backdrop-blur-md border-b border-[var(--color-border)] shadow-[var(--shadow-sm)]'
          : 'bg-transparent'
      )}
    >
      <div className="container flex items-center justify-between h-16 lg:h-18">
        {/* Logo */}
        <Link to="/" className="flex items-center gap-2">
          <span className="font-display font-bold text-xl text-[var(--color-text)]">
            BrandName {/* Replace with actual logo/name */}
          </span>
        </Link>

        {/* Desktop Nav */}
        <nav className="hidden lg:flex items-center gap-1">
          {NAV_LINKS.map((link) => (
            <Link
              key={link.href}
              to={link.href}
              className={cn(
                'px-4 py-2 rounded-[var(--radius-md)] text-sm font-medium transition-colors',
                isActive(link.href)
                  ? 'text-[var(--color-primary)] bg-[var(--color-secondary)]'
                  : 'text-[var(--color-text-muted)] hover:text-[var(--color-text)] hover:bg-[var(--color-surface-2)]'
              )}
            >
              {link.label}
            </Link>
          ))}
        </nav>

        {/* Desktop CTA */}
        <div className="hidden lg:flex items-center gap-3">
          <Link to="/login">
            <Button variant="ghost" size="sm">Log in</Button>
          </Link>
          <Link to="/signup">
            <Button size="sm">Get Started</Button>
          </Link>
        </div>

        {/* Mobile Hamburger */}
        <Sheet open={open} onOpenChange={setOpen}>
          <SheetTrigger asChild className="lg:hidden">
            <Button variant="ghost" size="icon">
              <Menu className="w-5 h-5" />
            </Button>
          </SheetTrigger>
          <SheetContent side="right" className="w-72 bg-[var(--color-surface)]">
            <div className="flex flex-col gap-2 mt-8">
              {NAV_LINKS.map((link) => (
                <Link
                  key={link.href}
                  to={link.href}
                  onClick={() => setOpen(false)}
                  className={cn(
                    'px-4 py-3 rounded-[var(--radius-md)] text-base font-medium transition-colors',
                    isActive(link.href)
                      ? 'text-[var(--color-primary)] bg-[var(--color-secondary)]'
                      : 'text-[var(--color-text-muted)] hover:text-[var(--color-text)] hover:bg-[var(--color-surface-2)]'
                  )}
                >
                  {link.label}
                </Link>
              ))}
              <div className="mt-4 flex flex-col gap-2">
                <Link to="/login" onClick={() => setOpen(false)}>
                  <Button variant="outline" className="w-full">Log in</Button>
                </Link>
                <Link to="/signup" onClick={() => setOpen(false)}>
                  <Button className="w-full">Get Started</Button>
                </Link>
              </div>
            </div>
          </SheetContent>
        </Sheet>
      </div>
    </header>
  )
}
```

---

## 4. Footer {#footer}

```tsx
import { Link } from 'react-router-dom'
import { Github, Twitter, Linkedin, Mail } from 'lucide-react'

const FOOTER_LINKS = {
  Product:  [{ label: 'Features', href: '/services' }, { label: 'Pricing', href: '#' }, { label: 'Changelog', href: '#' }],
  Company:  [{ label: 'About',    href: '/about' },    { label: 'Blog',    href: '#' }, { label: 'Careers',   href: '#' }],
  Support:  [{ label: 'Contact',  href: '/contact' },  { label: 'Docs',    href: '#' }, { label: 'Status',    href: '#' }],
}

export default function Footer() {
  return (
    <footer className="bg-[var(--color-surface)] border-t border-[var(--color-border)]">
      <div className="container py-16">
        {/* Top grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-10 lg:gap-16">
          {/* Brand col */}
          <div className="col-span-2 md:col-span-1">
            <span className="font-display font-bold text-xl text-[var(--color-text)]">BrandName</span>
            <p className="mt-3 text-sm text-[var(--color-text-muted)] leading-relaxed max-w-xs">
              Short brand description goes here. One or two sentences max.
            </p>
            <div className="mt-5 flex gap-4">
              {[Twitter, Github, Linkedin, Mail].map((Icon, i) => (
                <a key={i} href="#" className="text-[var(--color-text-subtle)] hover:text-[var(--color-primary)] transition-colors">
                  <Icon className="w-4 h-4" />
                </a>
              ))}
            </div>
          </div>

          {/* Link cols */}
          {Object.entries(FOOTER_LINKS).map(([section, links]) => (
            <div key={section}>
              <h4 className="text-xs font-semibold uppercase tracking-widest text-[var(--color-text-subtle)] mb-4">
                {section}
              </h4>
              <ul className="space-y-2.5">
                {links.map((link) => (
                  <li key={link.label}>
                    <Link
                      to={link.href}
                      className="text-sm text-[var(--color-text-muted)] hover:text-[var(--color-text)] transition-colors"
                    >
                      {link.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Bottom bar */}
        <div className="mt-12 pt-6 border-t border-[var(--color-border)] flex flex-col sm:flex-row items-center justify-between gap-4">
          <p className="text-xs text-[var(--color-text-subtle)]">
            © {new Date().getFullYear()} BrandName. All rights reserved.
          </p>
          <div className="flex gap-6">
            {['Privacy Policy', 'Terms of Service', 'Cookie Policy'].map((item) => (
              <a key={item} href="#" className="text-xs text-[var(--color-text-subtle)] hover:text-[var(--color-text)] transition-colors">
                {item}
              </a>
            ))}
          </div>
        </div>
      </div>
    </footer>
  )
}
```

---

## 5. HomePage {#home}

```tsx
import { motion } from 'framer-motion'
import { ArrowRight, Star, CheckCircle } from 'lucide-react'
import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent } from '@/components/ui/card'

const FEATURES = [
  { icon: '⚡', title: 'Feature One',   description: 'Short description of what this feature does for the user.' },
  { icon: '🎯', title: 'Feature Two',   description: 'Short description of what this feature does for the user.' },
  { icon: '🛡️', title: 'Feature Three', description: 'Short description of what this feature does for the user.' },
  // Add more as needed
]

const TESTIMONIALS = [
  { name: 'Alex Chen',    role: 'CTO, Startup Inc.',    body: 'This product transformed how our team works.', rating: 5 },
  { name: 'Priya Sharma', role: 'Product Lead, Acme',   body: 'Incredibly intuitive — onboarding took minutes.', rating: 5 },
  { name: 'James Wright', role: 'Founder, CloudBase',   body: 'Worth every penny. The ROI was immediate.', rating: 5 },
]

const STEPS = [
  { step: '01', title: 'Sign Up',         desc: 'Create your account in seconds.' },
  { step: '02', title: 'Configure',       desc: 'Set up your workspace to fit your needs.' },
  { step: '03', title: 'Launch',          desc: 'Go live and start seeing results.' },
]

export default function HomePage() {
  return (
    <div className="overflow-x-hidden">
      {/* ─── HERO ─── */}
      <section className="relative min-h-screen flex items-center pt-20">
        {/* Background decoration — customize per design style */}
        <div className="absolute inset-0 -z-10 bg-gradient-to-br from-[var(--color-background)] via-[var(--color-surface)] to-[var(--color-background)]" />

        <div className="container">
          <motion.div
            className="max-w-4xl"
            initial="hidden"
            animate="show"
            variants={{ hidden: {}, show: { transition: { staggerChildren: 0.12 } } }}
          >
            <motion.div variants={{ hidden: { opacity: 0, y: 20 }, show: { opacity: 1, y: 0 } }}>
              <Badge variant="outline" className="mb-6 text-[var(--color-primary)]">
                ✦ Announcing our latest feature
              </Badge>
            </motion.div>

            <motion.h1
              className="text-[var(--text-5xl)] sm:text-[var(--text-6xl)] lg:text-[var(--text-7xl)] font-display font-bold leading-tight text-[var(--color-text)]"
              variants={{ hidden: { opacity: 0, y: 30 }, show: { opacity: 1, y: 0 } }}
            >
              Your Compelling{' '}
              <span className="text-[var(--color-primary)]">Headline Here</span>
            </motion.h1>

            <motion.p
              className="mt-6 text-[var(--text-lg)] lg:text-[var(--text-xl)] text-[var(--color-text-muted)] max-w-2xl leading-relaxed"
              variants={{ hidden: { opacity: 0, y: 20 }, show: { opacity: 1, y: 0 } }}
            >
              Subheadline that explains what the product does and who it's for in 1-2 sentences.
              Keep it punchy and benefit-focused.
            </motion.p>

            <motion.div
              className="mt-10 flex flex-wrap gap-4"
              variants={{ hidden: { opacity: 0, y: 20 }, show: { opacity: 1, y: 0 } }}
            >
              <Link to="/signup">
                <Button size="lg" className="gap-2">
                  Get Started Free <ArrowRight className="w-4 h-4" />
                </Button>
              </Link>
              <Button size="lg" variant="outline">Watch Demo</Button>
            </motion.div>

            <motion.p
              className="mt-5 text-sm text-[var(--color-text-subtle)]"
              variants={{ hidden: { opacity: 0 }, show: { opacity: 1 } }}
            >
              No credit card required · Free plan available · Cancel anytime
            </motion.p>
          </motion.div>
        </div>
      </section>

      {/* ─── SOCIAL PROOF STRIP ─── */}
      <section className="border-y border-[var(--color-border)] bg-[var(--color-surface)] py-8">
        <div className="container">
          <p className="text-center text-sm text-[var(--color-text-subtle)] uppercase tracking-widest mb-6">
            Trusted by teams at
          </p>
          <div className="flex flex-wrap justify-center gap-10 items-center opacity-60">
            {['Company A', 'Company B', 'Company C', 'Company D', 'Company E'].map((c) => (
              <span key={c} className="text-[var(--color-text-muted)] font-display font-semibold text-lg">{c}</span>
            ))}
          </div>
        </div>
      </section>

      {/* ─── FEATURES ─── */}
      <section className="section">
        <div className="container">
          <div className="text-center max-w-2xl mx-auto mb-16">
            <p className="text-sm font-semibold uppercase tracking-widest text-[var(--color-primary)] mb-3">Features</p>
            <h2 className="text-[var(--text-4xl)] font-display font-bold">Everything you need</h2>
            <p className="mt-4 text-[var(--color-text-muted)] text-[var(--text-lg)]">
              Section subtitle explaining the value of these features.
            </p>
          </div>

          <motion.div
            className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6"
            initial="hidden"
            whileInView="show"
            viewport={{ once: true, margin: '-50px' }}
            variants={{ hidden: {}, show: { transition: { staggerChildren: 0.1 } } }}
          >
            {FEATURES.map((f) => (
              <motion.div
                key={f.title}
                variants={{ hidden: { opacity: 0, y: 24 }, show: { opacity: 1, y: 0 } }}
              >
                <Card className="h-full border-[var(--color-border)] bg-[var(--color-surface)] hover:border-[var(--color-primary)] transition-colors">
                  <CardContent className="p-6">
                    <span className="text-3xl mb-4 block">{f.icon}</span>
                    <h3 className="text-[var(--text-xl)] font-display font-semibold mb-2">{f.title}</h3>
                    <p className="text-[var(--color-text-muted)] text-sm leading-relaxed">{f.description}</p>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* ─── HOW IT WORKS ─── */}
      <section className="section bg-[var(--color-surface)]">
        <div className="container">
          <div className="text-center max-w-xl mx-auto mb-16">
            <p className="text-sm font-semibold uppercase tracking-widest text-[var(--color-primary)] mb-3">Process</p>
            <h2 className="text-[var(--text-4xl)] font-display font-bold">How it works</h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 lg:gap-12">
            {STEPS.map((s, i) => (
              <div key={s.step} className="text-center">
                <div className="w-12 h-12 rounded-[var(--radius-full)] bg-[var(--color-primary)] text-[var(--color-primary-fg)] flex items-center justify-center font-display font-bold mx-auto mb-4">
                  {i + 1}
                </div>
                <h3 className="text-[var(--text-xl)] font-display font-semibold mb-2">{s.title}</h3>
                <p className="text-[var(--color-text-muted)] text-sm">{s.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ─── TESTIMONIALS ─── */}
      <section className="section">
        <div className="container">
          <div className="text-center max-w-xl mx-auto mb-16">
            <h2 className="text-[var(--text-4xl)] font-display font-bold">What people say</h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {TESTIMONIALS.map((t) => (
              <Card key={t.name} className="border-[var(--color-border)] bg-[var(--color-surface)]">
                <CardContent className="p-6">
                  <div className="flex gap-0.5 mb-4">
                    {Array.from({ length: t.rating }).map((_, i) => (
                      <Star key={i} className="w-4 h-4 fill-[var(--color-accent)] text-[var(--color-accent)]" />
                    ))}
                  </div>
                  <p className="text-[var(--color-text-muted)] text-sm leading-relaxed mb-4">"{t.body}"</p>
                  <div>
                    <p className="font-semibold text-sm">{t.name}</p>
                    <p className="text-xs text-[var(--color-text-subtle)]">{t.role}</p>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* ─── FINAL CTA ─── */}
      <section className="section bg-[var(--color-primary)]">
        <div className="container text-center">
          <h2 className="text-[var(--text-4xl)] font-display font-bold text-[var(--color-primary-fg)]">
            Ready to get started?
          </h2>
          <p className="mt-4 text-[var(--color-primary-fg)] opacity-80 text-[var(--text-lg)] max-w-xl mx-auto">
            Join thousands of teams already using this product.
          </p>
          <div className="mt-8 flex flex-wrap gap-4 justify-center">
            <Link to="/signup">
              <Button size="lg" variant="secondary" className="gap-2">
                Start for free <ArrowRight className="w-4 h-4" />
              </Button>
            </Link>
            <Link to="/contact">
              <Button size="lg" variant="outline" className="border-[var(--color-primary-fg)] text-[var(--color-primary-fg)]">
                Talk to sales
              </Button>
            </Link>
          </div>
        </div>
      </section>
    </div>
  )
}
```

---

## 6. AboutPage {#about}

```tsx
import { motion } from 'framer-motion'
import { Target, Eye, Heart, Zap } from 'lucide-react'

const TEAM = [
  { name: 'Jane Doe',   role: 'CEO & Co-Founder',     initials: 'JD' },
  { name: 'John Smith', role: 'CTO & Co-Founder',     initials: 'JS' },
  { name: 'Ava Patel',  role: 'Head of Design',       initials: 'AP' },
  { name: 'Mike Chen',  role: 'Head of Engineering',  initials: 'MC' },
]

const VALUES = [
  { icon: Target, title: 'Mission-driven',  desc: 'We build with purpose, not profit alone.' },
  { icon: Eye,    title: 'Transparent',     desc: 'No black boxes — our work speaks for itself.' },
  { icon: Heart,  title: 'Human-first',     desc: 'Every decision starts with user empathy.' },
  { icon: Zap,    title: 'Relentlessly fast', desc: 'We ship, learn, and iterate without delay.' },
]

export default function AboutPage() {
  return (
    <div className="pt-20">
      {/* Hero */}
      <section className="section">
        <div className="container max-w-3xl">
          <motion.div initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
            <p className="text-sm font-semibold uppercase tracking-widest text-[var(--color-primary)] mb-3">About Us</p>
            <h1 className="text-[var(--text-5xl)] font-display font-bold mb-6">
              We're building something worth using
            </h1>
            <p className="text-[var(--text-lg)] text-[var(--color-text-muted)] leading-relaxed">
              Brand story paragraph. Who you are, why you started, what drives you.
              Keep it personal and authentic — 3–4 sentences maximum for the opener.
            </p>
          </motion.div>
        </div>
      </section>

      {/* Mission / Vision */}
      <section className="section bg-[var(--color-surface)]">
        <div className="container">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
            <div>
              <h2 className="text-[var(--text-3xl)] font-display font-bold mb-4">Our Mission</h2>
              <p className="text-[var(--color-text-muted)] leading-relaxed">
                One clear sentence stating the mission. Then 2–3 sentences of elaboration.
              </p>
            </div>
            <div>
              <h2 className="text-[var(--text-3xl)] font-display font-bold mb-4">Our Vision</h2>
              <p className="text-[var(--color-text-muted)] leading-relaxed">
                Where you're going. The world you're trying to create. Aspirational but grounded.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Values */}
      <section className="section">
        <div className="container">
          <h2 className="text-[var(--text-4xl)] font-display font-bold mb-12 text-center">What we believe in</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
            {VALUES.map(({ icon: Icon, title, desc }) => (
              <div key={title} className="text-center">
                <div className="w-12 h-12 rounded-[var(--radius-lg)] bg-[var(--color-secondary)] flex items-center justify-center mx-auto mb-4">
                  <Icon className="w-6 h-6 text-[var(--color-primary)]" />
                </div>
                <h3 className="font-display font-semibold mb-2">{title}</h3>
                <p className="text-sm text-[var(--color-text-muted)]">{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Team */}
      <section className="section bg-[var(--color-surface)]">
        <div className="container">
          <h2 className="text-[var(--text-4xl)] font-display font-bold mb-12 text-center">The team</h2>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-8">
            {TEAM.map((member) => (
              <div key={member.name} className="text-center">
                <div className="w-20 h-20 rounded-[var(--radius-full)] bg-[var(--color-primary)] text-[var(--color-primary-fg)] flex items-center justify-center font-display font-bold text-xl mx-auto mb-4">
                  {member.initials}
                </div>
                <p className="font-semibold">{member.name}</p>
                <p className="text-sm text-[var(--color-text-muted)]">{member.role}</p>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  )
}
```

---

## 7. ServicesPage {#services}

```tsx
import { motion } from 'framer-motion'
import { ArrowRight } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Link } from 'react-router-dom'

// ← ALWAYS data-driven. Adapt length and content to the project.
const SERVICES = [
  {
    id: 1,
    icon: '🎯',
    title: 'Service One',
    description: 'Full description of this service. What it includes, who it\'s for, and the benefit delivered.',
    features: ['Feature A', 'Feature B', 'Feature C'],
  },
  {
    id: 2,
    icon: '⚙️',
    title: 'Service Two',
    description: 'Full description of this service.',
    features: ['Feature A', 'Feature B', 'Feature C'],
  },
  // Add more entries from user input
]

const DIFFERENTIATORS = [
  { stat: '99.9%', label: 'Uptime SLA' },
  { stat: '10x',   label: 'Faster delivery' },
  { stat: '500+',  label: 'Happy clients' },
  { stat: '24/7',  label: 'Support' },
]

export default function ServicesPage() {
  return (
    <div className="pt-20">
      {/* Hero */}
      <section className="section text-center">
        <div className="container max-w-2xl mx-auto">
          <p className="text-sm font-semibold uppercase tracking-widest text-[var(--color-primary)] mb-3">Services</p>
          <h1 className="text-[var(--text-5xl)] font-display font-bold mb-6">What we offer</h1>
          <p className="text-[var(--text-lg)] text-[var(--color-text-muted)]">
            Brief description of the services section — the range of what you do.
          </p>
        </div>
      </section>

      {/* Services Grid — dynamic from SERVICES array */}
      <section className="section">
        <div className="container">
          <motion.div
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
            initial="hidden"
            whileInView="show"
            viewport={{ once: true }}
            variants={{ hidden: {}, show: { transition: { staggerChildren: 0.1 } } }}
          >
            {SERVICES.map((service) => (
              <motion.div
                key={service.id}
                variants={{ hidden: { opacity: 0, y: 24 }, show: { opacity: 1, y: 0 } }}
              >
                <Card className="h-full border-[var(--color-border)] bg-[var(--color-surface)] hover:shadow-[var(--shadow-md)] transition-all">
                  <CardContent className="p-6 flex flex-col h-full">
                    <span className="text-4xl mb-4 block">{service.icon}</span>
                    <h3 className="text-[var(--text-xl)] font-display font-semibold mb-3">{service.title}</h3>
                    <p className="text-[var(--color-text-muted)] text-sm leading-relaxed mb-5 flex-1">
                      {service.description}
                    </p>
                    <ul className="space-y-1.5 mb-6">
                      {service.features.map((f) => (
                        <li key={f} className="flex items-center gap-2 text-sm text-[var(--color-text-muted)]">
                          <span className="w-1.5 h-1.5 rounded-full bg-[var(--color-primary)]" />
                          {f}
                        </li>
                      ))}
                    </ul>
                    <Button variant="outline" size="sm" className="gap-2 w-full mt-auto">
                      Learn more <ArrowRight className="w-4 h-4" />
                    </Button>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* Why Us */}
      <section className="section bg-[var(--color-surface)]">
        <div className="container">
          <h2 className="text-[var(--text-4xl)] font-display font-bold text-center mb-12">Why choose us</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
            {DIFFERENTIATORS.map((d) => (
              <div key={d.label}>
                <p className="text-[var(--text-4xl)] font-display font-bold text-[var(--color-primary)]">{d.stat}</p>
                <p className="text-sm text-[var(--color-text-muted)] mt-1">{d.label}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="section text-center">
        <div className="container max-w-xl mx-auto">
          <h2 className="text-[var(--text-4xl)] font-display font-bold mb-4">Ready to begin?</h2>
          <p className="text-[var(--color-text-muted)] mb-8">Contact us to discuss your project.</p>
          <Link to="/contact">
            <Button size="lg" className="gap-2">Get in touch <ArrowRight className="w-4 h-4" /></Button>
          </Link>
        </div>
      </section>
    </div>
  )
}
```

---

## 8. ContactPage {#contact}

```tsx
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import { MapPin, Mail, Phone, Clock } from 'lucide-react'

export default function ContactPage() {
  const [form, setForm] = useState({ name: '', email: '', subject: '', message: '' })
  const [status, setStatus] = useState<'idle' | 'loading' | 'success'>('idle')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setStatus('loading')
    // Replace with actual submission logic
    await new Promise(r => setTimeout(r, 1000))
    setStatus('success')
  }

  return (
    <div className="pt-20">
      <section className="section">
        <div className="container">
          <div className="max-w-xl mb-12">
            <p className="text-sm font-semibold uppercase tracking-widest text-[var(--color-primary)] mb-3">Contact</p>
            <h1 className="text-[var(--text-5xl)] font-display font-bold mb-4">Let's talk</h1>
            <p className="text-[var(--color-text-muted)] text-[var(--text-lg)]">
              Fill in the form and we'll get back to you within 24 hours.
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-5 gap-12">
            {/* Form — spans 3 cols */}
            <form onSubmit={handleSubmit} className="lg:col-span-3 space-y-5">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="space-y-1.5">
                  <Label htmlFor="name">Name</Label>
                  <Input id="name" placeholder="Your name" value={form.name}
                    onChange={(e) => setForm(f => ({ ...f, name: e.target.value }))} required />
                </div>
                <div className="space-y-1.5">
                  <Label htmlFor="email">Email</Label>
                  <Input id="email" type="email" placeholder="you@example.com" value={form.email}
                    onChange={(e) => setForm(f => ({ ...f, email: e.target.value }))} required />
                </div>
              </div>
              <div className="space-y-1.5">
                <Label htmlFor="subject">Subject</Label>
                <Input id="subject" placeholder="How can we help?" value={form.subject}
                  onChange={(e) => setForm(f => ({ ...f, subject: e.target.value }))} required />
              </div>
              <div className="space-y-1.5">
                <Label htmlFor="message">Message</Label>
                <Textarea id="message" placeholder="Tell us more..." rows={6} value={form.message}
                  onChange={(e) => setForm(f => ({ ...f, message: e.target.value }))} required />
              </div>
              <Button type="submit" size="lg" className="w-full" disabled={status === 'loading'}>
                {status === 'loading' ? 'Sending...' : status === 'success' ? '✓ Sent!' : 'Send Message'}
              </Button>
            </form>

            {/* Contact info — spans 2 cols */}
            <div className="lg:col-span-2 space-y-8">
              {[
                { icon: Mail,   label: 'Email',   value: 'hello@brand.com' },
                { icon: Phone,  label: 'Phone',   value: '+1 (555) 000-0000' },
                { icon: MapPin, label: 'Address', value: '123 Main St, City, Country' },
                { icon: Clock,  label: 'Hours',   value: 'Mon–Fri, 9am–6pm' },
              ].map(({ icon: Icon, label, value }) => (
                <div key={label} className="flex gap-4">
                  <div className="w-10 h-10 rounded-[var(--radius-lg)] bg-[var(--color-secondary)] flex items-center justify-center shrink-0">
                    <Icon className="w-5 h-5 text-[var(--color-primary)]" />
                  </div>
                  <div>
                    <p className="text-xs uppercase tracking-widest text-[var(--color-text-subtle)] mb-0.5">{label}</p>
                    <p className="text-[var(--color-text)]">{value}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}
```

---

## 9. LoginPage {#login}

```tsx
import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Separator } from '@/components/ui/separator'

export default function LoginPage() {
  const [form, setForm] = useState({ email: '', password: '' })

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-12 bg-[var(--color-background)]">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <Link to="/" className="font-display font-bold text-2xl text-[var(--color-text)]">BrandName</Link>
          <p className="mt-2 text-[var(--color-text-muted)]">Welcome back</p>
        </div>

        <div className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-[var(--radius-xl)] p-8 shadow-[var(--shadow-md)]">
          <form className="space-y-5" onSubmit={(e) => e.preventDefault()}>
            <div className="space-y-1.5">
              <Label htmlFor="email">Email address</Label>
              <Input id="email" type="email" placeholder="you@example.com" autoComplete="email"
                value={form.email} onChange={(e) => setForm(f => ({ ...f, email: e.target.value }))} required />
            </div>
            <div className="space-y-1.5">
              <div className="flex items-center justify-between">
                <Label htmlFor="password">Password</Label>
                <a href="#" className="text-xs text-[var(--color-primary)] hover:underline">Forgot password?</a>
              </div>
              <Input id="password" type="password" placeholder="••••••••" autoComplete="current-password"
                value={form.password} onChange={(e) => setForm(f => ({ ...f, password: e.target.value }))} required />
            </div>
            <Button type="submit" className="w-full" size="lg">Sign in</Button>
          </form>

          <div className="my-6 flex items-center gap-3">
            <Separator className="flex-1" />
            <span className="text-xs text-[var(--color-text-subtle)]">or continue with</span>
            <Separator className="flex-1" />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <Button variant="outline" className="gap-2">
              <svg className="w-4 h-4" viewBox="0 0 24 24"><path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/><path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/><path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/><path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/></svg>
              Google
            </Button>
            <Button variant="outline" className="gap-2">
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0 0 24 12c0-6.63-5.37-12-12-12z"/></svg>
              GitHub
            </Button>
          </div>

          <p className="mt-6 text-center text-sm text-[var(--color-text-muted)]">
            Don't have an account?{' '}
            <Link to="/signup" className="text-[var(--color-primary)] hover:underline font-medium">Sign up</Link>
          </p>
        </div>
      </div>
    </div>
  )
}
```

---

## 10. SignupPage {#signup}

```tsx
import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Checkbox } from '@/components/ui/checkbox'

export default function SignupPage() {
  const [agreed, setAgreed] = useState(false)

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-12 bg-[var(--color-background)]">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <Link to="/" className="font-display font-bold text-2xl text-[var(--color-text)]">BrandName</Link>
          <p className="mt-2 text-[var(--color-text-muted)]">Create your account</p>
        </div>

        <div className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-[var(--radius-xl)] p-8 shadow-[var(--shadow-md)]">
          <form className="space-y-5" onSubmit={(e) => e.preventDefault()}>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1.5">
                <Label htmlFor="first">First name</Label>
                <Input id="first" placeholder="Jane" required />
              </div>
              <div className="space-y-1.5">
                <Label htmlFor="last">Last name</Label>
                <Input id="last" placeholder="Doe" required />
              </div>
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="email">Email address</Label>
              <Input id="email" type="email" placeholder="you@example.com" required />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="password">Password</Label>
              <Input id="password" type="password" placeholder="Min. 8 characters" required />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="confirm">Confirm password</Label>
              <Input id="confirm" type="password" placeholder="Repeat password" required />
            </div>
            <div className="flex items-start gap-3">
              <Checkbox id="terms" checked={agreed} onCheckedChange={(v) => setAgreed(!!v)} />
              <Label htmlFor="terms" className="text-sm text-[var(--color-text-muted)] leading-relaxed cursor-pointer">
                I agree to the{' '}
                <a href="#" className="text-[var(--color-primary)] hover:underline">Terms of Service</a>
                {' '}and{' '}
                <a href="#" className="text-[var(--color-primary)] hover:underline">Privacy Policy</a>
              </Label>
            </div>
            <Button type="submit" className="w-full" size="lg" disabled={!agreed}>
              Create account
            </Button>
          </form>

          <p className="mt-6 text-center text-sm text-[var(--color-text-muted)]">
            Already have an account?{' '}
            <Link to="/login" className="text-[var(--color-primary)] hover:underline font-medium">Sign in</Link>
          </p>
        </div>
      </div>
    </div>
  )
}
```

---

## 11. theme.ts {#theme}

```ts
// src/lib/theme.ts
// Programmatic access to design tokens (for JS-driven animations, charts, etc.)

export const theme = {
  colors: {
    primary:        'var(--color-primary)',
    primaryHover:   'var(--color-primary-hover)',
    primaryFg:      'var(--color-primary-fg)',
    secondary:      'var(--color-secondary)',
    accent:         'var(--color-accent)',
    background:     'var(--color-background)',
    surface:        'var(--color-surface)',
    border:         'var(--color-border)',
    text:           'var(--color-text)',
    textMuted:      'var(--color-text-muted)',
    textSubtle:     'var(--color-text-subtle)',
  },
  fonts: {
    display: 'var(--font-display)',
    body:    'var(--font-body)',
    mono:    'var(--font-mono)',
  },
  radius: {
    sm:   'var(--radius-sm)',
    md:   'var(--radius-md)',
    lg:   'var(--radius-lg)',
    xl:   'var(--radius-xl)',
    full: 'var(--radius-full)',
  },
  shadow: {
    sm: 'var(--shadow-sm)',
    md: 'var(--shadow-md)',
    lg: 'var(--shadow-lg)',
  },
} as const

export type Theme = typeof theme
```