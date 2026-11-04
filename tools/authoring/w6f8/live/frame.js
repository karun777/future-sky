"use strict";
(() => {
  const byId = id => document.getElementById(id);
  const dialogs = [...document.querySelectorAll("dialog")];
  function closeAll() { dialogs.forEach(d => { if (d.open) d.close(); }); }
  document.querySelectorAll("[data-open]").forEach(button => {
    button.addEventListener("click", () => {
      if (byId("game").hidden) return;
      closeAll();
      byId(button.dataset.open).showModal();
    });
  });
  document.querySelectorAll("[data-close]").forEach(button =>
    button.addEventListener("click", closeAll));
  byId("movement").addEventListener("click", () => {
    const available = byId("exits").querySelector("button:not(:disabled)");
    if (available) available.focus();
    else byId("refresh").focus();
  });
  byId("read-closely").addEventListener("click", () => {
    if (byId("game").hidden) return;
    byId("passage-title").textContent = byId("room-title").textContent;
    byId("passage-copy").replaceChildren(...[...byId("room-description").children].map(n => n.cloneNode(true)));
    closeAll(); byId("passage").showModal();
  });
  // Clear snapshots and close private panels whenever the transport signs out.
  new MutationObserver(() => {
    if (!byId("game").hidden) return;
    closeAll();
    byId("passage-title").textContent = "";
    byId("passage-copy").replaceChildren();
  }).observe(byId("game"), {attributes: true, attributeFilter: ["hidden"]});
  byId("fullscreen").addEventListener("click", async () => {
    try {
      if (document.fullscreenElement) await document.exitFullscreen();
      else await document.documentElement.requestFullscreen();
    } catch {
      byId("fullscreen").textContent = "Use browser fullscreen";
    }
  });
  document.addEventListener("fullscreenchange", () => {
    byId("fullscreen").textContent = document.fullscreenElement ? "Exit fullscreen" : "Fullscreen";
  });
})();
