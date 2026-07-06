# Design System Inspired by Pictographic

## 1. Visual Theme & Atmosphere

Pictographic's design system embodies a bold, minimalist aesthetic centered on dark backgrounds with vibrant accent colors that command attention. The atmosphere is professional yet approachable, balancing technical precision with creative energy. The interface leverages generous spacing, clean typography, and carefully placed accent colors to guide user focus toward the core action: generating and discovering SVG icons. Decorative sparkle elements scattered throughout reinforce a sense of innovation and magic, while the predominantly dark palette creates a sophisticated, modern foundation that lets colorful UI elements pop.

**Key Characteristics**
- Deep, sophisticated dark backgrounds with high contrast
- Vibrant accent colors used sparingly for maximum impact
- Clean, geometric icon-driven visual language
- Generous whitespace and breathing room between elements
- Minimalist navigation and form design
- Accent colors that evoke energy and creativity
- Star/sparkle decorative motifs for visual interest

## 2. Color Palette & Roles

### Primary
- **Deep Black** (`#000000`): Primary text, high-contrast elements, foundational interface color (418 uses)
- **Pure White** (`#FFFFFF`): Primary background for input fields, buttons, and contrast elements (86 uses)

### Accent Colors
- **Vivid Red** (`#F85252`): Primary call-to-action, highlight states, energetic accent (29 uses)
- **Sky Blue** (`#3B82F6`): Secondary accent, interactive hover states
- **Success Green** (`#4CD03A`): Success states, confirmation messaging (29 uses)

### Interactive
- **Semi-transparent White** (`#FFFFFF` at 10-15% opacity): Button backgrounds, subtle interactive overlays
- **Semi-transparent Black** (`#000000` at 0% opacity): Transparent backgrounds for dark mode inputs

### Neutral Scale
- **Light Gray Surface** (`#F2F2F2`): Secondary background surfaces, soft contrast (15 uses)
- **Medium Gray** (`#808080`): Disabled states, secondary text (12 uses)
- **Dark Gray Text** (`#333333`): Body copy, secondary headings (9 uses)
- **Slate Gray** (`#6B7280`): Tertiary text, muted labels (2 uses)
- **Charcoal** (`#252B37`): Very dark neutral alternative (2 uses)

### Surface & Borders
- **Soft Slate** (`#E2E8F0`): Borders, dividers, light surface backgrounds (453 uses)
- **Light Divider** (`#E5E5E5`): Subtle borders and separators (15 uses)
- **Pale Outline** (`#CCCCCC`): Soft borders, minimal contrast dividers (6 uses)
- **Near Black** (`#111827`): Deep background, high-contrast borders

## 3. Typography Rules

### Font Family
- **Primary:** Rethink Sans, system-ui, sans-serif
- **Fallback Stack:** Rethink Sans, -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif

### Hierarchy

| Role | Font | Size | Weight | Line Height | Letter Spacing | Notes |
|------|------|------|--------|-------------|-----------------|-------|
| Display/H1 | Rethink Sans | 72px | 700 | 79.2px | 0px | Hero headings, main page title |
| Heading/H2 | system-ui | 35.44px | 500 | 35.44px | 0px | Section headings, large titles |
| Body Large | Rethink Sans | 20px | 600 | 28px | 0px | Primary content, prominent text |
| Body Regular | Rethink Sans | 20px | 400 | 30px | 0px | Standard paragraph text |
| Input/Label | Rethink Sans | 16px | 600 | 16px | 0px | Form inputs, input labels |
| Link/Button Text | Rethink Sans | 16px | 400 | 24px | 0px | Buttons, navigation links |
| Caption | Rethink Sans | 14px | 400 | 20px | 0px | Helpers, fine print (inferred) |

### Principles
- Rethink Sans is the primary typeface, providing geometric precision and modern sensibility
- Bold weights (700, 600) create strong visual hierarchy and draw attention to key actions
- Generous line heights (28–30px for body) ensure readability in hero and content sections
- Input and button text maintains strong weight (600) for interactive clarity
- All typography is left-aligned in a clean, accessible manner

## 4. Component Stylings

### Buttons

