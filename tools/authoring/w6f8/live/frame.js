"use strict";
(() => {
  const byId = id => document.getElementById(id);
  const dialogs = [...document.querySelectorAll("dialog")];
  function closeAll() { dialogs.forEach(d => { if (d.open) d.close(); }); }
  document.addEventListener("keydown", event => { if (event.key === "Escape") closeAll(); });
  document.querySelectorAll("[data-open]").forEach(button => {
    button.addEventListener("click", () => {
      if (byId("game").hidden) return;
      closeAll();
      byId(button.dataset.open).show();
    });
  });
  document.querySelectorAll("[data-close]").forEach(button =>
    button.addEventListener("click", closeAll));
  // Clear snapshots and close private panels whenever the transport signs out.
  new MutationObserver(() => {
    if (!byId("game").hidden) return;
    closeAll();
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
