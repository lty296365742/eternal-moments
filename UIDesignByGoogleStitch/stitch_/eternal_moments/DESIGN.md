---
name: Eternal Moments
colors:
  surface: '#fff8f7'
  surface-dim: '#eed4d4'
  surface-bright: '#fff8f7'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#fff0f0'
  surface-container: '#ffe9e9'
  surface-container-high: '#fce2e2'
  surface-container-highest: '#f6dddc'
  on-surface: '#261818'
  on-surface-variant: '#594141'
  inverse-surface: '#3c2c2d'
  inverse-on-surface: '#ffedec'
  outline: '#8d7071'
  outline-variant: '#e1bebf'
  surface-tint: '#b3263c'
  primary: '#b2253c'
  on-primary: '#ffffff'
  primary-container: '#d43f52'
  on-primary-container: '#ffffff'
  inverse-primary: '#ffb3b5'
  secondary: '#775a19'
  on-secondary: '#ffffff'
  secondary-container: '#fed488'
  on-secondary-container: '#785a1a'
  tertiary: '#006a52'
  on-tertiary: '#ffffff'
  tertiary-container: '#008668'
  on-tertiary-container: '#fffffc'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#ffdada'
  primary-fixed-dim: '#ffb3b5'
  on-primary-fixed: '#40000c'
  on-primary-fixed-variant: '#910427'
  secondary-fixed: '#ffdea5'
  secondary-fixed-dim: '#e9c176'
  on-secondary-fixed: '#261900'
  on-secondary-fixed-variant: '#5d4201'
  tertiary-fixed: '#8ef6d2'
  tertiary-fixed-dim: '#72d9b6'
  on-tertiary-fixed: '#002117'
  on-tertiary-fixed-variant: '#00513e'
  background: '#fff8f7'
  on-background: '#261818'
  surface-variant: '#f6dddc'
  celebration-ruby: '#D43F52'
  anniversary-gold: '#C5A059'
  relationship-family: '#5856D6'
  relationship-social: '#34C759'
  relationship-custom: '#AF52DE'
  system-background: '#F2F2F7'
  secondary-background: '#FFFFFF'
  tertiary-background: '#F9F9F9'
typography:
  display-lg:
    fontFamily: Inter
    fontSize: 34px
    fontWeight: '700'
    lineHeight: 41px
    letterSpacing: 0.37px
  headline-md:
    fontFamily: Inter
    fontSize: 28px
    fontWeight: '600'
    lineHeight: 34px
    letterSpacing: 0.36px
  title-lg:
    fontFamily: Inter
    fontSize: 22px
    fontWeight: '600'
    lineHeight: 28px
    letterSpacing: 0.35px
  title-sm:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: '500'
    lineHeight: 25px
    letterSpacing: 0.38px
  body-lg:
    fontFamily: Inter
    fontSize: 17px
    fontWeight: '400'
    lineHeight: 22px
    letterSpacing: -0.41px
  body-sm:
    fontFamily: Inter
    fontSize: 15px
    fontWeight: '400'
    lineHeight: 20px
    letterSpacing: -0.24px
  label-caps:
    fontFamily: Inter
    fontSize: 13px
    fontWeight: '500'
    lineHeight: 18px
    letterSpacing: 0.06px
  caption:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 16px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  margin-page: 1rem
  gutter-card: 0.75rem
  stack-sm: 0.25rem
  stack-md: 0.5rem
  stack-lg: 1rem
  touch-target: 2.75rem
---

## Brand & Style

The design system is centered on the concept of "Thoughtful Remembrance." It targets users who value deep personal connections and high-quality digital experiences. The brand personality is warm, sophisticated, and reliable, acting as a quiet concierge for life's most important milestones.

The visual style is **High-Fidelity Minimalism**, strictly adhering to iOS design patterns while injecting a premium "editorial" feel. It utilizes generous whitespace, delicate typography, and the concept of "Depth through Translucency." By leveraging frosted glass effects (materials) and soft, ambient shadows, the UI feels lightweight yet substantial, prioritizing emotional content—like photos and countdowns—over heavy interface chrome.

