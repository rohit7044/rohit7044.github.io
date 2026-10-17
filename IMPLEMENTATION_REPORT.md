# Portfolio implementation and deployment readiness

## Current site

React + Vite + TypeScript with an independent Three.js face viewer, editorial charcoal/off-white/sand styling, mobile navigation and layouts, research case studies, experience, publications, education, skills, contact and public-safe resume download. Latest resume facts and disagreements are documented in CONTENT_REVIEW.md.

The face is the official GNM V3 neutral template (17,821 vertices, 35,324 triangles), not a personal identity reconstruction. Its 2,997,896-byte GLB includes real skin, eyes, teeth, gums and tongue. Offline export and independent comparisons against GNM confirmed the neutral positions, original triangle topology and all baked poses. Four expressions are exposed: Open mouth, Smile, Pucker and Left wink. Teeth/gums remain in the mesh. Topology, Wide smile, anatomy controls and the metadata paragraph were removed per the final user preferences. Engineering is capitalized in visible copy.

## GitHub Pages preparation

Added .github/workflows/deploy.yml, following Vite's official Pages workflow. It runs npm ci, lint and the typechecked production build, uploads only dist, then deploys to GitHub Pages. It triggers on pushes to main and manual invocation. Action revisions are pinned. GitHub's Pages source must be set to GitHub Actions once by the owner. No repository setting, Git push or deployment was performed here.

## Cleanup

Removed obsolete root portfolio.html, portfoliojstyles.js, portfoliostyles.css and styles.css; the production compatibility redirect is retained under public. Removed duplicate root diagrams after matching their hashes to the unchanged copies in public/assets. Moved the original supplied resume into ignored private/resume-original.pdf and updated its preparation script; only public-safe copies are built. Consolidated historical GNM update notes into the current documentation and removed the redundant GNM_UPDATE_REPORT.md. Updated README with the actual deployment and development steps.

Recursive deletion of .idea, the old prototype and .tools model/runtime directories was rejected by automatic safety review, which reported only blocked by policy. Those directories remain local. The old prototype, private sources, tooling, generated builds, test results and node_modules are ignored; none is uploaded as the Pages artifact. Existing tracked .idea files remain unchanged. No files outside this website directory were modified.

## Verification

- npm run lint: passed.
- npm run build: passed, including TypeScript checks. The lazy Three.js chunk warning remains (approximately 577 kB minified, 148 kB gzip).
- Production browser smoke checks: passed at 1440, 768 and 390px, including four visibly deforming expressions, keyboard/mouse rotation, mobile touch, reset, removed-control absence, navigation, resume, no overflow and no console errors. Reduced-motion, no-WebGL and failed-asset poster scenarios pass. One Chromium screenshot process closed unexpectedly; the complete retry passed.
- Earlier narrow layout checks passed at 320, 360 and 414px as well.
- dist output inspection: 14 compiled/public files; no raw model weights, sampler networks, Python/TeX sources, private folder or archives. GLB SHA-256 matches the manifest; both resume URLs serve identical public-safe PDF bytes.
- git diff --check: passed.
- Workflow structure and official action revisions were reviewed locally; GitHub-hosted execution awaits the owner's first push and Pages setting.

CPU render-submission times in test-results/browser-results.json are not GPU timings or FPS benchmarks. GNM model provenance, license and exporter limitations are recorded in GNM_ASSET_PIPELINE.md and the shipped notices. No browser-side fitting or inference occurs.

## Next step for the owner

Set Settings > Pages > Source to GitHub Actions, review the source changes, commit and push main using the commands in README, and wait for the Pages workflow to succeed. The destination remains https://rohit7044.github.io/.
