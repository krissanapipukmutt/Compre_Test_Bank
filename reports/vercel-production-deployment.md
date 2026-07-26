# Vercel Production Deployment Report

Date: 2026-07-26 (Asia/Bangkok)

## Outcome

- Status: successful and production-ready
- Canonical production URL: <https://compre-test-bank.vercel.app>
- Vercel-generated deployment hostname: <https://compre-test-bank-cao62zxh3-krissanas-projects.vercel.app> (team-auth protected)
- Vercel project: `compre-test-bank`
- Deployment ID: `dpl_Fz6QMJniENF9nVSNUT5wT6PqeibL`
- Vercel state: `Ready`
- Target: `production`

The canonical URL is the public release endpoint and serves the application with HTTP 200 without authentication. The Vercel-generated per-deployment hostname is covered by the team's Vercel authentication policy and redirects unauthenticated visitors to Vercel login; this does not affect the public canonical production alias.

## Deployment audit

| Setting | Verified value |
| --- | --- |
| Framework | React 19 + Vite 7 + TypeScript |
| Application root | `web/` |
| Install command | `npm install` |
| Build command | `npm run build` |
| Output directory | `dist` |
| Entry point | `dist/index.html` |
| Node version | `22.x` from `package.json` |
| Runtime environment variables | None required |
| Routing | Hash routing through `window.location.hash` |
| Server rewrite | Not required for hash-route refreshes |
| Static assets | Vite bundle plus source-faithful question visuals from `web/public/` |

The Vercel CLI downloaded local project-link metadata and an OIDC credential for its own authenticated workflow. Both are excluded from Git by `web/.gitignore`; no credential value was printed, committed, or required by the browser application.

## Changes made

- `web/vercel.json`
  - Declares Vite explicitly.
  - Sets `npm install`, `npm run build`, and `dist`.
  - Prevents project-dashboard defaults from silently changing the release contract.
- `web/.vercelignore`
  - Excludes local coverage, build, browser-test, and test-result artifacts from source uploads.
- `web/package.json`
  - Pins the Vercel build runtime to Node `22.x`, matching the validated local runtime.
- `web/package-lock.json`
  - Records the same Node engine metadata for reproducible installs.
- `web/.gitignore`
  - Excludes `.vercel` project metadata and `.env*` credential files generated during linking.
- `.DS_Store`
  - Restores the exact non-academic metadata bytes recorded by the immutable-source inventory (12,292 bytes; SHA-256 `4f8568fe946b7491bbc1e1d28d98ef9116d5f895a7f5e6bce3f12f51716c7be0`). A prior Git commit had changed only this macOS metadata file without updating the inventory; no academic file was altered.
- `PLANS.md`, `TASKS.md`, and `PROJECT_STATE.md`
  - Record Phase 10 deployment completion and its validation gate.
- `reports/vercel-production-deployment.md`
  - Provides this release record.
- `reports/screenshots/question-visuals/{mobile,tablet,desktop}/visual-question-{021,080}-*.png`
  - Refreshes the repository's representative responsive evidence through the passing Playwright run.
- `web/playwright-report/index.html`
  - Records the latest 12-test passing browser report.
- `web/node_modules/.vite/vitest/da39a3ee5e6b4b0d3255bfef95601890afd80709/results.json`
  - Updates the already tracked local Vitest result cache during the 40-test passing validation run; it does not affect production output.

No academic data, question wording, choices, answers, translations, evidence, or examination visuals were modified.

## Deployment execution and log summary

1. A global Vercel CLI installation was attempted and failed with a local `/usr/local/lib/node_modules` permission error.
2. The workflow recovered without elevated privileges by using `npx --yes vercel@latest` (Vercel CLI 57.0.0).
3. Vercel device authentication completed for the existing account and project.
4. `web/` was linked to the existing `compre-test-bank` project.
5. Production project settings were pulled locally.
6. A Vercel production build completed successfully:
   - Vercel honored the package Node `22.x` engine over the dashboard's Node 24 default.
   - `npm install` completed with 0 reported vulnerabilities.
   - Vite transformed 53 modules.
   - `dist/index.html`: 0.60 kB (0.36 kB gzip).
   - CSS: 41.21 kB (8.51 kB gzip).
   - JavaScript: 2,405.80 kB (247.86 kB gzip).
   - The only build note was Vite's non-blocking chunk-size advisory.
7. The prebuilt output was deployed with `--prod`, uploaded successfully, assigned deployment ID `dpl_Fz6QMJniENF9nVSNUT5wT6PqeibL`, and aliased to the canonical URL.
8. `vercel inspect` reported target `production` and status `Ready`.

No build error, Vercel 404, missing `index.html`, or incorrect output-directory condition remains.

## Production verification

### HTTP and assets

- Canonical `/`: HTTP 200, `text/html; charset=utf-8`, 602 bytes.
- CSS `/assets/index-BiLCo0G4.css`: HTTP 200, `text/css; charset=utf-8`, 41,212 bytes.
- JavaScript `/assets/index-kDsnFU7f.js`: HTTP 200, `application/javascript; charset=utf-8`, 2,405,795 bytes.
- HTML contains the React mount node `<div id="root"></div>`.
- All 18 referenced examination visual assets return HTTP 200 with an image content type.
- Every production visual asset's SHA-256 digest exactly matches its local canonical file.

### Live browser verification

Headless Chromium loaded the canonical production URL and confirmed:

- document title `COMPRE Study Fieldbook`;
- document ready state `complete`;
- React root populated and body nonblank;
- stylesheet loaded;
- no console errors, page errors, or failed requests;
- no 404 state;
- 390 px mobile viewport has no horizontal overflow;
- navigation to `/#/library` renders `Study library`;
- direct reload of `/#/library` remains on that route and renders successfully.

### Repository validation

- Immutable-source and Phase 8 visual validation: PASS, 0 errors, 0 warnings.
- Translation integrity: PASS, 105 questions, 525 choices, 24 glossary terms, 0 errors, 0 warnings.
- ESLint: PASS.
- TypeScript strict build: PASS.
- Vitest: 7 files and 40 tests passed.
- Playwright: 12 tests passed, including responsive layouts, UNION visual order/readability, image zoom, keyboard handling, missing-image blocking, scoring exclusion, and asset delivery.
- Production build: PASS.
- Dependency install/audit result: 0 vulnerabilities.

## Commands executed

```bash
cd /Users/krissanap/Document/KMUTT/COMPRE_CODEX/web
npm install
npm run build
npm install -g vercel@latest
npx --yes vercel@latest whoami
npx --yes vercel@latest project ls
npx --yes vercel@latest link --yes --project compre-test-bank
npx --yes vercel@latest deploy --dry --prod --yes --format=json
npx --yes vercel@latest pull --yes --environment production
npx --yes vercel@latest build --prod --yes
npx --yes vercel@latest deploy --prebuilt --prod --yes --logs
npx --yes vercel@latest inspect https://compre-test-bank-cao62zxh3-krissanas-projects.vercel.app --wait --timeout 2m --no-color
curl -sS https://compre-test-bank.vercel.app/
curl -sS https://compre-test-bank.vercel.app/assets/index-BiLCo0G4.css
curl -sS https://compre-test-bank.vercel.app/assets/index-kDsnFU7f.js
npm run check
npm run test:e2e
```

Additional scripted checks used `curl`, SHA-256 comparison, and Playwright Chromium against the production URL to validate all referenced visual assets and live rendering.
