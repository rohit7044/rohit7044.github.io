# Reproducible tools

`prepare_public_assets.py` requires PyMuPDF. It creates a public-safe PDF from private/resume-original.pdf without overwriting the original. Diagrams live only in public/assets and are not rewritten. It also removes hidden ActualText strings, corrects the conflicting email hyperlink to the visible resume address and replaces Sony superlatives with public high-level descriptions. Run before building.

`download_gnm_model.py` caches the pinned official release under ignored tools and verifies its published SHA-256. `create_gnm_poses.py` uses the official GNM semantic sampler offline. `export_gnm_for_web.py` evaluates the neutral model and curated poses, writes a derived GLB with anatomical materials and a manifest, and never includes bases or coefficients. It has now been run against the actual official V3 model. See ../GNM_ASSET_PIPELINE.md and gnm_requirements.txt for the isolated runtime.

`browser_smoke.py` requires Playwright and Chromium. Start Vite on 127.0.0.1:5173, then run it to check three viewport widths, modes, keyboard/pointer orbit, reset, four visibly deforming expressions, absence of removed controls, navigation, PDF loading, overflow, console errors and fallback scenarios. Output goes to ignored test-results/.