## Colors

The palette is anchored by **Celebration Ruby**, a sophisticated red that evokes heart-felt emotion without the aggression of a standard error red. **Anniversary Gold** is used for secondary accents, specifically for high-value milestones or premium features.

The system utilizes iOS semantic naming for background tiers:
- **System Background:** The base layer of the application, using a subtle off-white (`#F2F2F7`).
- **Secondary Background:** Used for cards and grouped list sections (`#FFFFFF`).
- **Tertiary Background:** Used for inset elements or search bars.

For relationship tagging, a diverse but muted set of hues is employed to ensure categorization is clear but doesn't distract from the primary brand identity. All colors must meet WCAG AA contrast ratios against white backgrounds.

## Typography

This design system uses **Inter** (as the closest web-available equivalent to San Francisco) to maintain a systematic, utilitarian, yet modern feel. 

The hierarchy is structured to support "Information-First" browsing:
- **Large Titles (`display-lg`)** are reserved for top-level navigation headers that collapse into the navigation bar on scroll.
- **Milestone Numbers** (like "Days Remaining") should use `title-lg` or `headline-md` with medium or semi-bold weights to create a clear focal point.
- **Secondary Metadata** (dates, relationship labels) uses `body-sm` or `label-caps` to provide context without competing with event titles.

## Layout & Spacing

The system follows a **Fixed-Fluid hybrid grid**. On mobile, it uses a single-column layout with a standard 16pt (1rem) margin on both sides. On larger screens, content is contained within a maximum width of 600px for detail views to maintain readability.

Vertical rhythm is driven by an 8pt grid system. Components like list items and buttons must maintain a minimum height of 44pt (`touch-target`) to ensure accessibility and comfort. Cards should use `stack-lg` (16px) spacing between each other to create a breathable, "premium" layout.

## Elevation & Depth

Visual hierarchy is achieved through **Material Translucency** rather than aggressive shadows. 

1.  **The Base:** Flat system background.
2.  **The Content Layer:** White cards with a very soft, high-spread shadow (0px 4px 12px, 5% opacity black).
3.  **The Navigation Layer:** Frosted glass (Backdrop Blur: 20px) using the `systemUltraThinMaterial` look. This keeps the user grounded in their current context by allowing hints of content colors to bleed through.
4.  **Floating Elements:** Primary Action Buttons (PABs) use a slightly more pronounced shadow (0px 8px 20px, 15% opacity of the `primary_color_hex`) to suggest interactivity and importance.

## Shapes

The design system employs **Rounded** (Apple-style) corners. 
- **Standard UI Elements:** (Buttons, Input Fields) use a 0.5rem (8px) radius.
- **Large Container Elements:** (Cards, Modals) use a 1rem (16px) radius to create a soft, friendly aesthetic.
- **Avatars:** Strictly circular for individual characters, but 1.5rem (24px) `rounded-xl` for AI-generated posters or event thumbnails to differentiate between people and objects.

## Components

### Buttons
- **Primary:** Filled with `celebration-ruby`, white text, 10px roundedness. High-gloss appearance with a subtle gradient (top-down, 5% lighter to 5% darker).
- **Secondary:** Transparent background with `anniversary-gold` border and text.

### Anniversary Cards
Cards are the primary unit of the app. They must feature:
- A clear **Countdown Badge** in the top right (using `celebration-ruby` text).
- The **Event Title** in `title-sm`.
- A **Relationship Chip** in the bottom left using the specific category color with 10% opacity background and full-opacity text.

### Relationship Tags (Chips)
Small, pill-shaped indicators. They use low-saturation background tints of their assigned relationship color to ensure the text remains the primary focus.

### Input Fields
Standard iOS-style fields with an inline label. Understated grey borders that turn `celebration-ruby` on focus.

### List Items
Minimalist rows with a 16px horizontal padding. Include a chevron icon for navigation and a `status.unread` red dot indicator for new AI-generated gift suggestions.

### AI Posters
Featured in the "Blessing" section, these use a 1.5rem radius and are the only element allowed to use vibrant, multi-color gradients or full-bleed photography.