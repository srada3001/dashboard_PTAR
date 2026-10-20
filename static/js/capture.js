/* The capture grid (docs/REQUISITOS.md §6): every cell saves itself when it is left.

   The server decides (apps/capture/views.py); here only:
   - the keyboard, as in Excel: Enter goes down, Shift + Enter up, Tab right, Escape undoes;
   - a quick check while typing (a number, optionally with "<" or ">"), so a typo shows at once;
   - the questions the server asks before saving (outside the usual range, correcting or deleting
     a value), with an optional reason, one at a time;
   - the bar below, with the focused cell's variable, ranges, who registered it, and its history. */

(function () {
  "use strict";

  const table = document.querySelector("table.rejilla");
  if (!table) return;

  const NUMBER = /^\s*[<>]?\s*-?(\d+([.,]\d+)?|[.,]\d+)\s*$/;
  const variables = JSON.parse(document.getElementById("variables").textContent);
  const csrf = JSON.parse(document.body.getAttribute("hx-headers"))["X-CSRFToken"];
  const status = {
    cell: document.querySelector("[data-status-cell]"),
    detail: document.querySelector("[data-status-detail]"),
    history: document.querySelector("[data-history]"),
    panel: document.querySelector("[data-history-panel]"),
  };
  const prompt = {
    box: document.querySelector("[data-prompt]"),
    text: document.querySelector("[data-prompt-text]"),
    reasonField: document.querySelector("[data-prompt-reason]"),
    reason: document.querySelector("[data-prompt-reason] input"),
    yes: document.querySelector("[data-prompt-yes]"),
    no: document.querySelector("[data-prompt-no]"),
  };
  const questions = []; // waiting to be asked, one at a time
  let asking = null;
  let focused = null;

  const cellOf = (input) => input.closest("td");

  function setState(input, state, message) {
    const cell = cellOf(input);
    cell.classList.remove("celda--guardando", "celda--guardada", "celda--error", "celda--aviso");
    if (state) cell.classList.add(`celda--${state}`);
    input.dataset.message = message || "";
    if (state === "guardada") setTimeout(() => cell.classList.remove("celda--guardada"), 1500);
    if (input === focused) describe(input);
  }

  function describe(input) {
    const variable = variables[input.dataset.variable];
    const unit = variable.unit ? ` (${variable.unit})` : "";
    status.cell.textContent = `${variable.label}${unit} · ${table.dataset.dayLabel} ${input.dataset.slotLabel}`;
    const parts = [];
    if (input.dataset.message) parts.push(input.dataset.message);
    if (variable.typical) parts.push(`Habitual: ${variable.typical}.`);
    if (variable.physical) parts.push(`Posible: ${variable.physical}.`);
    if (input.title) parts.push(input.title);
    status.detail.textContent = parts.join(" ");
    status.history.hidden = !input.dataset.version && !input.dataset.saved;
  }

  function apply(input, answer) {
    input.value = answer.value;
    input.dataset.saved = answer.value;
    input.dataset.version = answer.version;
    input.title = answer.note;
    if (!("future" in input.dataset)) input.readOnly = answer.readonly;
    cellOf(input).classList.toggle("celda--dudosa", answer.suspect);
    cellOf(input).classList.toggle("celda--bloqueada", input.readOnly);
  }

  async function save(input, extra) {
    const value = input.value.trim();
    if (input.readOnly || (value === input.dataset.saved && !extra)) {
      setState(input, null);
      return;
    }
    const body = new FormData();
    body.append("variable", input.dataset.variable);
    body.append("slot", input.dataset.slot);
    body.append("date", table.dataset.date);
    body.append("value", value);
    body.append("original", input.dataset.version);
    for (const [key, item] of Object.entries(extra || {})) body.append(key, item);
    setState(input, "guardando");
    let answer;
    try {
      const response = await fetch(table.dataset.saveUrl, {
        method: "POST", body, credentials: "same-origin", headers: { "X-CSRFToken": csrf },
      });
      if (!response.ok || !(response.headers.get("Content-Type") || "").includes("json")) {
        throw new Error(response.redirected ? "session" : String(response.status));
      }
      answer = await response.json();
    } catch (error) {
      const message = error.message === "session"
        ? "Tu sesión terminó: recarga la página y vuelve a entrar. No se guardó."
        : "No se pudo guardar: revisa la conexión y vuelve a intentarlo.";
      setState(input, "error", message);
      return;
    }
    switch (answer.state) {
      case "saved":
      case "deleted":
        apply(input, answer);
        setState(input, "guardada");
        break;
      case "unchanged":
        apply(input, answer);
        setState(input, null);
        break;
      case "conflict":
        apply(input, answer);
        setState(input, "aviso", answer.message);
        break;
      case "confirm":
        ask(input, answer.message, answer.reason);
        break;
      default: // invalid or refused: the typed value stays, to be fixed
        setState(input, "error", answer.message);
    }
  }

  // ---------------------------------------------------------------- questions before saving

  function ask(input, message, withReason) {
    setState(input, "aviso", message);
    questions.push({ input, message, withReason });
    if (!asking) next();
  }

  function next() {
    asking = questions.shift() || null;
    if (!asking) {
      prompt.box.hidden = true;
      return;
    }
    asking.returnTo = document.activeElement;
    prompt.text.textContent = asking.message;
    prompt.reasonField.hidden = !asking.withReason;
    prompt.reason.value = "";
    prompt.box.hidden = false;
    const rect = cellOf(asking.input).getBoundingClientRect();
    const width = prompt.box.offsetWidth;
    prompt.box.style.left = `${Math.max(8, Math.min(rect.left, window.innerWidth - width - 8))}px`;
    const below = rect.bottom + 6;
    prompt.box.style.top = `${below + prompt.box.offsetHeight > window.innerHeight ? rect.top - prompt.box.offsetHeight - 6 : below}px`;
    (asking.withReason ? prompt.reason : prompt.yes).focus();
  }

  function answer(yes) {
    const { input, returnTo } = asking;
    if (yes) {
      save(input, { confirm: "1", reason: prompt.reason.value.trim() });
    } else {
      input.value = input.dataset.saved;
      setState(input, null);
    }
    prompt.box.hidden = true;
    if (returnTo && returnTo !== prompt.yes && returnTo !== prompt.reason && document.contains(returnTo)) returnTo.focus();
    else input.focus();
    next();
  }

  prompt.yes.addEventListener("click", () => answer(true));
  prompt.no.addEventListener("click", () => answer(false));
  prompt.box.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      event.preventDefault();
      answer(false);
    } else if (event.key === "Enter" && event.target === prompt.reason) {
      event.preventDefault();
      answer(true);
    }
  });

  // ---------------------------------------------------------------- keyboard and focus

  /** The input `step` rows above or below, in the same column, skipping cells without one. */
  function vertical(input, step) {
    const cell = cellOf(input);
    const column = [...cell.parentElement.children].indexOf(cell) - cell.parentElement.children.length;
    let row = cell.parentElement;
    while ((row = step > 0 ? row.nextElementSibling : row.previousElementSibling)) {
      // Rows of the variables layout may lack the point's header: count cells from the right.
      const target = row.children[row.children.length + column];
      const field = target && target.querySelector("input");
      if (field) return field;
    }
    return null;
  }

  table.addEventListener("keydown", (event) => {
    const input = event.target;
    if (!input.matches("input.celda__valor")) return;
    if (event.key === "Enter" || event.key === "ArrowDown" || event.key === "ArrowUp") {
      event.preventDefault();
      const target = vertical(input, event.key === "ArrowUp" || (event.key === "Enter" && event.shiftKey) ? -1 : 1);
      if (target) target.focus();
      else if (event.key === "Enter") input.blur();
    } else if (event.key === "Escape") {
      input.value = input.dataset.saved;
      setState(input, null);
    }
  });

  table.addEventListener("input", (event) => {
    const input = event.target;
    const value = input.value.trim();
    const wrong = value !== "" && !NUMBER.test(value);
    cellOf(input).classList.toggle("celda--error", wrong);
    input.dataset.message = wrong ? "Solo números, con coma o punto decimal, opcionalmente con «<» o «>» delante." : "";
    describe(input);
  });

  table.addEventListener("change", (event) => {
    if (event.target.matches("input.celda__valor")) save(event.target);
  });

  table.addEventListener("focusin", (event) => {
    if (!event.target.matches("input.celda__valor")) return;
    focused = event.target;
    event.target.select();
    describe(event.target);
  });

  status.history.addEventListener("click", async () => {
    if (!focused) return;
    const params = new URLSearchParams({ variable: focused.dataset.variable, slot: focused.dataset.slot, date: table.dataset.date });
    const response = await fetch(`${table.dataset.historyUrl}?${params}`, { credentials: "same-origin" });
    status.panel.innerHTML = response.ok ? await response.text() : "<p class=\"error\">No se pudo leer el historial.</p>";
    status.panel.hidden = false;
    status.panel.scrollIntoView({ behavior: "smooth", block: "nearest" });
  });

  // Start where there is something to type: today, in the hours layout, the current hour (the
  // latest that can be filled); otherwise the first row. Within it, the first empty cell.
  const editable = (row) => [...row.querySelectorAll("input.celda__valor")].filter((input) => !input.readOnly);
  const rows = [...table.tBodies[0].rows].filter((row) => editable(row).length);
  const start = table.classList.contains("rejilla--horas") && "today" in table.dataset ? rows.at(-1) : rows[0];
  if (start) {
    const inputs = editable(start);
    focused = inputs.find((input) => !input.value) || inputs[0];
    focused.focus();
    describe(focused);
  }
})();
