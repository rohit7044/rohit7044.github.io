# GNM asset pipeline — current implementation

The procedural placeholder has been replaced with the official **GNM V3 neutral template**, exported offline using the user's existing official checkout at `D:/Github Repo/gnm-webcam-puppet/GNM` (revision `5cf11d785a38a83597e64ad0b6d15950bcd6b390`). The research checkout remains read-only. No fitting, identity reconstruction, tracking or training is involved.

## Model provenance and rights

Official model release: https://huggingface.co/google/gnm-v3 at revision `c01e90d298d82301f9fd18f54806be751775cb7c`. Its model card explicitly licenses both the project and model weights under Apache 2.0. Pinned weights SHA-256: `61d78bbfb4ad8e0b38495804a4caef3214d3df00f8c3f68761e63b41ce3747eb` (verified after download). Raw weights remain under ignored `.tools/gnm/`, never in public assets. The public GLB is derived render geometry with a curated expression subset, not a model checkpoint or identity basis. Publication still requires the user's approval.

The notebook approach supplied by the user was verified directly: `gnm_numpy.GNM.from_remote(version=GNMMajorVersion.V3, variant=GNMVariant.HEAD, cache_dir=...)` loads the same cached official model. The reproducible exporter uses `from_custom_file` on that checksum-verified file to avoid implicit network access.

## Reproduce

Use a separate Python environment, install `scripts/gnm_requirements.txt`, and keep the original checkout read-only. Export scripts suppress bytecode writes to imported GNM sources. If installing the package itself, first copy it into an isolated temporary build directory to avoid build-metadata writes in the original checkout.

```powershell
python scripts/download_gnm_model.py
python scripts/create_gnm_poses.py --repo "D:\Github Repo\gnm-webcam-puppet\GNM"
python scripts/export_gnm_for_web.py --repo "D:\Github Repo\gnm-webcam-puppet\GNM" --model-file .tools/gnm/gnm_head.npz --poses .tools/gnm/curated-poses.json --out .tools/gnm/export --unit-to-metres 1 --front +z --rights-note "Official pinned Google model card explicitly licenses model weights Apache-2.0; local review only"
```

Review the outputs before copying `face.glb`, `face-manifest.json`, `GNM-LICENSE.txt` and `GNM-NOTICE.txt` to public/assets. Never transfer raw weights, sampler networks or coefficient JSON there. The actual neutral source bounds span roughly 0.342 m in Y and 0.255 m in X, with the nose facing +Z. Front orientation, surface normals and framing were checked in browser renders. The source right-handed orientation and triangle winding are preserved; zero-parameter output matches the template to floating-point tolerance.

## Anatomy and expressions

The full 17,821-vertex / 35,324-triangle topology is retained. GNM's own vertex-group memberships assign nine material regions: skin, mouth interior, gums, teeth, tongue, sclera, iris, pupil and cornea. A triangle uses the majority group membership at its vertices; no anatomical indices are invented. Corneas remain transparent. Teeth and gums remain visible inside the face, including while expressions are active. A separate isolation control was removed at the user's request.

The five presets use the official `semantic_sampler.ExpressionSampler`: SURPRISE (labeled Open mouth), HAPPY (Smile), SMILE_WIDE, PUCKER and WINK_LEFT. Each uses the mean of 16 samples with seed 42. All identity coefficients remain zero. The complete GNM evaluator produces geometry before export, preserving its built-in deformation behavior. This version has neck, head and eye joints; no nonexistent jaw-joint index is assumed. GNM expressions are unrelated to the separate 64D Audio2Motion representation.

Neutral positions/normals and pose deltas/normals are baked into a GLB. Vertex indexing and topology equality are asserted across poses, along with finite geometry and nonzero deformation. The manifest records topology, byte size, SHA-256, upstream revision, model revision/checksum, pose provenance/displacement, bounds, material counts and limitations. Coefficients and model bases are omitted from public output.

## Web delivery and limitations

The self-contained GLB is lazy-loaded; no Python or GNM inference runs in the browser. The neutral-only export measured 855,392 bytes; the final expression-inclusive size is recorded in the current manifest. Full-resolution topology is retained, with no destructive simplification or texture compression. Rendering is demand-driven, capped at device pixel ratio 1.5 and paused offscreen.

This is an untextured clay visualization; UVs exist in the source but are omitted because no texture is used. Material boundaries use vertex-group majority rather than a custom UV texture. Browser morph interpolation is linear between neutral and each baked pose; it is not a continuously evaluated parametric model. The fallback `face-poster.png` is a screenshot of the actual exported neutral head. Tests cover real model loading, visible pose changes, teeth retained within the face, orbit/reset and reduced-motion/WebGL/asset failures. These are local browser checks, not hardware FPS benchmarks or clinical/anatomical validation.

The shipped GLB retains five original pose targets for reproducibility; the website exposes only four, omitting Wide smile. The UI no longer exposes Topology or anatomy isolation, and the metadata paragraph has been removed. License/provenance information remains in the asset notices and documentation.
