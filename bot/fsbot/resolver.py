# ============================================================
# FILE META — fsbot/resolver.py
# Canonical name: Modifier Layer Resolver (effective character view + hooks)
#
# Version: v0.1.2
# Last edited: 2026-01-23 (Australia/Perth)
#
# Authority:
# - AUTHORITATIVE for computing an in-memory "effective character view"
#   from (spine + context + modifier layers).
# - This module performs NO I/O and must NEVER write to Storage/JSON.
#
# Purpose:
# - Computes an "effective character view" from:
#     (1) a minimal character spine (authoritative inputs)
#     (2) an optional context dict (event/room/etc)
#     (3) a list of modifier layers (data/modifiers/layers.json)
# - Returns:
#     { view, hooks, applied_layers, skipped_layers }
#
# Contracts (v0):
# - Layers are dicts with: id, enabled, priority, scope, selector, conditions, mods/effects, hooks
# - Compat: supports layer["mods"] OR legacy layer["effects"] (same schema).
# - Selector (minimal):
#     selector.user_ids: allow-only those character ids
#     unknown selector keys => fail closed (skip layer)
# - Conditions: AND semantics
#     missing paths fail comparisons except exists:false
#     unknown comparator keys => fail closed (skip layer)
#
# Boundaries / discipline (LOCKED):
# - Pure in-memory transformation: NEVER writes to storage or performs I/O.
# - Fail-closed selectors/conditions: unknown keys skip layer safely.
# - Safe dotted-path set: overwrites non-dicts on the path with dicts (resolver must not crash).
# - Pools are clamped after each layer and at end:
#     current in [0,max], max >= 0
#
# Used by:
# - fsbot/storage.py via Storage.resolve_for_combat() (Phase 1 bridge)
#
# Operational notes / hazards:
# - This module is intentionally dependency-light (no discord imports).
# - Layers are treated as untrusted input: all operations are best-effort + safe.
# ============================================================

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List, Optional, Tuple


# -------------------------
# Path helpers (scalar paths)
# -------------------------

def _get_path(d: Dict[str, Any], path: str) -> Any:
    cur: Any = d
    for part in path.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def _ensure_path(d: Dict[str, Any], path: str) -> Tuple[Dict[str, Any], str]:
    """
    Ensure parent dictionaries exist for a dotted path.
    Returns (parent_dict, last_key).

    Resolver MUST be safe:
    - If a non-dict is in the way, overwrite it with dict.
    """
    parts = path.split(".")
    cur: Any = d

    for p in parts[:-1]:
        if not isinstance(cur, dict):
            # If root is somehow non-dict, bail safe
            return d, parts[-1]

        if p not in cur or not isinstance(cur[p], dict):
            cur[p] = {}
        cur = cur[p]

    if not isinstance(cur, dict):
        return d, parts[-1]

    return cur, parts[-1]


def _set_path(d: Dict[str, Any], path: str, value: Any) -> None:
    parent, key = _ensure_path(d, path)
    parent[key] = value


# -------------------------
# Conditions
# -------------------------

def _cond_exists(value: Any, want_exists: bool) -> bool:
    return (value is not None) if want_exists else (value is None)


def eval_conditions(conditions: List[Dict[str, Any]], view: Dict[str, Any]) -> bool:
    """
    AND semantics.
    Missing paths fail comparisons (except exists:false).
    Unknown comparator => fail closed.
    """
    for c in conditions or []:
        path = c.get("path")
        if not path or not isinstance(path, str):
            return False

        actual = _get_path(view, path)

        # exists comparator
        if "exists" in c:
            want_exists = bool(c["exists"])
            if not _cond_exists(actual, want_exists):
                return False
            continue

        # Any other comparator: missing path fails safe
        if actual is None:
            return False

        # eq / ne
        if "eq" in c:
            if actual != c["eq"]:
                return False
            continue
        if "ne" in c:
            if actual == c["ne"]:
                return False
            continue

        # ordering
        if "gt" in c:
            if not (actual > c["gt"]):
                return False
            continue
        if "gte" in c:
            if not (actual >= c["gte"]):
                return False
            continue
        if "lt" in c:
            if not (actual < c["lt"]):
                return False
            continue
        if "lte" in c:
            if not (actual <= c["lte"]):
                return False
            continue

        # membership
        if "in" in c:
            hay = c["in"]
            if not isinstance(hay, list):
                return False
            if actual not in hay:
                return False
            continue

        # Unknown comparator => fail closed
        return False

    return True


