# W4-F6 — sensory interaction authoring rehearsal

Offline prototype, 19 October 2026. No bot integration, live data or deployed commands.
Edit examples.json to author a verb/target response. Run:
```sh
cd /opt/futuresky/tools/authoring/w4f6
python3 interactions.py
python3 -m unittest -v
```

Each entry has a scene, verb, target aliases, sense and observation. Optional thought is tentative authored inner speech; it is not a universal intuition system. Optional requires lists positive context facts supplied by the caller. Optional variants supply character-specific wording; overlapping eligible variants fail visibly. Optional discoveries are proposals returned to the caller, never saved here.

Pod maintenance is ordinary building maintenance (Karun, 19 October); no mystery, quest or escalating investigation is implied. Its source remains uncertain to the character in the sample.
All sample wording is review content. workshop_demo, body_demo and garden_demo are fictional test settings, not new canon locations. The warmth, taste, smell and training are authoring examples, not live character conditions or pod additions.

No sense-unlock timeline is implemented. Unknown/unmodelled sensory availability is distinct from explicitly unavailable in rehearsal. Facts must come from a future authorised context adapter; do not pass all private world facts into player-facing context indiscriminately.

The resolver demonstrates authored observation, contextual variation and proposed discovery output. It does not implement manipulation, events, pain progression, proximity physics, inventory, gear or character creation. Existing stewards must own those effects when integration is designed.
Unsupported means missing authoring, not evidence that the target cannot be sensed. Production refusals need authored context and useful guidance.

Authoring review: can Karun add a new target, change wording, and add one conditional response without editing Python? Is that content clearer than a list of bespoke command handlers?

## Bodily action rehearsal
Run python3 body_rehearsal.py. Edit body_example.json to change the fictional posture/discomfort transitions and wording. This is a separate throwaway state-transition rehearsal, not integration with the sensory resolver or production character store. It asserts no diagnosis, healing, injury mechanism or pain threshold. Repeated/unsupported actions return missing-authoring guidance, not a physical impossibility claim. Four checks cover action sequence, out-of-order attempts, nonmutation/isolation and overlapping conditions.
