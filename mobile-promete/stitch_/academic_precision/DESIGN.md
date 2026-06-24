---
name: Academic Precision
colors:
  surface: '#f3faff'
  surface-dim: '#cddce4'
  surface-bright: '#f3faff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#e7f6fe'
  surface-container: '#e1f0f8'
  surface-container-high: '#dbebf3'
  surface-container-highest: '#d6e5ed'
  on-surface: '#0f1d23'
  on-surface-variant: '#3f4944'
  inverse-surface: '#243239'
  inverse-on-surface: '#e4f3fb'
  outline: '#6f7974'
  outline-variant: '#bec9c3'
  surface-tint: '#166b53'
  primary: '#005842'
  on-primary: '#ffffff'
  primary-container: '#1f7159'
  on-primary-container: '#a4f2d4'
  inverse-primary: '#88d6b9'
  secondary: '#40655b'
  on-secondary: '#ffffff'
  secondary-container: '#c2ebde'
  on-secondary-container: '#466c61'
  tertiary: '#00583d'
  on-tertiary: '#ffffff'
  tertiary-container: '#007351'
  on-tertiary-container: '#8cf7c7'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#a4f2d4'
  primary-fixed-dim: '#88d6b9'
  on-primary-fixed: '#002117'
  on-primary-fixed-variant: '#00513d'
  secondary-fixed: '#c2ebde'
  secondary-fixed-dim: '#a7cfc2'
  on-secondary-fixed: '#00201a'
  on-secondary-fixed-variant: '#284d44'
  tertiary-fixed: '#8cf7c7'
  tertiary-fixed-dim: '#6fdaac'
  on-tertiary-fixed: '#002114'
  on-tertiary-fixed-variant: '#005138'
  background: '#f3faff'
  on-background: '#0f1d23'
  surface-variant: '#d6e5ed'
typography:
  display:
    fontFamily: Plus Jakarta Sans
    fontSize: 24px
    fontWeight: '700'
    lineHeight: 32px
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
  headline-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 17px
    fontWeight: '600'
    lineHeight: 24px
  body-lg:
    fontFamily: Be Vietnam Pro
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-md:
    fontFamily: Be Vietnam Pro
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  body-sm:
    fontFamily: Be Vietnam Pro
    fontSize: 13px
    fontWeight: '400'
    lineHeight: 18px
  label-md:
    fontFamily: Be Vietnam Pro
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.02em
  label-sm:
    fontFamily: Be Vietnam Pro
    fontSize: 11px
    fontWeight: '500'
    lineHeight: 14px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  page_margin: 14px
  gutter: 12px
  stack_sm: 8px
  stack_md: 16px
  stack_lg: 24px
---

## Brand & Style

This design system is tailored for educational professionals managing administrative and pedagogical tasks in a high-pressure environment. The brand personality is **authoritative yet approachable**, prioritizing clarity and cognitive ease to reduce the "mental load" of teachers. 

The design style follows a **Modern Corporate** approach with a focus on **Tonal Layering**. It leverages a sophisticated palette of deep forest greens and soft mints to evoke a sense of calm and growth. By utilizing high-quality typography and strategic whitespace, the interface remains clean and lightweight, ensuring that information density is balanced—sufficient for professional utility without being overwhelming.

## Colors

The color strategy uses a **Deep Green Monochrome Base** to establish professional trust. 
- **The Core Palette:** The primary green (`#1f7159`) is used for main actions, while the deep slate (`#193f36`) is reserved for high-emphasis containers to create a strong visual anchor.
- **Semantic Feedback:** Status colors use a "Tinted Background + High-Contrast Text" model. This ensures accessibility and immediate recognition of task states (Success, Warning, Danger) without disrupting the professional aesthetic.
- **Layering:** The background (`#f4f6f5`) provides a cool, neutral canvas that allows white cards to pop, defining the workspace clearly.

## Typography

This design system uses a pairing of **Plus Jakarta Sans** for headings and **Be Vietnam Pro** for body text. 
- **Headlines:** Use Plus Jakarta Sans to provide a friendly yet geometric and modern feel. It performs exceptionally well in short, impactful strings like student names or class titles.
- **Body & Data:** Be Vietnam Pro is chosen for its contemporary grotesque style and excellent legibility in list-heavy views (e.g., student lists, error books).
- **Hierarchy:** Primary emphasis is placed on weight transitions (Regular to Semi-Bold) rather than extreme size shifts, maintaining a compact mobile footprint.

## Layout & Spacing

The layout is built for a **375x812 mobile viewport** using a fluid vertical stack model.
- **Margins:** A consistent **14px side margin** is applied to all main content containers to maximize screen real estate while preventing elements from touching the bezel.
- **Card Spacing:** Vertical spacing between cards is standardized at 12px to maintain a rhythmic flow without excessive scrolling.
- **Grid:** While primarily a single-column layout, internal card structures may use a simple 2-column or 4-column distribution for meta-data (e.g., "Class Time" vs "Student Count").

## Elevation & Depth

To maintain a "clean and lightweight" feel, this design system avoids heavy drop shadows. Depth is communicated through **Tonal Elevation**:
- **Level 0 (Base):** Background color `#f4f6f5`.
- **Level 1 (Content):** White cards (`#ffffff`) with a subtle 1px border (`#e7ece9`). No shadow is used here to keep the UI "flat" and professional.
- **Level 2 (High Emphasis):** The dark green card (`#193f36`). This level uses color contrast rather than shadow to draw the eye to "Today's Schedule" or "Urgent Notifications."
- **Interaction:** On press, cards may transition to a slightly darker background shade or scale down by 2% to provide tactile feedback.

## Shapes

The shape language is primarily **Soft-Geometric**. 
- **Standard Cards:** Use an **8px radius** to create a structured, professional look.
- **Dark Emphasis Cards:** These feature a slightly larger **9px radius**, giving them a subtle visual distinction and "heavier" feel compared to standard white containers.
- **Interactive Elements:** Chips and Status Labels always use a **Capsule (Pill) shape** to distinguish them from actionable buttons or data containers.

## Components

### Buttons
- **Primary:** Height 44-46px. Solid background `#1f7159` with white text. 8px rounded corners.
- **Secondary/Ghost:** Transparent background with `#1f7159` border and text.

### Chips & Status Tags
- **Style:** Capsule/Pill-shaped. 
- **Implementation:** Use the semantic background/text pairs (e.g., Success: `#e9f6ef` bg / `#227253` text). Padding: 4px top/bottom, 12px left/right.

### Cards
- **Standard:** White background, 1px `#e7ece9` border, 8px radius. 14px internal padding.
- **Dark:** Background `#193f36`, 9px radius, white or light green text. Used for "Today's Summary" header.

### Input Fields
- **Style:** 44px height, light grey border `#e7ece9`, 8px radius. Labels are `label-md` in secondary text color.

### Bottom Navigation (Tab Bar)
- **Structure:** 5 items (Today, Schedule, Students, Error Book, Me).
- **Active State:** Icon and text use `#018d71`.
- **Inactive State:** Icon and text use `#74828a`.
- **Design:** Solid white background with a 1px top stroke `#e7ece9`.

### Lists
- **Item Style:** Clean rows with 14px horizontal padding. Use a 1px bottom divider for lists within cards, but omit the divider for the last item.