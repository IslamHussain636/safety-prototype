# Verification evidence

Verified locally on **11 September 2026**, using an isolated Python 3.12 environment and a headless Microsoft Edge browser through Playwright. These are engineering checks of a prototype; no participant study or independent safety-expert assessment was performed.

## Automated backend checks

Command: `python -m unittest discover -s tests -v`

**15 tests passed.** They include 300 generated scenes (100 seeds at each of three experience levels), reproducibility, static baseline stability, weak-category targeting, explicit category coverage, invalid geometry/citations/conditions, module overlap, blocked spawn/approach, malformed/oversized requests, authentication, sanitized upstream errors, timeouts, rate limits and OpenRouter/Ollama payload handling.

Provider tests use mocked responses. They verify the integration contract and failure handling, not live model availability, quality, pricing or successful authentication.

## Browser checks

Verified on the actual Waitress-served app at `http://127.0.0.1:7860`:

- Generate and inspect a scenario; follow the module’s source-link target in the DOM.
- Generate a three-layout comparison and switch layouts.
- Complete a four-module practice session; confirm the expected 1/4 score for the scripted answers, saved responses and browser persistence after reload.
- Generate adaptively using that saved profile; confirm the target is displayed.
- Initialize A-Frame 1.5.0, render a WebGL canvas and four clickable module markers.
- Export scenario JSON and parse its validation envelope.
- Check a 390 px mobile viewport for horizontal overflow.
- Observe no uncaught JavaScript exceptions, failed requests or external asset requests after bundling the renderer and fonts.

Desktop, mobile and 3D screenshots were inspected. The 3D scene is schematic and the trench is a raised cutaway; this is not an engineered construction model. An actual immersive-headset session was not available for testing.

## Synthetic benchmark

Command: `python benchmark.py --runs 30 --out data`

| Strategy | Runs passing encoded checks | Unique scenes | Median synthesis + validation | Target-category coverage |
|---|---:|---:|---:|---:|
| Static | 30/30 | 1 | 4.477 ms | 0/30 |
| Procedural | 30/30 | 30 | 5.124 ms | 23/30 |
| Adaptive heuristic | 30/30 | 30 | 5.309 ms | 30/30 |

The target was a predefined weak trench/caught-in-between category in a synthetic profile. Static mode fixes three modules; the other modes use four. These are not controlled latency comparisons at equal workload, human recognition scores, training gains or regulatory-accuracy measurements. Hardware-dependent timings are stored with the raw runs in `data/benchmark-runs.csv` and summarized in `data/benchmark-summary.json`.

## Remaining deployment checks

No OpenRouter API key was supplied in the accessible material, so live OpenRouter inference was not tested. No live Ollama model was installed. Docker was not available, so the Docker image was prepared but not built or deployed. The Python app and static assets were tested locally; run the Docker and hosting smoke checks in `DEPLOYMENT.md` before sharing a public demonstration URL.

No source files in the supplied OneDrive folder were modified. All upgraded source, documentation and benchmark artifacts are in this package.
