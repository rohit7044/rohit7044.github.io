# Rohit Das - Research & Engineering portfolio

React, Vite, TypeScript and Three.js. Public destination: https://rohit7044.github.io/.

## Local development

Install Node 22.12+ and npm, then run:

```sh
npm ci
npm run dev
```

Development preview: http://127.0.0.1:5173/. Run `npm run build` and `npm run preview` for a production preview at http://127.0.0.1:4173/.

This workstation also has an ignored local Node/npm under .tools. PowerShell fallback:

```powershell
$env:PATH=(Join-Path $PWD '.tools')+';'+$env:PATH
.tools/node.exe .tools/package/bin/npm-cli.js run dev
```

## Publish to GitHub Pages

The workflow `.github/workflows/deploy.yml` installs locked dependencies, lints, typechecks, builds and deploys only `dist/`. It runs on pushes to `main` or a manual Actions trigger. No Python, raw GNM weights or research-server access is needed in CI.

1. On GitHub, open this repository's **Settings > Pages** and select **GitHub Actions** as the source. This is a one-time repository setting.
2. Review the changes locally, then commit and push when ready:

```sh
git add -A
git commit -m "Build research portfolio and configure GitHub Pages"
git push origin main
```

3. Wait for **Deploy portfolio to GitHub Pages** to succeed in the Actions tab, then visit https://rohit7044.github.io/.

No push or deployment was performed by the assistant. These commands publish when you choose to run them. Vite uses the correct root-domain base `/`. Hash navigation requires no SPA server fallback. The old `/portfolio.html` URL redirects to the research section; the old named-resume URL serves the public-safe PDF.

## Important files

- `src/`: application, content data, styles and independent GNM viewer.
- `public/`: reviewed downloadable resume, original research diagrams, derived GNM GLB/poster, attribution and compatibility links.
- `.github/workflows/deploy.yml`: build/deployment configuration.
- `scripts/`: optional PDF preparation, GNM download/export/validation and browser checks.
- Package/lock, TypeScript and ESLint configuration: reproducible development and checks.
- `CONTENT_REVIEW.md`, `DESIGN_SPEC.md`, `GNM_ASSET_PIPELINE.md`, `IMPLEMENTATION_REPORT.md`: content provenance, design, model pipeline and validation.
- `LICENSE`: repository license; separate GNM notices ship with the face asset.

`node_modules`, `dist`, `.tools`, test results, old prototype and editor files are local/ignored. They are not uploaded as the Pages artifact. The original supplied resume is preserved at ignored `private/resume-original.pdf`; only the sanitized derivative in public is shipped. Legacy tracked website files are recoverable from Git history.

## Face and resume

The viewer uses the official neutral GNM V3 template with eyes, teeth, gums and tongue. It offers Surface and Expression modes, with Open mouth, Smile, Pucker and Left wink. Teeth remain part of the face; there is no separate anatomy option, Topology control, Wide smile option or metadata paragraph. This is not a reconstructed personal identity. No model inference runs in the browser. See GNM_ASSET_PIPELINE.md for provenance and reproduction.

The public PDF removes the phone number/telephone link and hidden accessibility instructions, reconciles the email link, and uses high-level Sony descriptions. To update it, place the new original in private/resume-original.pdf and run `python scripts/prepare_public_assets.py` with PyMuPDF installed. Keep the research diagrams in public/assets unchanged.

## Validation

```sh
npm run typecheck
npm run lint
npm run build
```

For optional browser regression checks, install Python Playwright/Chromium, start the preview, and run `scripts/browser_smoke.py` with SITE_BASE_URL set to the preview URL. Generated screenshots/results go to ignored test-results/.