#### Primary Button (Generate/CTA)
- **Background:** `#F2F2F2`
- **Text Color:** `#000000`
- **Font Size:** `16px`
- **Font Weight:** `600`
- **Font Family:** Rethink Sans
- **Padding:** `12px 24px`
- **Border Radius:** `4px`
- **Border:** `0px none`
- **Box Shadow:** `none`
- **Height:** Auto or 48px min
- **Hover State:** Opacity 0.9, cursor pointer
- **Line Height:** `24px`

#### Secondary Button (Icon/Utility – Rounded)
- **Background:** `rgba(255, 255, 255, 0.1)`
- **Text Color:** `#000000`
- **Font Size:** `16px`
- **Font Weight:** `400`
- **Padding:** `0px`
- **Border Radius:** `50%`
- **Border:** `0px none`
- **Width/Height:** `40px`
- **Hover State:** Background `rgba(255, 255, 255, 0.15)`, opacity increase

#### Secondary Button (Icon/Utility – Square)
- **Background:** `rgba(255, 255, 255, 0.15)`
- **Text Color:** `#000000`
- **Font Size:** `16px`
- **Font Weight:** `400`
- **Padding:** `0px`
- **Border Radius:** `4px`
- **Border:** `1px solid rgba(255, 255, 255, 0.1)`
- **Width/Height:** `32px`
- **Hover State:** Background `rgba(255, 255, 255, 0.2)`

#### Tertiary Button (Neutral Gray)
- **Background:** `#B0B0B0` or `#F2F2F2`
- **Text Color:** `#000000`
- **Font Size:** `16px`
- **Font Weight:** `400`
- **Padding:** `6px`
- **Border Radius:** `4px`
- **Border:** `0px solid #E2E8F0`
- **Width/Height:** `32px`
- **Hover State:** Opacity 0.85

### Cards & Containers

#### Hero Card (Dark Container)
- **Background:** `#0F0F0F`
- **Text Color:** `#000000` (text) or `#FFFFFF` (light text inside)
- **Padding:** `0px`
- **Border Radius:** `8px`
- **Border:** `1px solid #FFFFFF`
- **Width:** `658px`
- **Height:** `160px`
- **Box Shadow:** `none`
- **Display:** Flex, centered content
- **Responsive:** Adjust width for smaller screens

### Inputs & Forms

#### Text Input (Primary Search)
- **Background:** `rgba(0, 0, 0, 0)` (transparent on dark)
- **Text Color:** `#FFFFFF`
- **Font Size:** `16px`
- **Font Weight:** `400`
- **Font Family:** Rethink Sans
- **Padding:** `16px 16px 16px 48px` (left padding for icon)
- **Border Radius:** `8px`
- **Border:** `0px none #FFFFFF` (appear borderless)
- **Height:** `72px`
- **Width:** `656px`
- **Line Height:** `22.86px`
- **Placeholder Color:** `rgba(255, 255, 255, 0.6)`
- **Focus State:** Subtle outline `1px solid rgba(255, 255, 255, 0.3)`, background stays transparent

### Navigation

#### Navigation Buttons (Header)
- **Background:** `#E2E8F0` or `rgba(255, 255, 255, 0.1)` depending on state
- **Text Color:** `#000000`
- **Font Size:** `14px`
- **Font Weight:** `500`
- **Padding:** `8px 12px`
- **Border Radius:** `0px` (rectangular, flush style)
- **Border:** `1px solid #000000` or `none`
- **Display:** Inline-block or flex with gap `16px`
- **Hover State:** Background color shift, text remains dark
- **Active State:** Bold text or underline indicator

#### Navigation Links
- **Background:** `#E8E8E8` (pill) or transparent
- **Text Color:** `#333333`
- **Font Size:** `16px`
- **Font Weight:** `400`
- **Padding:** `4px 16px`
- **Border Radius:** `0px`
- **Hover State:** Opacity 0.8, slight color shift
- **Underline:** On hover or active state

## 5. Layout Principles

### Spacing System

Base unit: **8px**

Full scale and contexts:
- **4px:** Micro spacing (icon padding, tight borders)
- **8px:** XS spacing (icon padding, button padding)
- **12px:** S spacing (section margins, small gaps)
- **16px:** M spacing (form padding, card padding)
- **20px:** L spacing (content padding)
- **24px:** XL spacing (component gaps, section spacing)
- **32px:** 2XL spacing (larger gaps between sections)
- **48px:** 3XL spacing (hero section spacing)
- **64px:** 4XL spacing (major section separations)
- **80px:** 5XL spacing (hero top/bottom padding)
- **88px:** Custom large padding (full-width hero padding)
- **100px:** Custom XL padding (page margins on large screens)