# -------------------------
# Selector (minimal)
# -------------------------

def eval_selector(selector: Any, view: Dict[str, Any]) -> bool:
    """
    Minimal v0 selector support:
    - selector.user_ids: list of allowed character ids
    If selector is missing -> pass.
    If selector is invalid/unknown keys -> fail closed.
    """
    if selector is None:
        return True
    if not isinstance(selector, dict):
        return False

    user_ids = selector.get("user_ids")
    if user_ids is not None:
        if not isinstance(user_ids, list):
            return False
        me = str(view.get("id", ""))
        allowed = {str(x) for x in user_ids if str(x)}
        return me in allowed

    # Unknown selector keys -> fail closed (safer)
    return False


# -------------------------
# Pools
# -------------------------

def _ensure_pool(view: Dict[str, Any], pool_name: str) -> Dict[str, Any]:
    pools = view.setdefault("pools", {})
    if not isinstance(pools, dict):
        view["pools"] = {}
        pools = view["pools"]

    if pool_name not in pools or not isinstance(pools[pool_name], dict):
        pools[pool_name] = {"current": 0, "max": 0}

    pool = pools[pool_name]

    if "current" not in pool:
        pool["current"] = 0
    if "max" not in pool:
        pool["max"] = 0

    try:
        pool["current"] = int(pool["current"])
    except Exception:
        pool["current"] = 0

    try:
        pool["max"] = int(pool["max"])
    except Exception:
        pool["max"] = 0

    return pool


def clamp_pools(view: Dict[str, Any]) -> None:
    pools = view.get("pools")
    if not isinstance(pools, dict):
        return

    for name, p in list(pools.items()):
        if not isinstance(p, dict):
            pools[name] = {"current": 0, "max": 0}
            p = pools[name]

        cur = p.get("current", 0)
        mx = p.get("max", 0)

        try:
            cur = int(cur)
        except Exception:
            cur = 0

        try:
            mx = int(mx)
        except Exception:
            mx = 0

        if mx < 0:
            mx = 0
        if cur < 0:
            cur = 0
        if cur > mx:
            cur = mx

        p["current"] = cur
        p["max"] = mx


# -------------------------
# Mods application
# -------------------------

def _get_numeric_scalar(view: Dict[str, Any], path: str) -> float:
    v = _get_path(view, path)
    if v is None:
        return 0.0
    try:
        return float(v)
    except Exception:
        return 0.0


def apply_mod(view: Dict[str, Any], mod: Dict[str, Any]) -> None:
    op = mod.get("op")
    if not op:
        return

    # Pool ops (explicit)
    if op in ("pool_add_max", "pool_add_current", "pool_set_max", "pool_set_current"):
        pool_name = mod.get("pool")
        if not isinstance(pool_name, str) or not pool_name:
            return

        pool = _ensure_pool(view, pool_name)

        val = mod.get("value", 0)
        try:
            val_i = int(val)
        except Exception:
            val_i = 0

        if op == "pool_add_max":
            pool["max"] = int(pool.get("max", 0)) + val_i
        elif op == "pool_add_current":
            pool["current"] = int(pool.get("current", 0)) + val_i
        elif op == "pool_set_max":
            pool["max"] = val_i
        elif op == "pool_set_current":
            pool["current"] = val_i
        return

    # Scalar ops (path-based)
    path = mod.get("path")
    if not isinstance(path, str) or not path:
        return

    if op == "set":
        _set_path(view, path, mod.get("value"))
        return

    val = mod.get("value", 0)
    try:
        val_f = float(val)
    except Exception:
        val_f = 0.0

    current = _get_numeric_scalar(view, path)

    if op == "add":
        _set_path(view, path, current + val_f)
    elif op == "mul":
        _set_path(view, path, current * val_f)
    elif op == "min":
        _set_path(view, path, min(current, val_f))
    elif op == "max":
        _set_path(view, path, max(current, val_f))
    else:
        # Unknown op: no-op (safe)
        return


