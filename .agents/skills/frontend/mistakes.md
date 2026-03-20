---
name: frontend-mistakes
description: Living log of 20 known frontend failure patterns and anti-patterns — hardcoded colors, wrong font sizes, missing mobile nav, broken auth page layout, form tag misuse, and more. Always check this file before finalizing any frontend output. Update it when new mistakes are discovered.
---

# Mistakes Log

A living record of known failure patterns, anti-patterns, and common errors.
**Check this file before finalizing any frontend output.**
Update this file whenever a new mistake is identified.

---

## M-001 · Hardcoded colors in JSX
**Mistake**: Writing `className="bg-blue-500 text-white"` or `style={{ color: '#3b82f6' }}` directly.  
**Why it breaks**: Ignores the theme system; breaks dark/light mode; inconsistent across components.  
**Fix**: Always use CSS variable tokens: `bg-[var(--color-primary)] text-[var(--color-primary-fg)]`  
**Status**: ACTIVE — check every component

---

## M-002 · Raw pixel font sizes
**Mistake**: `style={{ fontSize: '32px' }}` or custom Tailwind values like `text-[32px]`.  
**Why it breaks**: Bypasses the fixed type scale; breaks responsive scaling; inconsistent hierarchy.  
**Fix**: Use only the CSS variable scale: `text-[var(--text-4xl)]` or Tailwind mapped values.  
**Status**: ACTIVE

---

## M-003 · Services page with hardcoded JSX cards
**Mistake**: Writing `<Card>Service 1...</Card> <Card>Service 2...</Card>` individually in JSX.  
**Why it breaks**: Adding/removing services requires editing JSX structure; not maintainable.  
**Fix**: Always define a `SERVICES` array and render with `.map()`. Consult templates.md §7.  
**Status**: ACTIVE

---

## M-004 · Missing mobile Navbar
**Mistake**: Building desktop nav but omitting mobile hamburger menu.  
**Why it breaks**: Nav links unreachable on mobile; critical UX failure.  
**Fix**: Always include `Sheet` component from shadcn for mobile drawer. Consult templates.md §3.  
**Status**: ACTIVE

---

## M-005 · Importing shadcn components without proper initialization
**Mistake**: `import { Button } from '@/components/ui/button'` when the component hasn't been added.  
**Why it breaks**: Runtime import error.  
**Fix**: Always remind user to run `npx shadcn@latest add [component]` OR include the component code inline if scaffolding a complete project.  
**Status**: ACTIVE

---

## M-006 · Missing `pt-20` on all pages
**Mistake**: Page content starts at top of viewport, hidden under fixed Navbar.  
**Why it breaks**: First section of every page is partially obscured by the sticky navbar.  
**Fix**: All page root divs must have `pt-20` (5rem = 80px, matching navbar height). Auth pages use `min-h-screen flex items-center` instead.  
**Status**: ACTIVE

---

## M-007 · Using `<form>` HTML element in React artifacts
**Mistake**: `<form onSubmit={...}>` in React components inside Claude.ai artifacts.  
**Why it breaks**: Artifacts don't support native HTML form submission; causes errors.  
**Fix**: Handle submit via `<button onClick={handleSubmit}>`. Do NOT use `<form>` tags in artifact mode.  
**Status**: ACTIVE — artifact mode only

---

## M-008 · Font not applied to heading elements
**Mistake**: Heading fonts default to `font-body` because only `body {}` sets `--font-body`.  
**Why it breaks**: Display font is not applied to `h1`–`h6`; loses typographic hierarchy.  
**Fix**: Always include in globals.css: `h1, h2, h3, h4, h5, h6 { font-family: var(--font-display); }`  
**Status**: ACTIVE

---

## M-009 · Forgetting `display=swap` in Google Fonts URL
**Mistake**: `@import url('...?family=Syne:wght@400;700')` without `&display=swap`.  
**Why it breaks**: Text invisible during font load (FOIT — Flash of Invisible Text); poor CLS score.  
**Fix**: Always append `&display=swap` to every Google Fonts import URL.  
**Status**: ACTIVE

---

