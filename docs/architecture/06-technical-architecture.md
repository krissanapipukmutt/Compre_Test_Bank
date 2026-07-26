# Technical Architecture

## Stack decision

Use **React + Vite + TypeScript**. Static local JSON, browser-only state, and no server-rendering requirement make Next.js unnecessary; Vite produces a small static bundle and fast local workflow.

## Layers

```text
Validated JSON assets
  → runtime parsers / indexes
  → academic repository (read-only)
  → session engines + local progress repository
  → React contexts/hooks
  → responsive semantic components/pages
```

## Dependency policy

- Runtime: React and React DOM only unless a concrete need appears.
- Development: Vite, TypeScript, ESLint, Vitest, Testing Library, jsdom, and Playwright for browser/viewport checks.
- No analytics, CDN fonts, server SDK, authentication, database, or cloud dependency.

## Data loading

Build-time copied JSON lives under `web/src/data/`. The application validates once during bootstrap, creates read-only maps/indexes, and renders only after success. Tests inject valid/invalid fixtures.

## State

- Immutable academic repository context.
- Lightweight reducer for navigation/session UI.
- Practice/mock engines are pure functions where possible.
- Local progress repository isolates `localStorage`, versioning, and errors.
- Active exam state persists defensively so a refresh can be resumed without revealing answers.

## Security and privacy

- No HTML from academic data is injected; render text as React text nodes.
- No `dangerouslySetInnerHTML`, eval, dynamic remote code, secrets, telemetry, or network calls.
- Static hosting should add a restrictive CSP, `X-Content-Type-Options`, and `Referrer-Policy`.
- Source paths are local relative references, not clickable filesystem URLs in the browser.

