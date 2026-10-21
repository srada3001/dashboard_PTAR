/* The explorer's parameter lists (docs/REQUISITOS.md §7.2): «Añadir parámetro» adds a list with the
   same menu and × removes one. Removing tells HTMX, so the points and sources follow; a new list
   does it when a parameter is chosen in it. */

(function () {
  "use strict";

  function start() {
    const box = document.querySelector("[data-parameters]");
    if (!box) return;
    const template = box.querySelector("template[data-parameter-row]");

    box.querySelector("[data-add-parameter]").addEventListener("click", () => {
      const row = template.content.firstElementChild.cloneNode(true);
      template.before(row);
      row.querySelector("select").focus();
    });

    box.addEventListener("click", (event) => {
      const button = event.target.closest("[data-remove-parameter]");
      if (!button) return;
      const row = button.closest(".parametro");
      const chosen = row.querySelector("select").value !== "";
      row.remove();
      const first = box.querySelector("select"); // the label points to the first list
      first.id = "id_parameters";
      first.removeAttribute("aria-label");
      if (chosen) htmx.trigger(box, "change");
    });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start);
  else start();
})();