## M-010 · Navbar not sticky / fixed
**Mistake**: Navbar rendered in normal document flow (no `position: fixed/sticky`).  
**Why it breaks**: Navbar scrolls away; standard UX expectation not met.  
**Fix**: Always apply `className="fixed top-0 left-0 right-0 z-50"` to the `<header>` element.  
**Status**: ACTIVE

---

## M-011 · Footer not at bottom of page
**Mistake**: Footer renders mid-page when content is short.  
**Why it breaks**: Looks broken on pages with little content (Login, Contact).  
**Fix**: App root wrapper must be `min-h-screen flex flex-col`. `<main>` must have `flex-1`. Footer has no flex setting (stays at bottom).  
**Status**: ACTIVE

---

## M-012 · Using `Inter` or `Roboto` as display font
**Mistake**: Defaulting to Inter, Roboto, or system-ui for the display/heading font.  
**Why it breaks**: Generic AI aesthetic; fails the "distinctive design" requirement.  
**Fix**: Always pick a distinctive display font from fonts.md. Never use Inter, Roboto, or Arial as `--font-display`.  
**Status**: ACTIVE

---

## M-013 · Omitting `viewport={{ once: true }}` on Framer motion
**Mistake**: `<motion.div whileInView={...}>` without `viewport={{ once: true }}`.  
**Why it breaks**: Animation replays every time user scrolls back up; feels cheap.  
**Fix**: Always include `viewport={{ once: true, margin: '-50px' }}` on scroll-triggered animations.  
**Status**: ACTIVE

---

## M-014 · Container max-width not applied
**Mistake**: Content spans full viewport width on large screens.  
**Why it breaks**: Readability failure on 1440px+ screens; lines become too wide.  
**Fix**: Always wrap section content in `<div className="container">` which maps to `max-w-7xl mx-auto px-4 sm:px-6 lg:px-8`.  
**Status**: ACTIVE

---

## M-015 · Auth pages (Login/Signup) including Navbar + Footer
**Mistake**: Rendering the main Navbar and Footer on Login/Signup pages.  
**Why it breaks**: Auth pages should be standalone, focused, distraction-free.  
**Fix**: Two approaches — (a) use a separate `AuthLayout` without nav/footer, or (b) conditionally hide nav on `/login` and `/signup` routes using `useLocation`.  
**Status**: ACTIVE

---

## M-016 · Missing `cn()` utility import
**Mistake**: Manually concatenating classNames with template literals instead of `cn()`.  
**Why it breaks**: Conditional classes become unwieldy; class deduplication fails.  
**Fix**: Always import `import { cn } from '@/lib/utils'` and use `cn(...)` for all conditional/merged classNames.  
**Status**: ACTIVE

---

## M-017 · Design style CSS not reflected in components
**Mistake**: Choosing "Neobrutalism" in Step 2 but generating rounded, shadow-soft cards.  
**Why it breaks**: Design direction and code are inconsistent; the product looks generic.  
**Fix**: After choosing a design style from design-styles.md, apply its CSS patterns to every component. Neobrutalism → `border: 2px solid #000; border-radius: 0; box-shadow: 4px 4px 0 #000`.  
**Status**: ACTIVE

---

## M-018 · Social links in Footer pointing to `href="#"`
**Mistake**: All social icons link to `#` placeholder.  
**Why it breaks**: Minor but acceptable for scaffolds. Must be flagged as TODOs.  
**Fix**: Always add a `{/* TODO: Replace # with actual social URLs */}` comment. Better: accept social URLs as props to Footer.  
**Status**: INFO — always comment

---

## M-019 · Checkbox in Signup not wiring to submit button disabled state
**Mistake**: Terms checkbox exists but Submit button is always enabled.  
**Why it breaks**: User can submit without agreeing to terms; legal/UX issue.  
**Fix**: `disabled={!agreed}` on the submit button, where `agreed` is state from the Checkbox `onCheckedChange`.  
**Status**: ACTIVE

---

