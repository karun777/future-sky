"use strict";
(() => {
  const el = id => document.getElementById(id);
  let csrf = null;
  let busy = false;
  let walkToken = null;
  function signedOut() {
    csrf = null;
    walkToken = null;
    el("exits").replaceChildren();
    el("game").hidden = true;
    el("signed-out").hidden = false;
    el("character-name").textContent = "";
    el("inventory").replaceChildren();
    el("equipped").replaceChildren();
    el("room-image").removeAttribute("src");
    el("connection").textContent = "Signed out";
  }
  function list(id, values) {
    const rows = values.length ? values : ["Nothing shown"];
    el(id).replaceChildren(...rows.map(text => {
      const li = document.createElement("li");
      li.textContent = text;
      return li;
    }));
  }
  async function refresh() {
    if (busy) return;
    busy = true;
    el("refresh").disabled = true;
    try {
      const response = await fetch("/play/api/me", {cache: "no-store", credentials: "same-origin"});
      if (response.status === 401) { signedOut(); return; }
      if (!response.ok) {
        if (response.status === 403) signedOut();
        throw new Error(response.status === 403 ? "This pilot account is not authorised." :
                        "The game connection is unavailable. Try refreshing shortly.");
      }
      const data = await response.json();
      csrf = data.session.csrf;
      walkToken = data.walking?.token || null;
      el("room-description").textContent = data.location.description || "";
      el("walk-notice").textContent = data.walking?.notice || "";
      el("exits").replaceChildren(...(data.walking?.exits || []).map(direction => {
        const button = document.createElement("button");
        button.type = "button";
        button.textContent = "Go " + direction;
        button.addEventListener("click", () => walk(direction));
        return button;
      }));

      el("signed-out").hidden = true;
      el("game").hidden = false;
      el("character-name").textContent = data.character.name || "Traveller";
      el("credits").textContent = data.character.credits ?? "—";
      el("room-title").textContent = data.location.title || "Location withheld";
      const img = el("room-image");
      const url = data.location.image;
      const validImage = typeof url === "string" && url.startsWith("https://future-sky.net/assets/");
      img.hidden = !validImage;
      el("no-image").hidden = validImage;
      if (validImage) { img.src = url; img.alt = data.location.title || "Current room"; }
      else img.removeAttribute("src");
      list("inventory", data.inventory.bag.map(item => item.name + " × " + item.quantity));
      list("equipped", Object.entries(data.inventory.equipped)
        .filter(([, item]) => item).map(([slot, item]) => slot.replaceAll("_", " ") + ": " + item.name));
      el("connection").textContent = "Connected · " + new Date().toLocaleTimeString();
      el("message").textContent = "";
    } catch (error) {
      el("connection").textContent = "Not refreshed";
      el("message").textContent = error.message || "Could not refresh.";
    } finally { busy = false; el("refresh").disabled = false; }
  }
  async function walk(direction) {
    if (busy || !walkToken) return;
    busy = true;
    const token = walkToken;
    walkToken = null;
    el("refresh").disabled = true;
    el("logout").disabled = true;
    el("exits").querySelectorAll("button").forEach(button => { button.disabled = true; });
    el("walk-feedback").textContent = "Walking…";
    let feedback = "";
    try {
      const response = await fetch("/play/api/walk", {
        method: "POST", credentials: "same-origin",
        headers: {"Content-Type": "application/json", "X-CSRF-Token": csrf || ""},
        body: JSON.stringify({direction, token})
      });
      if (response.status === 401) { signedOut(); return; }
      if (response.headers.get("Content-Type")?.includes("application/json")) {
        feedback = (await response.json()).message;
      } else {
        feedback = await response.text();
      }
    } catch (_) {
      feedback = "Connection interrupted. Refresh to check your location before moving again.";
    } finally {
      busy = false;
      el("refresh").disabled = false;
      el("logout").disabled = false;
    }
    await refresh();
    el("walk-feedback").textContent = feedback;
  }
  el("room-image").addEventListener("error", () => {
    el("room-image").hidden = true;
    el("no-image").hidden = false;
  });
  el("refresh").addEventListener("click", refresh);
  el("logout").addEventListener("click", async () => {
    if (busy) return;
    busy = true;
    el("logout").disabled = true;
    try {
      const response = await fetch("/play/logout", {method: "POST", credentials: "same-origin",
        headers: {"X-CSRF-Token": csrf || ""}});
      if (!response.ok && response.status !== 401) throw new Error("Sign-out failed. Please try again.");
      signedOut();
      el("message").textContent = "Signed out.";
    } catch (error) { el("message").textContent = error.message; }
    finally { busy = false; el("logout").disabled = false; }
  });
  refresh();
})();
