# Responsive UI Design

## Visual direction

The interface uses a calm academic “field notebook” aesthetic: warm paper background, ink/navy text, teal evidence accents, amber warnings, and restrained red for destructive/error states. Thai and English use the system sans-serif stack to avoid runtime font downloads.

## Mobile-first layout

- Base: single column, 16 px gutters, fluid type, stacked controls and choices.
- `min-width: 48rem` (768 px): two-column study layouts, persistent filter panel where space permits.
- `min-width: 64rem` (1024 px): left rail plus centered reading canvas; mock navigator may sit beside the question.
- `min-width: 80rem` (1280 px): wider dashboard grid while reading lines remain capped near 72 characters.

Component behavior—not device labels—drives adaptation. Container queries may be used for cards but are not required.

## Required viewport matrix

| Viewport | Navigation | Content / exam behavior |
| --- | --- | --- |
| 320×568, 360×800, 375×667 | bottom nav + drawer | one column; stacked choices; compact sticky exam status; full-screen-safe dialogs |
| 390×844, 412×915 | bottom nav + drawer | one column with roomier cards; navigator opens as bottom sheet |
| 768×1024, 820×1180 | compact rail or drawer | filters/content can split; navigator drawer or side panel |
| 1024×768 | rail | question and navigator side by side without hiding timer |
| 1280×800, 1440×900 | full rail | dashboard grids and capped reading column |

## Responsive safety

- `min-width: 0`, `overflow-wrap: anywhere`, and controlled code/source-path wrapping prevent accidental overflow.
- Only comparison tables receive a labelled horizontal scroll container; core exam UI never scrolls horizontally.
- Dialogs use `max-height: min(90dvh, 48rem)` with internal scrolling.
- Sticky exam status reserves layout space and uses `env(safe-area-inset-*)`.
- Mobile navigator is a labelled bottom sheet; buttons remain at least 44×44 px.
- Charts use CSS grid/bars and text values, not fixed-width canvas.
- Long Thai text uses normal line breaking and `line-height` at least 1.6.
- No hover-only information; hover styles supplement focus/pressed states.
- Reduced motion disables smooth scrolling and decorative transitions.

## Key screen wireframes

```text
PHONE                         DESKTOP
┌ app bar / timer ┐           ┌ rail ┬ header / status ┐
│ warning/status  │           │      │ filters          │
│ question        │           │ nav  ├ question ┬ nums  │
│ [ choice       ]│           │      │ choices  │ 1 2 3 │
│ [ choice       ]│           │      │ actions  │ 4 5 6 │
│ actions         │           └──────┴───────────┴───────┘
└ bottom nav      ┘
```

