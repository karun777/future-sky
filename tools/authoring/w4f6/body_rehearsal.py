"""Fictional disposable body-state authoring example; not a health simulation."""
import json
from copy import deepcopy
from pathlib import Path

def load():
    return json.loads(Path(__file__).with_name("body_example.json").read_text())

def attempt(content, state, verb):
    """Return a copied state and presentation; never update a live character."""
    verb = " ".join(verb.casefold().split())
    matches = [a for a in content["actions"] if a["verb"] == verb
               and all(state.get(k) == v for k,v in a["requires"].items())]
    if len(matches) > 1:
        raise ValueError("Overlapping authored actions")
    if not matches:
        return deepcopy(state), "No authored transition applies here."
    action = matches[0]
    if set(action["sets"]) - {"posture", "discomfort"}:
        raise ValueError("Example only owns posture and discomfort")
    updated = deepcopy(state)
    updated.update(action["sets"])
    return updated, action["text"]

if __name__ == "__main__":
    content = load()
    state = deepcopy(content["initial"])
    for verb in ["stand", "shift weight", "touch hip", "sit", "sit"]:
        before = deepcopy(state)
        state, text = attempt(content, state, verb)
        print(verb.upper() + ": " + text)
        print("  before:", before)
        print("  after: ", state)
