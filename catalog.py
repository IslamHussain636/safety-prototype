"""Small curated teaching catalog, not a comprehensive compliance knowledge base."""
CATALOG_VERSION = "2026-09-11.1"
BASE = "https://www.osha.gov/laws-regs/regulations/standardnumber/1926/"
CATALOG = {
    "fall": {
        "label": "Fall", "color": "#f68b60", "ref": "1926.501(b)(1)",
        "url": BASE + "1926.501", "asset": "platform",
        "description": "A worker stands on an 8 ft elevated construction platform with an open edge and no fall protection.",
        "observation": "Elevated platform: 8 ft above the lower level. One edge is open. No net or personal fall arrest system is provided.",
        "action": "Stop exposure to the edge and have appropriate fall protection provided before work resumes.",
        "basis": "For the scoped unprotected construction edge, the 6 ft trigger applies; guardrails, safety nets, or personal fall arrest are alternatives.",
        "conditions": {"height_ft": 8, "unprotected_edge": True, "fall_protection": False},
    },
    "electrical": {
        "label": "Electrical", "color": "#f6cc64", "ref": "1926.416(a)(1)",
        "url": BASE + "1926.416", "asset": "panel",
        "description": "An open energized panel has accessible live parts within a worker's reach.",
        "observation": "Panel door open; circuit energized; exposed terminals within reach of the work position. No effective insulating guard.",
        "action": "Keep workers clear and have qualified personnel establish appropriate electrical protection before work proceeds.",
        "basis": "The scoped condition allows contact with an electric power circuit without deenergizing and grounding or effective guarding.",
        "conditions": {"energized": True, "contact_possible": True, "effective_guard": False},
    },
    "struck_by": {
        "label": "Struck by", "color": "#78b6ff", "ref": "1926.100(a)",
        "url": BASE + "1926.100", "asset": "materials",
        "description": "A worker without a protective helmet is beneath elevated loose construction materials.",
        "observation": "Loose materials are stored overhead; a worker below wears no protective helmet.",
        "action": "Remove the worker from exposure, secure the materials, and provide appropriate head protection.",
        "basis": "Head protection is required where falling or flying objects can cause head injury. This citation addresses head protection, not every struck-by control.",
        "conditions": {"overhead_objects": True, "helmet_present": False},
    },
    "caught_in_between": {
        "label": "Caught in / between", "color": "#be9cff", "ref": "1926.652(a)(1)",
        "url": BASE + "1926.652", "asset": "trench",
        "description": "A worker occupies a 6 ft deep trench in soil with no protective system.",
        "observation": "Trench depth: 6 ft; material is soil, not stable rock. A worker is inside. No shoring, shielding, or protective slope.",
        "action": "Stop entry and have a competent person arrange an appropriate protective system before workers enter.",
        "basis": "The stable-rock and less-than-5-ft exceptions do not apply to this explicitly scoped occupied soil trench.",
        "conditions": {"depth_ft": 6, "stable_rock": False, "occupied": True, "protective_system": False},
    },
    "ppe_missing": {
        "label": "Eye / face protection", "color": "#64dbc2", "ref": "1926.102(a)(1)",
        "url": BASE + "1926.102", "asset": "workbench",
        "description": "A worker performs particle-producing grinding without eye or face protection.",
        "observation": "Grinding at the workbench produces flying particles. The worker has no eye or face protection.",
        "action": "Pause the task and provide eye or face protection appropriate to the exposure before continuing.",
        "basis": "The scoped task exposes the worker to flying particles, triggering appropriate eye or face protection.",
        "conditions": {"flying_particles": True, "eye_face_protection": False},
    },
}
