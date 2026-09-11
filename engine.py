"""Deterministic synthesis and a fail-closed validation gate."""
import copy
import hashlib
import json
import math
import random
from collections import deque
from catalog import CATALOG, CATALOG_VERSION

VERSION = "2.0.0"
LEVEL_COUNTS = {"apprentice": 3, "intermediate": 4, "experienced": 5}
KEYWORDS = {
    "fall": ("fall", "roof", "edge", "guardrail", "height"),
    "electrical": ("electric", "panel", "energized", "wire"),
    "struck_by": ("struck", "overhead", "helmet", "falling object"),
    "caught_in_between": ("trench", "excavat", "caught", "cave"),
    "ppe_missing": ("ppe", "eye", "grind", "face protection"),
}

def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()

def targets(prompt, explicit):
    found = [k for k, words in KEYWORDS.items() if any(w in prompt.lower() for w in words)]
    return list(dict.fromkeys(explicit + found))

def weak_category(profile):
    # Laplace-smoothed error probability. A heuristic, not a trained policy.
    if not any(p["attempts"] for p in profile.values()):
        return None
    return max(CATALOG, key=lambda k: (profile.get(k, {}).get("attempts", 0) - profile.get(k, {}).get("correct", 0) + 1) / (profile.get(k, {}).get("attempts", 0) + 2))

def choose_types(req, composed=None):
    if req["strategy"] == "static":
        return ["fall", "electrical", "struck_by"], None, []
    focus = targets(req["prompt"], req["focus"])
    weak = weak_category(req["profile"]) if req["strategy"] == "adaptive" else None
    selected = list(dict.fromkeys(([weak] if weak else []) + focus))
    if composed:
        selected = list(dict.fromkeys(selected + composed["hazard_types"]))
    rng = random.Random(req["seed"])
    rest = [k for k in CATALOG if k not in selected]
    rng.shuffle(rest)
    count = max(LEVEL_COUNTS[req["level"]], len(selected))
    return (selected + rest)[:count], weak, focus

def synthesize(req, composed=None):
    types, weak, focus = choose_types(req, composed)
    seed = 0 if req["strategy"] == "static" else req["seed"]
    rng = random.Random(seed)
    # Six 4 x 3 m modules, with clear approach lanes, in a 24 x 20 m yard.
    slots = [(4, 4), (12, 4), (20, 4), (4, 13), (12, 13), (20, 13)]
    if req["strategy"] != "static":
        rng.shuffle(slots)
    hazards = []
    for i, (kind, slot) in enumerate(zip(types, slots)):
        cat = CATALOG[kind]
        x, y = slot
        if req["strategy"] != "static":
            x += round(rng.uniform(-.5, .5), 2)
            y += round(rng.uniform(-.5, .5), 2)
        hazards.append({
            "id": f"H{i+1}", "type": kind, "x": x, "y": y,
            "footprint_width_m": 4, "footprint_depth_m": 3,
            "asset": cat["asset"], "severity": "high",
            "osha_ref": cat["ref"], "source_url": cat["url"],
            "description": cat["description"], "observation": cat["observation"],
            "action": cat["action"], "conditions": copy.deepcopy(cat["conditions"]),
            "intentional_training_hazard": True,
            "approach": {"x": x, "y": y + 3},
        })
    spec = {
        "schema_version": VERSION, "catalog_version": CATALOG_VERSION,
        "site_type": "Construction training yard", "site_width_m": 24, "site_depth_m": 20,
        "spawn": {"x": 12, "y": 19}, "hazards": hazards,
        "seed": seed, "strategy": req["strategy"],
        "level": "apprentice" if req["strategy"] == "static" else req["level"],
        "targeted_weak_category": weak, "required_categories": focus,
    }
    spec["scenario_id"] = digest(spec)[:16]
    return spec

def finite(v):
    return type(v) in (int, float) and math.isfinite(v)