### Grid & Container

- **Max Width:** `1280px` (default container)
- **Hero Container:** `658px` (centered, tighter constraint)
- **Grid Strategy:** 12-column flexible grid on desktop; adapts to 6-column on tablet, single-column on mobile
- **Section Padding:** `80px` vertical on desktop, `48px` on tablet, `24px` on mobile
- **Horizontal Margins:** `100px` on desktop, `48px` on tablet, `20px` on mobile
- **Page Background:** `#000000` (primary dark) or `#0F0F0F` (deepest dark)

### Whitespace Philosophy

Pictographic prioritizes generous whitespace to emphasize content hierarchy and reduce cognitive load. Large spacing between sections creates natural breathing room, allowing the eye to focus on key interactive elements. Hero sections employ 80–100px padding; standard content uses 48px gaps. Input fields and cards float in negative space to appear more prominent. Decorative sparkles occupy otherwise empty regions, adding visual interest without clutter. This approach reinforces the premium, creative positioning of the brand.

### Border Radius Scale

- **0px:** Navigation items, links (no radius)
- **4px:** Buttons (utility/secondary), navigation components, minimal rounding
- **8px:** Input fields, cards, major containers
- **50%:** Circular buttons, avatar spaces, perfectly round icons
- **0px 0px 8px 8px:** Input bottom radius (inferred for input variations)

## 6. Depth & Elevation

| Level | Treatment | Use |
|-------|-----------|-----|
| Flat | `box-shadow: none;` | Forms, buttons, primary interactive elements |
| Subtle | `box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.1);` | Cards on hover, secondary containers |
| Elevated | `box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.15);` | Modal overlays, expanded content (inferred) |
| Deep | `box-shadow: 0px 8px 24px rgba(0, 0, 0, 0.25);` | Floating action buttons, dropdown menus (inferred) |

Pictographic's shadow philosophy emphasizes flatness and clarity. Most interactive elements use no shadow, relying instead on color contrast and layout hierarchy to establish depth. Subtle shadows (0–2px) appear on hover or expanded states to indicate elevation without visual heaviness. The dark background (`#000000`) provides natural depth separation; shadows are kept minimal to maintain the clean, modern aesthetic. On lighter surfaces or modal overlays, shadows are slightly more pronounced to establish clear layering.

## 7. Do's and Don'ts

### Do
- Use `#F85252` (Vivid Red) for primary CTAs like "Generate" buttons to command attention
- Maintain deep dark backgrounds (`#000000` or `#0F0F0F`) for contrast and modern appeal
- Apply generous padding (80–100px) to hero sections to create breathing room
- Use Rethink Sans at bold weights (600–700) for headings and interactive elements
- Keep input fields transparent with light text (`#FFFFFF`) on dark backgrounds for sophistication
- Space navigation items with 16–24px gaps to prevent visual crowding
- Deploy decorative sparkle elements (`✦`) in empty quadrants of the layout
- Employ 8px border radius for inputs and cards; 50% for circular buttons
- Use `#4CD03A` (Success Green) exclusively for confirmatory states, not primary actions
- Maintain minimum touch targets at 40–48px for mobile buttons

### Don't
- Avoid using red (`#F85252`) for alerts or errors—reserve it for primary CTAs only
- Don't use heavy shadows; keep elevation subtle or flat
- Avoid clashing accent colors; stick to red, blue, and green in designated roles
- Don't reduce border radius below 4px for interactive elements; maintain clarity
- Avoid placing text directly on images without a dark overlay
- Don't use serif fonts for body copy; maintain Rethink Sans or system-ui
- Avoid padding buttons below 8px; maintain comfortable tap targets
- Don't mix light and dark mode palettes within the same view
- Avoid opacity below 0.8 for primary text; ensure readability
- Don't overuse decorative elements; keep sparkles to 4–6 per viewport

## 8. Responsive Behavior

### Breakpoints

