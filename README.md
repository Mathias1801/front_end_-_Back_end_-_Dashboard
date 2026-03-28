# Aurum Tempus — Luxury Watch Brand Website Template

> **🔗 Live Preview: [yourusername.github.io/your-repo-name](https://yourusername.github.io/your-repo-name)**
> *(Replace with your actual GitHub Pages URL after deploying)*

---

> ⚠️ **Template Notice:** This is a fictional brand created purely as a frontend portfolio piece. "Aurum Tempus" does not exist as a real company. All copy, products, prices, and brand history are invented. This project is not affiliated with, endorsed by, or in any way connected to any real watchmaker or luxury brand.

---

## Overview

A fully hand-coded, multi-page luxury brand website built as a portfolio/learning template. The brief was a high-end watch brand website indistinguishable from a real six-figure agency build — no frameworks, no component libraries, pure HTML, CSS, and vanilla JavaScript.

The fictional brand **Aurum Tempus** (Geneva, est. 1889) provided the creative canvas. Every design decision — typography, colour, motion, layout — was driven by the luxury horology aesthetic.

---

## Pages

| File | Description |
|---|---|
| `index.html` | Main hub — hero, collections teaser, brand story, live clock feature, stats, email capture |
| `collections.html` | Full filterable product grid with technical spec sheets |
| `heritage.html` | Brand story, interactive timeline, Vallat family tree, brand values |
| `craftsmanship.html` | 8-stage manufacture process, in-house calibre reference, finishing disciplines |
| `contact.html` | Validated enquiry form, 6 global boutique listings, servicing information |
| `styles.css` | Shared stylesheet — full design system via CSS custom properties |
| `script.js` | Shared JavaScript — all interactivity, animations, and utilities |

---

## Technical Highlights

**No frameworks. No build tools. No dependencies.**

- **Live SVG clock** — real-time watch face driven by `Date()`, updating at 50ms intervals with smooth sweeping seconds hand
- **Scroll animations** — `IntersectionObserver` triggers staggered fade/slide reveals and count-up number animations on entry
- **Filterable grid** — vanilla JS tab filtering on the collections page with instant show/hide transitions
- **Custom cursor** — gold dot + ring with lag-follow animation using `requestAnimationFrame`
- **Page transitions** — slide-up overlay on internal link navigation
- **Animated marquee** — pure CSS `@keyframes` infinite scroll
- **Mobile-first responsive** — breakpoints at 1024px, 768px, 480px; hamburger nav with animated state
- **Accessible** — semantic HTML5, `aria-label` throughout, `:focus-visible` states, sufficient contrast ratios
- **CSS custom properties** — full colour system, fonts, transitions defined as variables and used consistently across all pages
- **No placeholder copy** — all text, product specs, and brand history written as if for a real client

---

## Design Decisions

**Typography:** Cormorant Garamond (display/editorial) paired with Montserrat (UI/body) — chosen for the tension between old-world serif gravitas and modern geometric restraint.

**Colour:** Deep espresso browns (`#1a1410`, `#0d0b08`) as the primary canvas, with a warm gold accent system (`#b8933f`, `#d4af6a`, `#f0e6c8`). No blacks, no greys — every shade has warmth.

**Motion:** Restrained and intentional. Slow easing curves (`cubic-bezier(0.25, 0.46, 0.45, 0.94)`), parallax on scroll, float animation on the hero watch. Nothing bounces.

**Layout:** Asymmetric editorial grids, full-bleed feature rows, a CSS noise texture overlay on the hero, and radial gradient "glow" effects behind the watch illustrations — all built without a single external image file.

---

## How to Deploy via GitHub Pages

1. Push all 7 files to the root of a GitHub repository
2. Go to **Settings → Pages**
3. Set Source to your branch (`main`) and folder (`/root`)
4. Save — your live URL will appear within a minute

Update the live preview link at the top of this README with your actual URL.

---

## What I'd Adapt for a Real Client

This template is structured to be repurposed. To adapt it for a real brand:

- Swap the CSS custom properties in `:root` for the brand's colour system
- Replace the inline SVG watch illustrations with real product photography
- Update Google Fonts imports for the brand's chosen typefaces
- Connect the email and contact forms to a backend (e.g. Formspree, Netlify Forms)
- Add a CMS layer (e.g. Eleventy, Astro) for content management if needed

---

## License

This template is shared for portfolio and learning purposes. Feel free to fork, adapt, and use the code structure for your own projects. The fictional "Aurum Tempus" branding, copy, and visual identity should not be used commercially as-is.