def validate(spec):
    """Check authored catalog fidelity, footprints, clearance and 2D access.

    Passing means the encoded teaching constraints passed, never OSHA certification.
    Scene physics, human realism and full regulatory applicability remain unverified.
    """
    errors = []
    def check(ok, text):
        if not ok:
            errors.append(text)
    if not isinstance(spec, dict):
        return {"passed": False, "errors": ["Scenario must be an object."]}
    w, d = spec.get("site_width_m"), spec.get("site_depth_m")
    if not (finite(w) and finite(d) and 8 <= w <= 30 and 8 <= d <= 30):
        return {"passed": False, "errors": ["Invalid site dimensions."]}
    hazards = spec.get("hazards")
    if not isinstance(hazards, list) or not 3 <= len(hazards) <= 6:
        return {"passed": False, "errors": ["Expected 3–6 hazards."]}
    boxes, approaches, ids, kinds = [], [], [], []
    for h in hazards:
        if not isinstance(h, dict) or h.get("type") not in CATALOG:
            errors.append("Unknown hazard category."); continue
        cat = CATALOG[h["type"]]
        ids.append(h.get("id")); kinds.append(h["type"])
        check(isinstance(h.get("id"), str) and bool(h.get("id")), "Missing hazard ID.")
        check(h.get("osha_ref") == cat["ref"] and h.get("source_url") == cat["url"], "Citation does not match curated hazard.")
        check(h.get("conditions") == cat["conditions"], "Hazard conditions differ from the scoped teaching rule.")
        check(h.get("asset") == cat["asset"], "Asset does not match hazard.")
        check(h.get("intentional_training_hazard") is True, "Training hazard must be explicitly identified.")
        for key in ("description", "observation", "action"):
            check(h.get(key) == cat[key], f"Unreviewed {key}.")
        coords = [h.get(k) for k in ("x", "y", "footprint_width_m", "footprint_depth_m")]
        if not all(finite(v) for v in coords):
            errors.append("Non-finite geometry."); continue
        x, y, fw, fd = coords
        check(fw == 4 and fd == 3, "Asset footprint must be 4 x 3 m.")
        b = (x-fw/2, y-fd/2, x+fw/2, y+fd/2)
        check(0 <= b[0] < b[2] <= w and 0 <= b[1] < b[3] <= d, "Asset footprint outside site.")
        boxes.append(b)
        a = h.get("approach", {})
        if not isinstance(a, dict) or not all(finite(a.get(k)) for k in ("x", "y")):
            errors.append("Invalid approach point.")
        else:
            check(0 <= a["x"] < w and 0 <= a["y"] < d, "Approach outside site.")
            approaches.append((a["x"], a["y"]))
    check(len(set(str(i) for i in ids)) == len(ids), "Duplicate hazard IDs.")
    check(set(spec.get("required_categories", [])) <= set(kinds), "Required category omitted.")
    for i, a in enumerate(boxes):
        for b in boxes[i+1:]:
            clearance = 1.0
            check(a[2]+clearance <= b[0] or b[2]+clearance <= a[0] or a[3]+clearance <= b[1] or b[3]+clearance <= a[1], "Module overlap or insufficient 1 m separation.")
    spawn = spec.get("spawn", {})
    if not isinstance(spawn, dict) or not all(finite(spawn.get(k)) for k in ("x", "y")):
        errors.append("Invalid spawn.")
    elif not errors:
        # 0.5 m raster; inflate assets by 0.35 m for an approximate observer radius.
        step = .5
        nx, ny = int(w/step), int(d/step)
        def cell(p): return (int(p[0]/step), int(p[1]/step))
        def clear(c):
            x, y = (c[0]+.5)*step, (c[1]+.5)*step
            return 0 <= c[0] < nx and 0 <= c[1] < ny and all(not (b[0]-.35 <= x <= b[2]+.35 and b[1]-.35 <= y <= b[3]+.35) for b in boxes)
        start = cell((spawn["x"], spawn["y"]))
        seen, queue = set(), deque([start] if clear(start) else [])
        while queue:
            c = queue.popleft()
            if c in seen: continue
            seen.add(c)
            for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
                n = (c[0]+dx, c[1]+dy)
                if n not in seen and clear(n): queue.append(n)
        check(bool(seen), "Spawn is blocked or outside site.")
        check(all(cell(a) in seen for a in approaches), "Observer approach is unreachable on the 2D grid.")
    return {"passed": not errors, "errors": errors,
            "checks": ["Catalog and citation pairing", "Scoped hazard conditions", "Finite geometry and site bounds", "1 m module separation", "0.5 m grid approach reachability", "Required category coverage"],
            "intentional_hazards": len(hazards),
            "limitations": ["Teaching-rule checks only; not regulatory certification.", "Reachability is a 2D approximation, not a physics or structural-support simulation.", "Catalog scenarios and teaching effectiveness still require independent expert review."]}

def diversity(specs):
    pairs = []
    for i, a in enumerate(specs):
        for b in specs[i+1:]:
            at, bt = {h["type"] for h in a["hazards"]}, {h["type"] for h in b["hazards"]}
            shared = at & bt
            am, bm = {h["type"]: h for h in a["hazards"]}, {h["type"]: h for h in b["hazards"]}
            pairs.append({"a": a["scenario_id"], "b": b["scenario_id"],
                          "category_jaccard_distance": round(1-len(shared)/len(at|bt), 4),
                          "mean_shared_category_displacement_m": round(sum(math.hypot(am[k]["x"]-bm[k]["x"], am[k]["y"]-bm[k]["y"]) for k in shared)/len(shared), 3) if shared else None})
    return {"unique_scenarios": len({s["scenario_id"] for s in specs}), "pairs": pairs,
            "interpretation": "Category-set and spatial variation only; neither proves semantic diversity or learning benefit."}