# -------------------------
# Resolver
# -------------------------

def resolve_effective_character(
    spine: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None,
    layers: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Produce an effective character view by merging:
      base = context (if dict) + spine (authoritative fields)
    Then apply layers (sorted by priority asc).

    Returns:
      {
        "view": {...},
        "hooks": { when: [hook, ...] },
        "applied_layers": [layer_id, ...],
        "skipped_layers": [layer_id, ...],
      }
    """
    base: Dict[str, Any] = deepcopy(context) if isinstance(context, dict) else {}

    # Spine overwrites context for authoritative keys
    for k in ("id", "name", "stats", "pools", "vitals", "combat", "profile", "progression", "astro"):
        if k in spine:
            base[k] = deepcopy(spine[k])

    # Ensure required namespaces are dicts
    if "stats" not in base or not isinstance(base["stats"], dict):
        base["stats"] = {}
    if "pools" not in base or not isinstance(base["pools"], dict):
        base["pools"] = {}
    if "combat" not in base or not isinstance(base["combat"], dict):
        base["combat"] = {}

    clamp_pools(base)

    layer_list = layers if isinstance(layers, list) else []
    layer_list_sorted = sorted(
        layer_list,
        key=lambda L: int(L.get("priority", 50)) if isinstance(L, dict) else 50,
    )

    hooks_by_when: Dict[str, List[Dict[str, Any]]] = {}
    applied_layers: List[str] = []
    skipped_layers: List[str] = []

    for layer in layer_list_sorted:
        if not isinstance(layer, dict):
            continue

        layer_id = str(layer.get("id", "")).strip()
        if not layer_id:
            continue

        if layer.get("enabled", True) is False:
            skipped_layers.append(layer_id)
            continue

        # scope gate (minimal): only character scope is supported in v0
        scope = layer.get("scope")
        if scope is not None and str(scope) not in ("character", ""):
            skipped_layers.append(layer_id)
            continue

        # selector gate (v0)
        selector = layer.get("selector")
        if selector is not None and not eval_selector(selector, base):
            skipped_layers.append(layer_id)
            continue

        # conditions gate (AND)
        conds = layer.get("conditions", [])
        if conds and not eval_conditions(conds, base):
            skipped_layers.append(layer_id)
            continue

        # ✅ Compat: layer.mods OR legacy layer.effects
        mods = layer.get("mods", None)
        if mods is None:
            mods = layer.get("effects", [])

        if isinstance(mods, list):
            for m in mods:
                if isinstance(m, dict):
                    apply_mod(base, m)

        # Hooks collection (read-only)
        hooks = layer.get("hooks", [])
        if isinstance(hooks, list):
            for h in hooks:
                if not isinstance(h, dict):
                    continue
                when = h.get("when")
                if not isinstance(when, str) or not when:
                    continue

                h_conds = h.get("conditions", [])
                if h_conds and not eval_conditions(h_conds, base):
                    continue

                hooks_by_when.setdefault(when, []).append(deepcopy(h))

        applied_layers.append(layer_id)
        clamp_pools(base)

    clamp_pools(base)

    return {
        "view": base,
        "hooks": hooks_by_when,
        "applied_layers": applied_layers,
        "skipped_layers": skipped_layers,
    }
