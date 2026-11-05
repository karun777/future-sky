"use strict";
(() => {
  const el = id => document.getElementById(id);
  const POLL = 4000, STALE = 12000, TIMEOUT = 10000;
  let csrf = null, walkToken = null, inspectToken = null, view = null;
  let reading = null, moving = false, stopped = false, stale = true;
  let timer = null, failures = 0, lastSuccess = 0, exitKey = null;
  const changes = [];
  const commandHistory = [];
  let commandBusy = false;
  let observationTarget = null, observationActionsKey = null;
  let wardrobeToken = null, wardrobeKey = null, selectedGarment = null;
  let focusScene = null;
  function showFocus(id) {
    document.querySelectorAll("dialog").forEach(d => { if (d.open) d.close(); });
    focusScene = id;
    ["inspection-panel", "wardrobe-panel"].forEach(name => { el(name).hidden = name !== id; });
    el("room-scene").hidden = false;
    el("room-present").hidden = !!id;
    updateScene();
    document.querySelectorAll(".focus-location").forEach(n => { n.textContent = view?.location?.title || ""; });
  }
  function updateScene() {
    const source = focusScene === "inspection-panel" ? el("inspection-image") :
      focusScene === "wardrobe-panel" ? el("wardrobe-image") : null;
    const url = source && !source.hidden ? source.src : view?.location?.image;
    const valid = typeof url === "string" && url.startsWith("https://future-sky.net/assets/");
    const img = el("room-image");
    img.hidden = !valid; el("no-image").hidden = valid;
    if (valid) {
      if (img.src !== url) img.src = url;
      img.alt = source && !source.hidden ? source.alt : view?.location?.title || "Current room";
    } else img.removeAttribute("src");
  }
  function renderJournal(data) {
    const rows = data.journal?.entries || [];
    const entries = rows.map(entry => {
      const section = document.createElement("section");
      const h = document.createElement("h3"); h.textContent = entry.title;
      const p = document.createElement("p"); p.textContent = entry.text;
      section.append(h, p);
      const hint = document.createElement("p"); hint.className = "quiet";
      hint.textContent = entry.id === "feed7" ? "Open the signal with !feed7 in Discord." :
        (data.location.id === "pod_room" && (data.inspection?.targets || []).includes("booking") ?
        "Type inspect booking to revisit the notice." : "Return to the pod to read the notice.");
      section.append(hint); return section;
    });
    if (!entries.length) {
      const p = document.createElement("p");
      p.textContent = data.journal ? "No notices or bookings discovered yet." : "Your records are unavailable. Refresh to reconnect."; entries.push(p);
    }
    el("quest-entries").replaceChildren(...entries);
    const display = data.display;
    text("display-state", !display ? "" : "Implant · " + (!display.enabled ? "off" :
      display.state === "signal_degraded" ? "signal degraded" : display.state === "dark_mode" ? "dimmed" : "on"));
  }
  function outfitMatches(query) {
    return (view?.wardrobe?.available ? view.wardrobe.options || [] : []).filter(o =>
      o.name.toLowerCase() === query || o.id.toLowerCase() === query ||
      o.id.split(":").slice(1).join(":").toLowerCase() === query);
  }
  function examineOutfit(query) {
    const matches = outfitMatches(query);
    if (!matches.length) return false;
    if (matches.length > 1) {
      commandReply("Which outfit? Type inspect followed by " + matches.map(o => o.id).join(" or ") + ".");
      return true;
    }
    chooseGarment(matches[0]); showFocus("wardrobe-panel");
    commandReply(matches[0].name + "\n" + matches[0].description); text("command-response", "Examining " + matches[0].name + "."); return true;
  }
  function text(id, value) { if (el(id).textContent !== value) el(id).textContent = value; }
  function notice(id, value) {
    if (id === "walk-feedback") value = value.replaceAll("**", "").replaceAll(String.fromCharCode(96), "");
    text(id, value); el(id).hidden = !value;
    if (id === "walk-feedback") {
      if (value) text("command-response", value);
      text("wardrobe-status", value); el("wardrobe-status").hidden = !value;
      text("inspection-status", value); el("inspection-status").hidden = !value;
    }
  }
  function controls() {
    const blocked = stale || moving || document.hidden || !walkToken;
    el("exits").querySelectorAll("button").forEach(b => { b.disabled = blocked; });
    [...el("inspect-targets").querySelectorAll("button"), ...el("inspection-actions").querySelectorAll("button")].forEach(b => {
      b.disabled = stale || moving || document.hidden || !inspectToken;
    });
    el("wardrobe-choices").querySelectorAll("button").forEach(b => { b.disabled = stale || moving || document.hidden; });
    el("wardrobe-wear").disabled = stale || moving || document.hidden || !wardrobeToken || !selectedGarment?.action;
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
    stopped = true; stale = true; csrf = null; walkToken = null; inspectToken = null; view = null;
    clearObservation(); clearWardrobe();
    el("inspect-targets").replaceChildren();
    clearTimeout(timer);
    el("game").hidden = true; el("signed-out").hidden = false;
    ["character-name", "credits", "room-title", "room-description", "last-sync", "current-location", "display-state"].forEach(id => text(id, ""));
    ["exits", "inventory", "equipped", "recent", "quest-entries", "character-details"].forEach(id => el(id).replaceChildren());
    el("room-image").removeAttribute("src");
    changes.length = 0; exitKey = null;
    commandHistory.length = 0; el("command-history").replaceChildren();
    el("command-input").value = ""; text("command-response", "");
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
    source = source.split(/\n\s*\n/).filter(part => !part.startsWith("Follow what catches your attention:")).join("\n\n");
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
      clearObservation(); clearWardrobe();
      const home = data.idle_home?.enabled && data.idle_home?.at_home && data.idle_home?.status === "home";
      const message = home ? "Your idle return is complete. Now at " + title + "." : "Location updated: " + title + ".";
      remember(message);
      notice("walk-feedback", message);
    }
    const inspected = data.inspection || {};
    inspectToken = inspected.token || null;
    const targets = inspected.targets || [];
    if (!previous || JSON.stringify(previous.inspection?.targets || []) !== JSON.stringify(targets)) {
      text("inspect-targets", targets.length ? targets.map(t => "inspect " + t).join(" · ") : "");

    }
    const inspectionNotice = inspected.notice === "This first inspection pilot is available in the pod." ? "" : (inspected.notice || "");
    notice("inspect-notice", inspectionNotice);
    el("inspection-options").hidden = !targets.length && !inspectionNotice;
    csrf = data.session.csrf;
    walkToken = data.walking?.token || null;
    el("signed-out").hidden = true; el("game").hidden = false;
    text("character-name", data.character.name || "Traveller");
    text("credits", String(data.character.credits ?? "—"));
    if (!previous || JSON.stringify(previous.sheet) !== JSON.stringify(data.sheet)) {
      const sheet = data.sheet || {}, sections = [];
      const group = (title, rows) => {
        if (!rows.length) return;
        const section = document.createElement("section");
        const heading = document.createElement("h3"); heading.textContent = title;
        const grid = document.createElement("div"); grid.className = "sheet-grid";
        grid.replaceChildren(...rows.map(value => {
          const p = document.createElement("p"); p.textContent = value; return p;
        }));
        section.append(heading, grid); sections.push(section);
      };
      const identity = [];
      if (sheet.birthdate) identity.push("Birthdate: " + sheet.birthdate);
      if (sheet.class_id) identity.push("Class: " + sheet.class_id);
      const stats = sheet.stats || {};
      if (stats.hp !== undefined || stats.max_hp !== undefined)
        identity.push("HP: " + (stats.hp ?? "—") + " / " + (stats.max_hp ?? "—"));
      group("Profile", identity);
      group("Attributes", Object.entries(stats).filter(([key]) => !["hp", "max_hp"].includes(key))
        .map(([key, value]) => key[0].toUpperCase() + key.slice(1) + ": " + value));
      group("Elemental pools", Object.entries(sheet.pools || {}).map(([element, pool]) =>
        element[0].toUpperCase() + element.slice(1) + ": " + (pool.current ?? "—") + " / " + (pool.max ?? "—")));
      el("character-details").replaceChildren(...sections);
    }
    text("room-title", title); text("current-location", title);
    const description = data.location.description || "";
    if (!previous || description !== previous.location.description) prose(description);
    if (!previous || JSON.stringify(previous.inventory) !== JSON.stringify(data.inventory)) {
      list("inventory", data.inventory.bag.map(item => item.name + " × " + item.quantity));
      list("equipped", Object.entries(data.inventory.equipped).filter(([, item]) => item)
        .map(([slot, item]) => slot.replaceAll("_", " ") + ": " + item.name));
    }
    const exits = data.walking?.exits || [];
    const key = JSON.stringify([data.location.id, exits]);
    if (key !== exitKey) {
      text("exits", exits.length ? exits.join(" · ") : "none visible");
      exitKey = key;
    }
    notice("walk-notice", data.walking?.notice || (exits.length ? "" : "No walking exits available in this view."));
    text("inventory-guidance", !data.inventory.bag.length && !Object.values(data.inventory.equipped).some(Boolean) ?
      "Nothing is carried or equipped. If you have returned from recovery, check !pod_delivery in Discord for belongings stored in your pod." :
      "In the pod, type wear <name> to put on clothing you carry.");
    view = data; renderWardrobe(); renderObservationActions(); updateScene();
    if (!previous || JSON.stringify([previous.journal, previous.display, previous.location.id, previous.inspection?.targets]) !== JSON.stringify([data.journal, data.display, data.location.id, data.inspection?.targets])) renderJournal(data); stale = false; lastSuccess = Date.now(); failures = 0;
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
  function renderObservationActions() {
    const next = ({panels:["display","wardrobe"], display:["booking","wardrobe"], booking:["wardrobe"]})[observationTarget] || [];
    const targets = next.filter(t => (view?.inspection?.targets || []).includes(t));
    text("inspection-actions", observationTarget === "wardrobe" ?
      "Type wardrobe to browse outfits. Type look to return to the room." : targets.map(t => "inspect " + t).join(" · "));
  }
  function clearWardrobe() {
    if (focusScene === "wardrobe-panel") showFocus(null);
    wardrobeToken = null; wardrobeKey = null; selectedGarment = null;
    el("wardrobe-choices").replaceChildren();
    el("wardrobe-image").removeAttribute("src"); el("wardrobe-image").hidden = true;
    ["wardrobe-fit","garment-name","garment-description","wardrobe-status"].forEach(id => text(id,""));
    el("wardrobe-wear").hidden = true;
  }
  function chooseGarment(option) {
    selectedGarment = option;
    text("garment-name", option.name);
    text("garment-description", option.description);
    text("wardrobe-wear", option.action ? (option.action.startsWith("select:") ? "Type uniform " + option.action.slice(11) : "Type wear " + option.name) : "You have already received your first outfit. This description does not add another garment.");
    el("wardrobe-wear").hidden = false;
    controls();
  }
  function renderWardrobe() {
    const wardrobe = view?.wardrobe;
    if (!wardrobe?.available) { clearWardrobe(); return; }
    wardrobeToken = wardrobe.token || null;
    const key = JSON.stringify([wardrobe.options, wardrobe.fit, wardrobe.first_selection]);
    if (key === wardrobeKey) return;
    wardrobeKey = key;
    const equipped = Object.values(view.inventory?.equipped || {}).some(Boolean);
    text("wardrobe-fit", equipped ? "Wearing: " + (wardrobe.fit || "See inventory") : "Nothing equipped.");
    const roomImage = view.location.image;
    el("wardrobe-image").hidden = !(typeof roomImage === "string" && roomImage.startsWith("https://future-sky.net/assets/"));
    if (!el("wardrobe-image").hidden) { el("wardrobe-image").src = roomImage; el("wardrobe-image").alt = view.location.title + " — surrounding room"; }
    text("wardrobe-rule", wardrobe.first_selection ?
      "Choose your first outfit once, or wear a garment you already carry." :
      "Your first outfit has already been issued. You can examine the styles below, or wear clothing you carry.");
    el("wardrobe-choices").replaceChildren(...(wardrobe.options || []).map(option => {
      const b = document.createElement("p");
      b.textContent = option.name + (option.id.startsWith("carried:") ? " · carried" : " · outfit reference");

      return b;
    }));
    const current = (wardrobe.options || []).find(o => o.id === selectedGarment?.id);
    if (current) chooseGarment(current);
    else { selectedGarment = null; text("garment-name", "Examine an outfit");
      text("garment-description", "Type inspect followed by an outfit name to examine it.");
      el("wardrobe-wear").hidden = true; }
  }
  async function wearGarment() {
    if (moving || stale || stopped || document.hidden || !wardrobeToken || !selectedGarment?.action) return;
    if (Date.now() - lastSuccess > STALE) {
      markStale("Checking your wardrobe before changing…"); refresh(); return;
    }
    const selectedRoom = view.location.id, action = selectedGarment.action;
    if (reading) await reading;
    if (moving || stale || stopped || document.hidden || !wardrobeToken) return;
    if (view.location.id !== selectedRoom || !(view.wardrobe?.options || []).some(o => o.action === action)) {
      notice("walk-feedback", "Your wardrobe changed. Examine your current options."); return;
    }
    moving = true; clearTimeout(timer);
    const token = wardrobeToken; wardrobeToken = null; walkToken = null; inspectToken = null; controls();
    notice("walk-feedback", "Changing clothes…");
    let message = "";
    try {
      const {response, body} = await request("/play/api/wardrobe", {
        method:"POST", headers:{"Content-Type":"application/json","X-CSRF-Token":csrf || ""},
        body:JSON.stringify({action,token})
      });
      if (response.status === 401 || response.status === 403) { signedOut("Sign in again to continue."); return; }
      message = typeof body === "string" ? body : body.message || "Check your current fit.";
    } catch (_) {
      message = "The wardrobe response was interrupted. Checking your fit; the action will not be repeated.";
      markStale("Checking your saved equipment.");
    } finally { moving = false; stale = true; controls(); }
    if (!stopped) { await refresh(); if (!stopped) notice("walk-feedback", message); }
  }
  function clearObservation() {
    if (focusScene === "inspection-panel") showFocus(null);
    observationTarget = null; observationActionsKey = null;
    el("inspection-actions").replaceChildren();
    text("inspection-status", ""); el("inspection-status").hidden = true;
    text("inspection-title", "");
    el("inspection-text").replaceChildren();
    el("inspection-guidance").replaceChildren();
    el("inspection-image").removeAttribute("src");
    el("inspection-image").hidden = true;
  }
  function showObservation(observation, target) {
    clearObservation();
    observationTarget = target;
    renderObservationActions(); controls();
    text("inspection-title", observation.title || "Your attention");
    for (const [id, source] of [["inspection-text", observation.text || ""],
                                ["inspection-guidance", ""]]) {
      el(id).replaceChildren(...source.split(/\n\s*\n/).filter(Boolean).map(part => {
        const p = document.createElement("p"); inline(p, part); return p;
      }));
    }
    const url = observation.image || view?.location?.image;
    if (typeof url === "string" && url.startsWith("https://future-sky.net/assets/")) {
      el("inspection-image").src = url;
      el("inspection-image").alt = observation.image ? observation.title || "Observed detail" : (view?.location?.title || "Room") + " — surrounding room";
      el("inspection-image").hidden = false;
    }
    showFocus("inspection-panel");
  }
  async function inspect(target) {
    if (moving || stale || !inspectToken || document.hidden || stopped) return;
    if (Date.now() - lastSuccess > STALE) {
      markStale("Checking the current room before you inspect…"); refresh(); return;
    }
    const selectedRoom = view.location.id;
    if (reading) await reading;
    if (moving || stale || stopped || !inspectToken) return;
    if (view.location.id !== selectedRoom || !(view.inspection?.targets || []).includes(target)) {
      notice("walk-feedback", "Your situation changed. Choose a current detail."); return;
    }
    moving = true; clearTimeout(timer);
    const token = inspectToken; inspectToken = null; walkToken = null; controls();
    notice("walk-feedback", "Attending…");
    let observation = null, message = "";
    try {
      const {response, body} = await request("/play/api/inspect", {
        method: "POST", headers: {"Content-Type":"application/json", "X-CSRF-Token":csrf || ""},
        body: JSON.stringify({target, token})
      });
      if (response.status === 401 || response.status === 403) { signedOut("Sign in again to continue."); return; }
      if (response.ok && body.ok && body.observation) observation = body.observation;
      else message = typeof body === "string" ? body : body.message || "Refresh before inspecting again.";
    } catch (_) {
      message = "The inspection response was interrupted. Checking your character; the action will not be repeated.";
      markStale("Connection interrupted. Checking saved discoveries.");
    } finally { moving = false; stale = true; controls(); }
    if (!stopped) {
      await refresh();
      if (!stopped && !stale && observation && view.location.id === selectedRoom) {
        showObservation(observation, target);
        message = "Attending to " + (observation.title || target) + ".";
      } else if (observation && !stopped) message = "Observation saved; return to a current view before reading it again.";
      if (!stopped) notice("walk-feedback", message);
    }
  }

  function openPanel(id) {
    document.querySelectorAll("dialog").forEach(d => { if (d.open) d.close(); });
    if (id === "wardrobe-panel") showFocus(id);
    else el(id).show();
  }
  function commandReply(message) {
    text("command-response", message);
    if (message.startsWith("> ")) {
      commandHistory.unshift({command: message.slice(2), result: ""});
      commandHistory.splice(30);
    } else if (commandHistory.length) commandHistory[0].result = message;
    el("command-history").replaceChildren(...commandHistory.map(entry => {
      const row = document.createElement("li");
      const cmd = document.createElement("code"); cmd.textContent = "> " + entry.command;
      const result = document.createElement("p"); result.textContent = entry.result;
      row.append(cmd, result); return row;
    }));
  }
  async function issueCommand(event) {
    event.preventDefault();
    if (commandBusy || moving || stopped || document.hidden) return;
    const input = el("command-input");
    const raw = input.value.trim();
    if (!raw) return;
    if (raw.length > 200) { commandReply("Keep each command under 200 characters."); return; }
    const command = raw.replace(/^!/, "").trim().replace(/\s+/g, " ");
    const lower = command.toLowerCase();
    const [verb, ...parts] = lower.split(" ");
    const argument = parts.join(" ");
    commandBusy = true; input.disabled = true;
    try {
      if (stale || Date.now() - lastSuccess > STALE) await refresh();
      if (stopped || stale || document.hidden) { commandReply("Connection paused. Try again when this window is up to date."); return; }
      commandReply("> " + raw);
      if (lower === "help" || lower === "commands") {
        openPanel("actions"); commandReply("Commands are listed in the Commands panel."); return;
      }
      if (lower === "look") {
        document.querySelectorAll("dialog").forEach(d => { if (d.open) d.close(); });
        showFocus(null);
        await refresh();
        if (!stopped) commandReply("Attending to " + (view?.location?.title || "the room") + ".");
        return;
      }
      if (["quests","quest log","journal"].includes(lower)) {
        openPanel("quest-panel"); commandReply("Quest Log opened."); return;
      }
      if (["inventory","character","sheet","fit"].includes(lower)) {
        openPanel(lower === "inventory" || lower === "fit" ? "inventory-panel" : "character-panel");
        commandReply(lower === "fit" ? "Wearing: " + (view.wardrobe?.fit || el("equipped").textContent) : "Panel opened.");
        return;
      }
      if (verb === "go" && argument) {
        if (!(view.walking?.exits || []).includes(argument)) { commandReply("Available exits: " + (view.walking?.exits || []).join(", ")); return; }
        await walk(argument);
      } else if (verb === "inspect" && argument) {
        const target = ({"storage panels":"panels","booking notice":"booking"})[argument] || argument;
        if (!(view.inspection?.targets || []).includes(target) && examineOutfit(argument)) return;
        if (!(view.inspection?.targets || []).includes(target)) {
          commandReply("That inspection is not available here in the web window. Available: " + (view.inspection?.targets || []).join(", ")); return;
        }
        await inspect(target);
      } else if (verb === "wardrobe") {
        if (!view.wardrobe?.available) {
          commandReply("Inspect the wardrobe first: inspect wardrobe. Available details: " + (view.inspection?.targets || []).join(", ")); return;
        }
        if (argument && !argument.startsWith("inspect ")) { commandReply("Use wardrobe or wardrobe inspect <outfit>."); return; }
        if (argument) {
          if (!examineOutfit(argument.slice(8))) commandReply("That outfit is not listed. Type wardrobe to browse.");
          return;
        }
        openPanel("wardrobe-panel");
        commandReply(argument ? selectedGarment.description : "Wardrobe opened. Examine an outfit before choosing what to wear."); return;
      } else if ((verb === "wear" || verb === "uniform") && argument) {
        const options = view.wardrobe?.options || [];
        const option = options.find(o => verb === "uniform" ?
          o.action === "select:pod_" + argument.replace(/^pod_/, "") :
          o.action?.startsWith("wear:") && (o.name.toLowerCase() === argument || o.action.slice(5) === argument));
        if (!option) {
          commandReply(verb === "wear" ? "You cannot wear that from the current wardrobe offer. Type wardrobe to see carried clothing." :
            "That first outfit choice is unavailable. First selection is once only; use wear for carried clothes."); return;
        }
        chooseGarment(option);
        await wearGarment();
      } else {
        commandReply("That command is not connected to the web window yet. Type help for supported commands. Discord remains available."); return;
      }
      if (!stopped) {
        const feedback = el("walk-feedback").textContent || "Done.";
        const detail = verb === "inspect" && focusScene === "inspection-panel" ?
          el("inspection-title").textContent + "\n" + el("inspection-text").textContent : feedback;
        commandReply(detail); text("command-response", feedback);
      }
    } catch (_) {
      if (!stopped) commandReply("The command could not be completed. Refresh before trying again; it was not automatically repeated.");
    } finally {
      commandBusy = false; input.disabled = stopped;
      if (!stopped && !document.hidden) input.focus();
    }
  }
  el("command-form").addEventListener("submit", issueCommand);
  el("refresh").addEventListener("click", refresh);
  el("inspection-image").addEventListener("error", () => { el("inspection-image").hidden = true; });
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