## M-020 · Using `localStorage` in Claude.ai artifacts
**Mistake**: Calling `localStorage.setItem(...)` inside artifact code.  
**Why it breaks**: `localStorage` is blocked in Claude.ai artifact sandbox.  
**Fix**: Use React state (`useState`) for all in-session data. If persistence is needed, use the Storage API (`window.storage`).  
**Status**: ACTIVE — artifact mode only

---

## M-021 · Animating layout properties instead of transform/opacity
**Mistake**: `animate={{ width: '100%' }}` or `animate={{ height: 'auto', marginTop: 20 }}`.  
**Why it breaks**: Triggers browser layout reflow on every frame — causes jank, especially on mobile. Fails Lighthouse performance audit.  
**Fix**: Only animate `x`, `y`, `scale`, `rotate`, `opacity`. For height reveals use `AnimatePresence` with `height: 0 → 'auto'` scoped to the content wrapper only (as in the Accordion pattern in animations.md §13).  
**Status**: ACTIVE

---

## M-022 · Missing `viewport={{ once: true }}` on whileInView
**Mistake**: `<motion.div whileInView={{ opacity: 1, y: 0 }}>` without `viewport={{ once: true }}`.  
**Why it breaks**: Animation replays every time the user scrolls back up — feels cheap and amateurish.  
**Fix**: Always include `viewport={{ once: true, margin: '-60px' }}` on every `whileInView`.  
**Status**: ACTIVE

---

## M-023 · GSAP without context — memory leaks on unmount
**Mistake**: Calling `gsap.to(ref.current, { ... })` directly inside `useEffect` without `gsap.context()`.  
**Why it breaks**: GSAP animations and ScrollTriggers persist after the component unmounts — memory leak, stale DOM references, broken scroll positions on navigation.  
**Fix**: Always wrap in `const ctx = gsap.context(() => { ... }, ref)` and return `() => ctx.revert()`.  
**Status**: ACTIVE

---

## M-024 · Missing `AnimatePresence` for page transitions
**Mistake**: Wrapping routes in `motion.div` but forgetting `AnimatePresence` around `<Routes>`.  
**Why it breaks**: Exit animations never fire — pages just snap-cut instead of transitioning.  
**Fix**: Wrap `<Routes>` in `<AnimatePresence mode="wait">` and pass `location` + `key={location.pathname}` to `<Routes>`. See animations.md §1.  
**Status**: ACTIVE

---

## M-025 · Not honoring `prefers-reduced-motion`
**Mistake**: No reduced-motion handling anywhere in the project.  
**Why it breaks**: Users with vestibular disorders, epilepsy, or motion sensitivity experience harmful or nauseating animations. Also fails WCAG 2.1 success criterion 2.3.3.  
**Fix**: Add to `globals.css`:
```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation-duration: 0.01ms !important; transition-duration: 0.01ms !important; }
}
```
And in Framer Motion: `const reduced = useReducedMotion()` → swap variants to opacity-only when true.  
**Status**: ACTIVE

---

## M-026 · Forgetting `gsap.registerPlugin(ScrollTrigger)` 
**Mistake**: Using `ScrollTrigger` without registering it first, or registering it in one file but using it in another without re-registering.  
**Why it breaks**: Silent failure — ScrollTrigger just doesn't fire, no console error in some setups.  
**Fix**: Call `gsap.registerPlugin(ScrollTrigger)` at the top of every file that imports and uses ScrollTrigger.  
**Status**: ACTIVE

---

## M-027 · Hero using a single fade-in instead of orchestrated stagger
**Mistake**: `<motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>` wrapping the entire hero at once.  
**Why it breaks**: Entire block appears at once — no narrative hierarchy, no sense of choreography. Looks unpolished.  
**Fix**: Use the orchestrated stagger pattern from animations.md §2 — badge → headline → subheadline → CTA → trust line, each as a separate `variants` child with `staggerChildren`.  
**Status**: ACTIVE

---

## Update Log

| Date | Mistake Added | Source |
|------|--------------|--------|
| Init | M-001 to M-020 | Baseline audit |
| v2   | M-021 to M-027 | Animation system addition |

*When a new mistake is encountered during a project, add it here with the next M-XXX ID, a description, why it breaks things, and the fix.*