| Breakpoint Name | Width | Key Changes |
|-----------------|-------|------------|
| Mobile | 320–479px | Single-column layout, 20px padding, stacked navigation, buttons full width |
| Tablet Small | 480–767px | Two-column grid, 24px padding, horizontal navigation flex wrap, compact spacing |
| Tablet | 768–1023px | Six-column grid, 48px padding, navigation horizontal, cards 2-up |
| Desktop | 1024–1279px | Twelve-column grid, 80px padding, full hero width (658px centered) |
| Desktop Large | 1280px+ | Twelve-column grid, 100px side padding, container max-width 1280px |

### Touch Targets

- **Minimum interactive height:** `44px` (buttons, links, navigation items)
- **Minimum interactive width:** `44px` (square or circular buttons)
- **Recommended spacing between targets:** `8px` minimum, `16px` preferred
- **Icon buttons:** `40px` × `40px` on mobile, `32–40px` on desktop
- **Form inputs:** Full width on mobile (with 20px margins), 656px max on desktop
- **Navigation links:** `12px` horizontal padding, `8px` vertical padding minimum

### Collapsing Strategy

- **Hero Section:** Maintains centered layout on all screens; width reduces from 658px to 80% on tablet, 90% on mobile
- **Input Field:** Full width with margin reduction (20px on mobile, 48px on tablet, 100px on desktop)
- **Navigation:** Horizontal flex layout on desktop/tablet, vertical or hamburger menu on mobile (< 768px)
- **Grid Gaps:** 24px on desktop, 16px on tablet, 12px on mobile
- **Padding Collapse:** 100px (desktop) → 48px (tablet) → 20px (mobile)
- **Font Sizing:** Display type (72px) reduces to 48px on tablet, 32px on mobile; body remains 20px down to 18px on mobile
- **Decorative Elements:** Hide secondary sparkles on mobile (< 480px) to reduce visual noise

## 9. Agent Prompt Guide

### Quick Color Reference

Use this mapping for rapid component implementation:

- **Primary CTA & Accent:** Vivid Red (`#F85252`)
- **Success/Confirmation:** Success Green (`#4CD03A`)
- **Secondary Accent:** Sky Blue (`#3B82F6`)
- **Primary Text:** Deep Black (`#000000`)
- **Light/Contrast Text:** Pure White (`#FFFFFF`)
- **Light Background/Inputs:** Off White (`#F2F2F2`)
- **Borders & Dividers:** Soft Slate (`#E2E8F0`)
- **Disabled/Muted Text:** Medium Gray (`#808080`)
- **Dark Background:** Near Black (`#111827`) or Pure Black (`#000000`)
- **Hero Container Background:** Deep Black (`#0F0F0F`)
- **Subtle Interactive Overlay:** `rgba(255, 255, 255, 0.1)` or `rgba(255, 255, 255, 0.15)`

### Iteration Guide

Follow these 10 critical rules to implement Pictographic's design system accurately:

1. **Typography Priority:** All headings use Rethink Sans at weights 500–700; body text uses 400 or 600 weight with line-height 28–30px.

2. **Dark Mode Base:** All backgrounds default to `#000000` or `#0F0F0F`; light text (`#FFFFFF`) floats on dark surfaces.

3. **Accent Red Discipline:** Red (`#F85252`) is reserved exclusively for primary CTAs (e.g., "Generate" button) and highlights; never use for errors or warnings.

4. **Input Styling:** Search/input fields are transparent with `16px` left padding for icons, `72px` height, `8px` border radius, and white text on dark background.

5. **Button Sizing:** Primary buttons are 48px+ height; icon buttons are 40px (circular) or 32px (square) with 50% or 4px radius respectively.

6. **Spacing Consistency:** Apply base 8px multiples; hero sections use 80–100px padding, standard gaps are 24–48px, and buttons/forms use 12–20px internal padding.

7. **Whitespace Maximization:** Pair content with significant negative space; hero containers should appear centered and isolated, not edge-to-edge.

8. **Border Radius Hierarchy:** Navigation 0px, buttons 4px or 50%, inputs/cards 8px; never mix radius styles within a single component family.

9. **Decorative Elements:** Place small star/sparkle icons (`✦`) in empty quadrants of hero or between sections; limit to 4–6 per viewport; hide on mobile.

10. **Focus & Hover States:** Interactive elements show increased opacity (0.85–0.95) or subtle background color shift on hover; no heavy shadows; maintain 8–12px focus outline on keyboard navigation.