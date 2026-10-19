"""Offline sensory authoring prototype. No live storage or Discord imports."""
import json
from pathlib import Path

def norm(value):
    return " ".join(value.casefold().split())

def validate(rows):
    ids = set()
    for row in rows:
        required = {"id", "scene", "verb", "targets", "sense", "observation"}
        if required - row.keys():
            raise ValueError("Missing fields: " + str(required - row.keys()))
        if row["id"] in ids:
            raise ValueError("Duplicate interaction ID")
        ids.add(row["id"])
        for field in required:
            value = row[field]
            if field == "targets":
                if not isinstance(value, list) or not value or not all(isinstance(x, str) and x.strip() for x in value):
                    raise ValueError("Targets must be a nonempty list of names")
            elif not isinstance(value, str) or not value.strip():
                raise ValueError(field + " must be nonempty text")
        if row["sense"] not in {"hearing", "touch", "vision", "taste", "smell"}:
            raise ValueError("Unknown sense")
        for key in ("requires", "discoveries"):
            if key in row and (not isinstance(row[key], list) or not all(isinstance(x, str) for x in row[key])):
                raise ValueError(key + " must be a list of fact names")
        for variant in row.get("variants", []):
            if set(variant) - {"requires", "observation", "thought"}:
                raise ValueError("Unknown variant field")
            if not isinstance(variant.get("requires"), list) or not variant["requires"] or not all(isinstance(x, str) for x in variant["requires"]):
                raise ValueError("Variant needs explicit conditions")
    return rows

def resolve(rows, scene, verb, target, facts=(), senses=None):
    """Facts are supplied rehearsal context, never private data fetched by resolver.
    senses=None means availability is unmodelled; an explicit set is a test fixture.
    Returns proposed discoveries; caller must decide whether/how to persist.
    """
    rows = validate(rows)
    candidates = [r for r in rows if r["scene"] == scene and norm(r["verb"]) == norm(verb)
                  and norm(target) in {norm(t) for t in r["targets"]}]
    if not candidates:
        return {"status": "unsupported", "message": "That interaction has no authored response here.", "discoveries": []}
    available = [r for r in candidates if set(r.get("requires", [])) <= set(facts)]
    if not available:
        return {"status": "unavailable", "message": "That interaction is not available in this context.", "discoveries": []}
    if len(available) != 1:
        raise ValueError("Ambiguous interaction: author must resolve overlapping conditions")
    row = available[0]
    if senses is not None and row["sense"] not in senses:
        return {"status": "sense_unavailable", "message": "This rehearsal marks that sense unavailable.", "discoveries": []}
    variants = [v for v in row.get("variants", []) if set(v["requires"]) <= set(facts)]
    if len(variants) > 1:
        raise ValueError("Ambiguous character variants")
    view = dict(row)
    if variants:
        view.update(variants[0])
    return {"status": "observed", "observation": view["observation"],
            "thought": view.get("thought"), "discoveries": list(row.get("discoveries", [])),
            "interaction_id": row["id"]}

def load():
    return validate(json.loads(Path(__file__).with_name("examples.json").read_text()))

if __name__ == "__main__":
    rows = load()
    cases = [
        ("pod", "listen", "surroundings", ()),
        ("pod", "touch", "berth", ()),
        ("pod", "examine", "hands", ()),
        ("workshop_demo", "touch", "panel", ()),
        ("workshop_demo", "touch", "panel", ("maintenance_training",)),
        ("body_demo", "taste", "mouth", ()),
        ("garden_demo", "smell", "air", ()),
    ]
    for scene, verb, target, facts in cases:
        print(scene, "/", verb, target, "/", list(facts))
        print(json.dumps(resolve(rows, scene, verb, target, facts), ensure_ascii=False))
