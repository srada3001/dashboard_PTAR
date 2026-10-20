/* Behaviour shared by every page. */

(function () {
  "use strict";

  // Filters that apply as soon as they change; their button stays for browsers without JavaScript.
  function start() {
    document.querySelectorAll("form[data-autosubmit]").forEach((form) => {
      form.addEventListener("change", () => form.requestSubmit());
    });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start);
  else start();
})();
