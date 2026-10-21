/* The explorer's parameter blocks (docs/REQUISITOS.md §7.2): «Añadir parámetro» adds an empty block
   below the others, which keep what they have; «Quitar» removes one. Each block's fields carry its
   own prefix (p1-, p2-…), so a new block takes the next free number. */

(function () {
  "use strict";

  function start() {
    const blocks = document.querySelector("[data-blocks]");
    if (!blocks) return;
    const template = document.querySelector("template[data-block-template]");

    function nextNumber() {
      const numbers = [...blocks.querySelectorAll("select[name$='-parameter']")].map((s) => Number(s.name.slice(1, -"-parameter".length)));
      return Math.max(0, ...numbers) + 1;
    }

    document.querySelector("[data-add-block]").addEventListener("click", () => {
      const html = template.innerHTML.replaceAll("p__n__", `p${nextNumber()}`);
      blocks.insertAdjacentHTML("beforeend", html);
      const block = blocks.lastElementChild;
      htmx.process(block);
      block.querySelector("select").focus();
    });

    blocks.addEventListener("click", (event) => {
      const button = event.target.closest("[data-remove-block]");
      if (button) button.closest("[data-block]").remove();
    });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start);
  else start();
})();
