import json, os

p = "data/characters/characters.json"

with open(p, "r", encoding="utf-8") as f:
    d = json.load(f)

baseline_keys = ["earth", "water", "fire", "air", "ether", "spirit"]

changed = 0
for uid, ch in d.items():
    if not isinstance(ch, dict):
        continue

    pools = ch.get("pools")
    if not isinstance(pools, dict):
        pools = {}
        ch["pools"] = pools

    before = set(pools.keys())

    for k in baseline_keys:
        v = pools.get(k)
        if not isinstance(v, dict):
            v = {}
            pools[k] = v

        # normalize ints + clamp
        try:
            pmax = int(v.get("max", 0))
        except Exception:
            pmax = 0
        try:
            pcur = int(v.get("current", 0))
        except Exception:
            pcur = 0

        if pmax < 0:
            pmax = 0
        if pcur < 0:
            pcur = 0
        if pcur > pmax:
            pcur = pmax

        v["max"] = pmax
        v["current"] = pcur

    after = set(pools.keys())
    if before != after:
        changed += 1

tmp = p + ".tmp"
with open(tmp, "w", encoding="utf-8") as f:
    json.dump(d, f, ensure_ascii=False, indent=2)
os.replace(tmp, p)

print(f"patched_records={changed} total_records={len(d)}")
