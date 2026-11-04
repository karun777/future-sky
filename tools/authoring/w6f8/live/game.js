"use strict";
(() => {
  const el = id => document.getElementById(id);
  const POLL = 4000, STALE = 12000, TIMEOUT = 10000;
  let csrf = null, walkToken = null, view = null;
  let reading = null, moving = false, stopped = false, stale = true;
  let timer = null, failures = 0, lastSuccess = 0, exitKey = null;
  const changes = [];
  function text(id, value) { if (el(id).textContent !== value) el(id).textContent = value; }
  function notice(id, value) { text(id, value); el(id).hidden = !value; }
  function controls() {
    const blocked = stale || moving || document.hidden || !walkToken;
    el("exits").querySelectorAll("button").forEach(b => { b.disabled = blocked; });
    el("refresh").disabled = moving || !!reading;
    el("logout").disabled = moving;
  }
  function connection(label) { text("connection", label); el("connection").dataset.state = stale ? "stale" : "current"; }
  function markStale(message) {
    stale = true;
    connection("Updates paused");
    notice("message", message);
    controls();
  }
  function signedOut(message = "") {
    stopped = true; stale = true; csrf = null; walkToken = null; view = null;
    clearTimeout(timer);
    el("game").hidden = true; el("signed-out").hidden = false;
    ["character-name", "credits", "room-title", "room-description", "last-sync"].forEach(id => text(id, ""));
    ["exits", "inventory", "equipped", "recent"].forEach(id => el(id).replaceChildren());
    el("room-image").removeAttribute("src");
    changes.length = 0; exitKey = null;
    notice("walk-feedback", ""); text("recent-count", "");
    connection("Signed out"); notice("message", message); controls();
  }
  // A small display grammar, not an HTML or arbitrary Markdown interpreter.
  // Text always enters through textContent/createTextNode.
  function inline(parent, source, depth = 0) {
    if (depth > 4) { parent.append(document.createTextNode(source)); return; }
    const pattern = /\*\*([^\n]+?)\*\*|\x60([^\x60\n]+)\x60|\*([^*\n]+)\*/g;
    let match, cursor = 0;
    while ((match = pattern.exec(source))) {
      parent.append(document.createTextNode(source.slice(cursor, match.index)));
      const tag = match[1] !== undefined ? "strong" : match[2] !== undefined ? "code" : "em";
      const node = document.createElement(tag);
      const value = match[1] ?? match[2] ?? match[3];
      if (tag === "code") node.textContent = value;
      else inline(node, value, depth + 1);
      parent.append(node);
      cursor = pattern.lastIndex;
    }
    parent.append(document.createTextNode(source.slice(cursor)));
  }
  function prose(source) {
    el("room-description").replaceChildren(...source.split(/\n\s*\n/).filter(Boolean).map(part => {
      const p = document.createElement("p"); inline(p, part); return p;
    }));
  }
  function list(id, values) {
    const rows = values.length ? values : [id === "equipped" ? "Nothing equipped" : "Nothing carried"];
    el(id).replaceChildren(...rows.map(value => {
      const li = document.createElement("li"); li.textContent = value; return li;
    }));
  }
  function remember(message) {
    changes.unshift(new Date().toLocaleTimeString([], {hour: "2-digit", minute: "2-digit"}) + " · " + message);
    changes.splice(4);
    el("recent").replaceChildren(...changes.map(value => {
      const li = document.createElement("li"); li.textContent = value; return li;
    }));
    text("recent-count", "(" + changes.length + ")");
  }
  function render(data) {
    const previous = view;
    const title = data.location.title || "Location withheld";
    if (previous && previous.location.id !== data.location.id) {
      const home = data.idle_home?.enabled && data.idle_home?.at_home && data.idle_home?.status === "home";
      const message = home ? "Your idle return is complete. Now at " + title + "." : "Location updated: " + title + ".";
      remember(message);
      notice("walk-feedback", message);
    }
    csrf = data.session.csrf;
    walkToken = data.walking?.token || null;
    el("signed-out").hidden = true; el("game").hidden = false;
    text("character-name", data.character.name || "Traveller");
    text("credits", String(data.character.credits ?? "—"));
    text("room-title", title);
    const description = data.location.description || "";
    if (!previous || description !== previous.location.description) prose(description);
    const img = el("room-image"), url = data.location.image;
    const valid = typeof url === "string" && url.startsWith("https://future-sky.net/assets/");
    if (!previous || url !== previous.location.image) {
      img.hidden = !valid; el("no-image").hidden = valid;
      if (valid) { img.src = url; img.alt = title; }
      else img.removeAttribute("src");
    }
    if (!previous || JSON.stringify(previous.inventory) !== JSON.stringify(data.inventory)) {
      list("inventory", data.inventory.bag.map(item => item.name + " × " + item.quantity));
      list("equipped", Object.entries(data.inventory.equipped).filter(([, item]) => item)
        .map(([slot, item]) => slot.replaceAll("_", " ") + ": " + item.name));
    }
    const exits = data.walking?.exits || [];
    const key = JSON.stringify([data.location.id, exits]);
    if (key !== exitKey) {
      el("exits").replaceChildren(...exits.map(direction => {
        const button = document.createElement("button");
        button.type = "button"; button.textContent = "Go " + direction;
        button.addEventListener("click", () => walk(direction));
        return button;
      }));
      exitKey = key;
    }
    notice("walk-notice", data.walking?.notice || (exits.length ? "" : "No walking exits available in this view."));
    view = data; stale = false; lastSuccess = Date.now(); failures = 0;
    connection("Up to date");
    text("last-sync", "Checked " + new Date(lastSuccess).toLocaleTimeString());
    notice("message", "");
    controls();
  }
  async function request(url, options = {}) {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), TIMEOUT);
    try {
      const response = await fetch(url, {credentials: "same-origin", cache: "no-store", ...options, signal: controller.signal});
      // Keep the timeout active while consuming a slow response body.
      const body = response.headers.get("Content-Type")?.includes("application/json") ?
        await response.json() : await response.text();
      return {response, body};
    } finally { clearTimeout(timeout); }
  }
  function schedule() {
    clearTimeout(timer);
    if (stopped || document.hidden || navigator.onLine === false) return;
    timer = setTimeout(refresh, Math.min(30000, POLL * (2 ** Math.min(failures, 3))));
  }
  async function refresh() {
    if (stopped || moving || document.hidden) return;
    if (reading) return reading;
    if (navigator.onLine === false) { markStale("You’re offline. Showing the last known view; movement is paused."); return; }
    reading = (async () => {
      try {
        const {response, body} = await request("/play/api/me");
        if (response.status === 401 || response.status === 403) {
          signedOut(response.status === 401 ? "Sign in to reconnect to your character." : "This character is unavailable to this account.");
          return;
        }
        if (!response.ok) throw new Error("unavailable");
        render(body);
      } catch (_) {
        failures += 1;
        markStale("Connection interrupted. Showing the last known view; retrying automatically.");
      }
    })();
    controls();
    try { await reading; }
    finally {
      reading = null;
      if (!stopped && document.hidden) markStale("Updates paused while this tab is hidden.");
      else if (!stopped && navigator.onLine === false) markStale("You’re offline. Showing the last known view; movement is paused.");
      controls(); schedule();
    }
  }
  async function walk(direction) {
    if (moving || stale || !walkToken || document.hidden || stopped) return;
    if (Date.now() - lastSuccess > STALE) {
      markStale("Checking the current room before you move…");
      refresh(); return;
    }
    const selectedRoom = view.location.id;
    // Finish a pending observational read before sending a command. If it
    // changed location, ask for a fresh choice instead of reinterpreting intent.
    if (reading) await reading;
    if (moving || stale || stopped || !walkToken) return;
    if (view.location.id !== selectedRoom || !(view.walking?.exits || []).includes(direction)) {
      notice("walk-feedback", "Your location changed. Choose an exit from the current room.");
      return;
    }
    moving = true; clearTimeout(timer);
    const token = walkToken; walkToken = null; controls();
    notice("walk-feedback", "Walking…");
    let message;
    try {
      const {response, body} = await request("/play/api/walk", {
        method: "POST", headers: {"Content-Type": "application/json", "X-CSRF-Token": csrf || ""},
        body: JSON.stringify({direction, token})
      });
      if (response.status === 401 || response.status === 403) { signedOut("Sign in again to continue."); return; }
      message = typeof body === "object" ? body.message : body;
      if (!message) message = "Check your current location before moving again.";
    } catch (_) {
      message = "The movement response was interrupted. Checking your location; the action will not be repeated.";
      markStale("Connection interrupted. Checking the saved location.");
    } finally {
      moving = false; stale = true; controls();
    }
    if (!stopped) {
      await refresh();
      notice("walk-feedback", message);
    }
  }
  el("refresh").addEventListener("click", refresh);
  el("room-image").addEventListener("error", () => {
    el("room-image").hidden = true; el("no-image").hidden = false;
  });
  el("logout").addEventListener("click", async () => {
    if (moving || stopped) return;
    if (reading) await reading;
    if (stopped || moving) return;
    moving = true; clearTimeout(timer); controls();
    try {
      const {response} = await request("/play/logout", {method: "POST", headers: {"X-CSRF-Token": csrf || ""}});
      if (!response.ok && response.status !== 401) throw new Error("logout");
      signedOut("Signed out.");
    } catch (_) { markStale("Sign-out could not be confirmed. Reconnect and try again."); }
    finally { moving = false; controls(); schedule(); }
  });
  document.addEventListener("visibilitychange", () => {
    clearTimeout(timer);
    if (stopped) return;
    if (document.hidden) { markStale("Updates paused while this tab is hidden."); }
    else { markStale("Checking what changed…"); refresh(); }
  });
  window.addEventListener("offline", () => { clearTimeout(timer); if (!stopped) markStale("You’re offline. Showing the last known view; movement is paused."); });
  window.addEventListener("online", () => { if (!stopped) refresh(); });
  window.addEventListener("focus", () => { if (!stopped && !document.hidden && Date.now() - lastSuccess > POLL) refresh(); });
  setInterval(() => {
    if (!stopped && !document.hidden && !moving && !stale && Date.now() - lastSuccess > STALE)
      markStale("This view is out of date. Checking the connection…");
  }, 1000);
  refresh();
})();
