# Future Sky — Bootstrap

**Status:** Canonical Entry Point
**Version:** 1.0
**Purpose:** Establish the minimum reading and verification sequence before changing Future Sky.

---

## Principle

Do not begin development from memory.

Do not begin development from a single document.

Begin by reconstructing the current relationship between:

- constitutional direction
- runtime contracts
- operational truth
- live code
- today’s bounded mission

The bootstrap is complete only when Future Sky can be explained back coherently at all five levels.

---

## Step 1 — Read the Trajectory

Read:

```text
00_BOOTSTRAP/TRAJECTORY_v2.1.md
```

Answer:

> What is Future Sky becoming?

Summarise:

- the constitutional direction
- the civilization spine
- the participation spine
- the capability spine
- the temporal philosophy
- the principles that implementation must not violate

Do not treat `TRAJECTORY` as an implementation specification.

---

## Step 2 — Read the Event Model

Read:

```text
02_RUNTIME/EVENT_MODEL_v4.md
```

Answer:

> How does runtime authority move through Future Sky?

Explain:

- immutable facts
- event ownership
- publishers and subscribers
- causation and correlation
- persistence before publication
- the Event Flight Recorder
- why systems must publish facts rather than invoke one another

---

## Step 3 — Read Current Operational Truth

Read the current document identified by `KNOWLEDGE_ATLAS.md` as:

```text
Current Operational State
```

At the time of this bootstrap version, the local intake candidate is:

```text
05_OPERATIONS/DEV_STATE_v6.0.md
```

However, that document is dated **20 July 2026** and describes the former Debian 12 i386 server before Neptune Lounge v2 commissioning.

It must not be treated as current operational authority without verification.

Answer:

> What is true right now?

If the operational-state document is stale, incomplete, or contradicted by the live server:

1. state that explicitly;
2. inspect the live system;
3. update or replace the operational-state document before relying on it.

---

## Step 4 — Inspect the Live Runtime

Inspect the current Neptune Lounge runtime.

Minimum checks:

```bash
cd /opt/futuresky/bot

systemctl is-active futuresky-bot
journalctl -u futuresky-bot -n 120 --no-pager
find fsbot -maxdepth 3 -type f -name "*.py" | sort
find data -maxdepth 4 -type f | sort
```

Inspect the actual files relevant to the proposed work.

Answer:

> What architecture is demonstrably running?

Distinguish clearly between:

- documented intention
- persisted state
- loaded runtime components
- verified event behaviour
- unimplemented design

The live runtime outranks recollection.

---

## Step 5 — State Today’s Mission

Before editing, state one bounded mission.

The mission must identify:

- the single feather
- the truth or boundary being changed
- files expected to change
- what must not change
- verification evidence required
- the stopping point

Do not stack unrelated work.

---

## Step 6 — Explain Future Sky Back

Before implementation, answer all of the following:

1. What is Future Sky becoming?
2. What are its governing principles?
3. How do immutable facts move through the runtime?
4. What is operationally true today?
5. What single feather is being attempted now?

Only then begin development.

---

## Authority and Conflict Handling

Documents have different kinds of authority.

Do not flatten them into one hierarchy.

Use:

- `TRAJECTORY` for constitutional direction
- runtime contracts for event and persistence rules
- the current operational-state document for present-tense system truth
- live code, state, services, and logs for verification
- the Red Book for metaphysical and narrative canon when relevant

When documents conflict with verified runtime evidence:

- do not silently reconcile them;
- identify the conflict;
- determine whether the runtime or the document is stale;
- update the appropriate operational documentation as a separate, explicit action.

---

## Feathering Rule

Work proceeds as:

```text
One bounded change
    ↓
One verification
    ↓
Stop and assess
```

If additional issues appear, record them as findings.

Do not absorb them into the current feather without explicit agreement.

---

## Closing Test

The bootstrap has succeeded when a future developer can say:

> I understand what Future Sky is becoming, how its runtime facts move, what is actually alive today, and exactly what I am changing next.

Until then, do not edit the world.
