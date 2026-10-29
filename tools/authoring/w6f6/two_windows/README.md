# Future Sky — Two Windows (W6-F6)

Private, buildless interactive presentation study. No live API, account or game-state access.

- Open `dist/index.html` through any static HTTP server.
- `node test-engine.mjs` checks fictional state transitions.
- World and Discord-study views share one in-tab state; neither is the running Discord bot.
- Six preview seconds initiate the routine. Each walking step costs ten story minutes; presentation steps can take 3, 7 or 12 real preview seconds. Changing presentation speed leaves story costs unchanged.
- Observation does not interrupt this study; taking control does. This is a proposed distinction from the deployed all-command idle reset.
- Enable the obstacle through Experiment. The closed balcony passage requires a conscious choice to wait or detour via the stairs.
- Change the home destination to test resolution. Replay resets the fictional run.
- Sound is synthesized locally through Web Audio and is off by default. No audio recording, analytics, login or outbound game requests.
- A hidden browser tab pauses the presentation study; it does not demonstrate live server offline progression.
- Existing approved Future Sky artwork is reused. Route imagery is illustrative, with the Overlook image reused for the balcony.

## Integration boundary

A future authenticated web adapter must map a session to the correct character, authorize each action on the server, preserve normal gameplay checks, serialize overlapping Discord/web actions, and expose durable state/events for presentation. Never let this browser write character JSON. Visual delays must not become authoritative simulation time.

The Sites project is private by default. Publication does not alter the live Future Sky website or bot.
