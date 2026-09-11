# Research alignment and demonstration guidance

This presentation is a working, bounded implementation with inspectable evidence. Describe this version as **a constraint-validated procedural prototype with optional LLM composition and heuristic adaptation**. It is not yet the complete learned PCGML system in the proposal.

## updation

The revised version validates request fields and model module selections, constructs geometry from controlled templates, and rejects failed scenes before delivery. Descriptions, actions, conditions and citations come from a versioned catalog. Untrusted text is not injected as HTML. Frontend and backend share an origin, Waitress replaces debug mode, provider errors are sanitized, and A-Frame assets are bundled locally. Live inference requires a demo token and has bounded calls and concurrency.

**The composer’s freedom is deliberately reduced: it chooses supported modules, rather than inventing arbitrary hazards, numerical constraints or regulatory interpretations. This makes the delivered prototype more testable but limits generative expressiveness. Explain that tradeoff instead of implying unrestricted natural-language scene generation.**

## Mapping to the proposal

| Proposal component | Demonstrated now | Remaining research work |
|---|---|---|
| Knowledge ingestion | Five curated hazard modules with source links and applicability conditions | Reviewed ingestion of regulatory passages, incident records and BIM/IFC |
| LLM composer | OpenRouter/Ollama schema-constrained category selection | Richer abstract scene graphs and evaluated retrieval grounding |
| Content synthesis | Seeded 4 × 3 m asset placement in a bounded yard | Grammar over real geometry and learned configuration distributions |
| Validation | Catalog fidelity, footprint bounds, clearance and approximate approach reachability | Physical collision, structural support, full context-dependent rule checks and SME calibration |
| Immersive delivery | SVG plan and schematic A-Frame/WebXR scene from the same JSON | Headset validation, controller interactions, Unity/Unreal adapters and AR registration |
| Adaptation | Highest Laplace-smoothed error category is included in the next scene | Bandit or RL policy with held-out evaluation and explicit reward design |
| Evaluation | Synthetic benchmark, layout measurements and browser practice logs | Controlled participant study with unaided recognition and transfer outcomes |

## How to present it in five minutes

Start with the problem: manually authored training scenes have limited variation, and unconstrained model output is difficult to trust. Show one no-key scene, select a condition, and trace it to its source. Open validation evidence and the exported specification. State exactly what the gate checks.

Compare three layouts and discuss both category and positional variation. Do not describe three maps as proof of semantic diversity. Switch to the 3D scene to show the JSON-to-runtime connection. Complete a short practice round with a deliberate mistake and generate an adaptive scenario; identify the resulting target category.

Finish by showing the reproducible test/benchmark files and the remaining research plan: extend the knowledge base, validate engine physics and realism, then compare static, random and learned/adaptive generation on held-out tasks. If OpenRouter is configured, show one actual live call and its returned model and token usage. Do not present mocked provider tests as live-model evidence.

## Metrics that this version can support

The benchmark reports local synthesis-plus-validation time, gate pass counts, unique scenario identifiers, category-set Jaccard distance and coverage of a predefined weak category. Its profiles are synthetic. The 100% expected pass rate of a constrained template generator is an engineering result about those constraints, not measured regulatory accuracy or learning effectiveness.

Practice logs contain category choices, skipped items, correctness, elapsed response time and page-visibility interruptions. The browser supplies observations and marked locations, so the outcome is cued classification accuracy. A response’s latency starts on its first selection, includes time navigating elsewhere, and ends at submission. Pre-session instructor inspection is possible. These are prototype interaction logs, not clean recognition-study data.

For RQ1, sample outputs and have independent construction-safety experts judge citation applicability, realism and pedagogical value. Report agreement and rejected cases with an explicit denominator. For RQ2, keep catalog, task coverage and evaluation budget comparable across generators; separate provider latency from synthesis latency. For RQ3, implement a hidden-answer assessment with unmarked hazards, log false positives and missed hazards, and hold out layouts/configurations from training. Obtain the relevant institutional review before recruiting participants.

## Proposal corrections worth making before submission

The proposal cites reference [15] as support for a PCGRL/3D generation implementation, but the supplied bibliography labels [15] as a text-to-video safety benchmark. That entry does not match the described claim; verify and replace the citation. The bibliography and novelty claim were not comprehensively independently verified in this code task.

Clarify that training scenarios can intentionally depict violations. The validation requirement should reject malformed or physically implausible representations while retaining explicitly labeled learning hazards; it should not claim that every depicted condition is compliant. Distinguish regulatory applicability checks, geometric checks and expert judgments.

Use consistent difficulty language. This prototype increases module count from apprentice to experienced as a simple workload heuristic, while enforcing required targets. That is not a validated curriculum. Later difficulty should incorporate salience, distractors, task demands and expert ratings rather than count alone.

Prefer bounded evidence-backed claims over “proven valid” for the complete system. The current generator has a small validated parameter space; no comprehensive proof over BIM geometry, regulation, physics or human learning is available.

## Sources behind the teaching catalog

Catalog version: `2026-09-11.1`. Each entry is an authored paraphrase scoped to a concrete condition; the rule is not fetched live for each request.

| Module | Reference and scope |
|---|---|
| Elevated construction edge | [1926.501(b)(1)](https://www.osha.gov/laws-regs/regulations/standardnumber/1926/1926.501): an unprotected construction edge 8 ft above a lower level without a protective alternative. Roofing/scaffold-specific exceptions are not modeled. |
| Exposed electrical circuit | [1926.416(a)(1)](https://www.osha.gov/laws-regs/regulations/standardnumber/1926/1926.416): possible contact with energized parts without effective protection. |
| Overhead objects and head protection | [1926.100(a)](https://www.osha.gov/laws-regs/regulations/standardnumber/1926/1926.100): missing protective helmet under a head-injury exposure. This reference addresses PPE, not all material-handling safeguards. |
| Occupied trench | [1926.652(a)(1)](https://www.osha.gov/laws-regs/regulations/standardnumber/1926/1926.652): 6 ft deep, soil rather than stable rock, no protective system. |
| Grinding particles | [1926.102(a)(1)](https://www.osha.gov/laws-regs/regulations/standardnumber/1926/1926.102): particle exposure without eye/face protection. |

Independent SME review of these modules has not been performed. No compliance certification or selection outcome is promised.
