"use strict";
const $ = id => document.getElementById(id);
const names = {maker: "Sable", reader: "Efiishent", successor: "Tavi", convenor: "Oriel"};
const labels = {request: "Send briefing invitation", accept: "Accept the briefing", decline: "Decline", offer: "Offer briefing copy", receipt: "Verify and acknowledge", succeed: "Pass receipt responsibility to Tavi"};
const past = {request: "sent the briefing invitation", accept: "accepted the briefing", decline: "declined the briefing", offer: "offered the briefing copy", receipt: "verified and acknowledged the briefing", succeed: "passed receipt responsibility to Tavi"};
let csrf;
let view;
let uid;
let pending;
let busy = false;

async function api(path, body) {
  const headers = body ? {"Content-Type": "application/json", "X-CSRF-Token": csrf} : {};
  const response = await fetch(path, {method: body ? "POST" : "GET", headers, body: body ? JSON.stringify(body) : undefined});
  if (response.status === 401) throw new Error("Choose a test reader to open the briefing.");
  if (!response.ok) throw new Error(await response.text());
  return response.json();
}

function render() {
  $("case").hidden = false;
  $("title").textContent = view.fields.undertaking;
  $("brief").textContent = view.fields.brief;
  $("state").textContent = view.state[0].toUpperCase() + view.state.slice(1);
  $("holder").textContent = "Current reader · " + names[view.holder];
  $("actions").replaceChildren();
  for (const action of view.actions) {
    const button = document.createElement("button");
    button.textContent = labels[action];
    button.addEventListener("click", () => sendPending(action));
    $("actions").append(button);
  }
  $("copy-panel").hidden = !view.copy;
  $("copy-fields").replaceChildren();
  if (view.copy) {
    for (const text of Object.values(JSON.parse(view.copy).fields)) {
      const paragraph = document.createElement("p");
      paragraph.textContent = text;
      $("copy-fields").append(paragraph);
    }
  }
  $("empty").hidden = view.history.length > 0;
  $("history").replaceChildren();
  for (const event of view.history) {
    const item = document.createElement("li");
    item.textContent = names[event.actor] + " " + past[event.action];
    const time = document.createElement("span");
    time.textContent = new Date(event.at * 1000).toLocaleString();
    item.append(time);
    $("history").append(item);
  }
}

async function refresh() {
  try {
    const me = await api("/play/api/me");
    csrf = me.session.csrf;
    uid = me.character.name;
    $("reader").textContent = uid + " · synthetic perspective";
    view = await api("/play/api/undertaking");
    render();
    $("message").textContent = "";
    pending = JSON.parse(sessionStorage.getItem("fs-briefing-pending-" + uid) || "null");
    $("retry").hidden = !pending;
  } catch (error) {
    $("case").hidden = true;
    $("message").textContent = error.message;
  }
}

async function sendPending(action) {
  if (busy) return;
  busy = true;
  $("retry").hidden = true;
  document.querySelectorAll("button").forEach(button => button.disabled = true);
  try {
    if (typeof action === "string") {
      pending = {action, command_id: crypto.randomUUID(), revision: view.revision};
      if (action === "receipt") {
        const hash = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(view.copy));
        pending.checksum = Array.from(new Uint8Array(hash), n => n.toString(16).padStart(2, "0")).join("");
      }
      sessionStorage.setItem("fs-briefing-pending-" + uid, JSON.stringify(pending));
    }
    await api("/play/api/undertaking/action", pending);
    sessionStorage.removeItem("fs-briefing-pending-" + uid);
    pending = null;
    await refresh();
    $("message").textContent = "Your response is recorded.";
  } catch (error) {
    $("message").textContent = error.message + " Refresh to check what happened, or retry the same submission.";
    $("retry").hidden = false;
  } finally {
    busy = false;
    document.querySelectorAll("button").forEach(button => button.disabled = false);
  }
}


$("refresh").addEventListener("click", refresh);
$("retry").addEventListener("click", () => sendPending());
refresh();
