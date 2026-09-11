---
title: PCGML Construction Safety Lab
emoji: 🏗️
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: false
---

# PCGML Construction Safety Lab

A working research prototype based on the supplied five-layer construction-safety proposal. It provides constrained composition, deterministic site synthesis, server-side validation, 2D/WebXR delivery, and a small practice-feedback loop. It runs without an API key; OpenRouter and Ollama can optionally select the module mix.

**Start here:** run the local demo below. See [DEPLOYMENT.md](DEPLOYMENT.md) for Coolify and Hugging Face publishing, [RESEARCH_NOTES.md](RESEARCH_NOTES.md) for proposal alignment, and [VERIFICATION.md](VERIFICATION.md) for test evidence and remaining checks.

## Run locally on Windows

Install Python 3.12, extract this folder, and open PowerShell **inside the folder containing `backend_server.py`**:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe backend_server.py
```

Open [the local app](http://localhost:7860). Select **No-key procedural composer**, then **Generate scenario**. Do not open `static/index.html` directly. The backend serves the UI, assets and API from the same origin. No separate frontend server, Node build, database or CORS configuration is needed.

On Linux/macOS use `python3 -m venv .venv`, `.venv/bin/python -m pip install -r requirements.txt`, and `.venv/bin/python backend_server.py`.

## Connect OpenRouter

Stop the server with Ctrl+C. In **PowerShell 7**, set the secrets interactively so they are not literal entries in command history:

```powershell
$env:OPENROUTER_API_KEY = Read-Host 'OpenRouter API key' -MaskInput
$env:OPENROUTER_MODEL = Read-Host 'Exact OpenRouter model ID supporting structured outputs'
$env:APP_ACCESS_TOKEN = Read-Host 'Choose a long private demo access token' -MaskInput
.\.venv\Scripts\python.exe backend_server.py
```

Select **OpenRouter** in the page, and enter the **demo access token**, not the OpenRouter key. Model choice is server-side. Restart after changing environment variables; the health badge confirms configuration, not provider connectivity.

Choose an exact model ID whose endpoint supports `structured_outputs`. The integration sends `response_format: json_schema` and `provider.require_parameters: true`; unsupported models fail explicitly. A syntactically valid response is still checked by the server. No automatic retry or silent switch to a different provider occurs. A comparison uses one live composition call for three layouts. Availability and price depend on the chosen provider. [OpenRouter structured-output documentation](https://openrouter.ai/docs/guides/features/structured-outputs).

The OpenRouter key is never returned to the browser. The demo token authorizes live model usage; it is not an account system. The default limit is **30 live calls per rolling hour per server process**, with at most two concurrent generation requests. Failed live calls consume a slot in the hourly count. Restarting resets the count; multiple server processes each have their own limit. Keep the supplied one-process Waitress deployment for the small demo, and use provider-side spending controls for any public exposure.

`.env.example` documents the settings. The Python app does **not** load `.env` automatically. Hosted settings are environment variables; Docker can use a private `.env` through `--env-file`. Both Git and Docker ignore `.env`.

## Use a self-hosted model

Install [Ollama](https://docs.ollama.com/), run `ollama pull llama3.1`, and ensure the Ollama service is running. Set `APP_ACCESS_TOKEN` as above; set `OLLAMA_MODEL` to your installed model and optionally `OLLAMA_BASE_URL` (default `http://127.0.0.1:11434`). Select Ollama in the interface. The API uses `/api/chat` with a schema in `format`. See [Ollama’s API contract](https://docs.ollama.com/api/chat).

This route is self-hosted inference. Check the model’s own license; open weights and open-source software are different things. Ollama was mocked in automated testing; a live local model was not installed for verification.

## Demonstrate the prototype

1. Generate seed **42** in procedural mode. Inspect a module’s condition, recommended action and source link.
2. Review the validation panel and JSON. Every delivered scene has passed the server gate.
3. Compare three layouts. Export the bundle to preserve seeds, geometry, category differences and provenance.
4. Open the 3D view. Walk with WASD and drag to look; select a marker. Missing rails are actually omitted, and the trench is a labeled raised cutaway.
5. Start practice, select numbered modules, and classify their observations. Finish to reveal feedback. Unanswered modules count as incorrect; their answer latency is null.
6. Select Adaptive and generate again. The next scene includes the category with the highest smoothed error estimate. Export the practice log to inspect the evidence.

## Scope and interpretation

The supported setting is a **24 × 20 m generic teaching yard** with five curated modules: an elevated unprotected edge, exposed electrical parts, overhead-object head-protection exposure, an occupied soil trench, and grinding without eye/face protection. Natural-language keywords and explicit focus control required categories. The LLM can select a mix; it cannot invent geometry, citations or safety advice. Prompts for a roof or actual BIM model are not fulfilled as real site geometry and the UI says so.

The server checks catalog pairing, scoped conditions, finite geometry, site bounds, 1 m module separation, category coverage and approach-point reachability on a 0.5 m grid with a 0.35 m observer allowance. A deterministic seed reproduces the procedural result; live model selection is not guaranteed reproducible. Export the full scene and composer output for replay/provenance.

Hazards intentionally represent unsafe conditions. Passing the gate means the **encoded teaching constraints** passed; it does not certify a safe worksite, complete OSHA compliance, structural support, guardrail load resistance, or educational effectiveness.

Practice is **cued category classification**, with observations and locations supplied. It is not unaided hazard detection, gaze tracking, transfer testing or a protected examination. The browser receives the answer key for instructor review. Local timestamps measure first module selection to answer, including time away from that module; a page-visibility interruption flag is recorded. Results are editable browser data, not tamper-resistant research records.

The browser retains a category profile and the last 100 sessions in local storage. Older sessions are removed while cumulative profile counts remain. Data are not shared across devices or uploaded to a research database. Exports contain the prompt, scenario and profile; use synthetic examples for demonstrations.

## Project files

| File | Purpose |
|---|---|
| `backend_server.py` | Flask routes, provider calls, request validation and live-call controls |
| `catalog.py` | Versioned conditions, citations and teaching actions |
| `engine.py` | Seeded synthesis, validation and diversity measurements |
| `static/index.html`, `style.css`, `app.js` | UI, classification practice, exports and metric-scale renderers |
| `static/vendor/` | Bundled A-Frame 1.5.0, font assets and third-party licenses |
| `tests/test_backend.py` | Invariant, API and mocked-provider tests |
| `benchmark.py`, `data/` | Reproducible synthetic engineering benchmark |
| `Dockerfile` | Non-root deployment using Waitress on port 7860 |

The upgraded frontend replaces the original single-file HTML. The `/generate` endpoint remains, but its response is now an envelope with `scenario`, `validation`, and `metadata`; the original frontend is not compatible with it. OpenRouter replaces the need for several direct-provider SDKs. The supplied source files were left unchanged.

## Verify and extend

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe benchmark.py --runs 30 --out data
```

Benchmark CSV/JSON values are generated by this program, not human-study outcomes. Keep fixed catalog and engine versions when comparing runs. Before making a public open-source release, choose the license for your own project; the bundled third-party assets retain their licenses.
