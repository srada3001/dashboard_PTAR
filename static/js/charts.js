/* Draws the charts of the reading views with ECharts (docs/REQUISITOS.md §7).

   Everything is decided on the server (apps/dashboards/charts.py); this only draws it:
   - color = the point, marker shape = the source; a hollow marker is a value with "<" or ">";
   - a value that does not exist leaves a gap: the line breaks where a series goes longer than
     usual without data (three times its usual step, and at least a day), or where a day, week
     or month of means is missing;
   - with several parameters (the explorer), each one has its own line dash;
   - dashed lines are the limits, each in its point's color, only while they are in force;
   - the buttons above hide and show parameters, points and sources;
   - charts of the same data-group zoom together;
   - a data-image button downloads what is visible as a PNG, with a title and a legend.
   Times arrive as Bogotá's wall clock in UTC seconds and the chart draws in UTC, so it shows
   Bogotá's hours whatever the browser's time zone. */

(function () {
  "use strict";

  const INK = { text: "#17202a", soft: "#5a6874", faint: "#8b97a3", grid: "#e7ebf0", axis: "#c3cad3" };
  const FONT = '"IBM Plex Sans", system-ui, -apple-system, "Segoe UI", sans-serif';
  const DAY = 86400;
  const MANY = 3000; // past this, a series is drawn without markers
  const WEEKDAYS = ["dom", "lun", "mar", "mié", "jue", "vie", "sáb"];
  const MONTHS = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
    "septiembre", "octubre", "noviembre", "diciembre"];

  const pad = (n) => String(n).padStart(2, "0");

  function number(value, decimals) {
    return value.toFixed(decimals).replace(".", ",");
  }

  function axisNumber(value) {
    return String(Number(value.toPrecision(8))).replace(".", ",");
  }

  function escape(text) {
    return String(text).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
  }

  function dayText(t) {
    const d = new Date(t * 1000);
    return `${d.getUTCFullYear()}-${pad(d.getUTCMonth() + 1)}-${pad(d.getUTCDate())}`;
  }

  /** When a sample was taken, with the precision it is known: hour, a. m./p. m. or the day. */
  function whenText(t, precision) {
    const d = new Date(t * 1000);
    switch (precision) {
      case "h": return `${dayText(t)} ${pad(d.getUTCHours())}:${pad(d.getUTCMinutes())}`;
      case "a": return `${dayText(t)} a. m.`;
      case "p": return `${dayText(t)} p. m.`;
      default: return dayText(t);
    }
  }

  function periodText(t, period) {
    const d = new Date(t * 1000);
    if (period === "week") return `Semana del ${dayText(t)}`;
    if (period === "month") return `${MONTHS[d.getUTCMonth()]} de ${d.getUTCFullYear()}`;
    return dayText(t);
  }

  /** The longest step between two samples that still draws a line. */
  function gapLimit(rows, fixed) {
    if (fixed) return fixed;
    if (rows.length < 2) return Infinity;
    const steps = [];
    for (let i = 1; i < rows.length; i++) steps.push(rows[i][0] - rows[i - 1][0]);
    steps.sort((a, b) => a - b);
    return Math.max(3 * steps[Math.floor(steps.length / 2)], DAY);
  }

  class Chart {
    constructor(figure) {
      this.figure = figure;
      this.data = JSON.parse(document.getElementById(figure.dataset.chart).textContent);
      this.hiddenParameters = new Set();
      this.hiddenPoints = new Set();
      this.hiddenSources = new Set();
      this.drawn = []; // the series on the chart, in ECharts' order (limits come after them)
      this.canvas = figure.querySelector("[data-canvas]");
      this.chart = echarts.init(this.canvas, null, { locale: "ES", renderer: "canvas" });
      if (figure.dataset.group) {
        this.chart.group = figure.dataset.group;
        echarts.connect(figure.dataset.group);
      }
      new ResizeObserver(() => this.chart.resize()).observe(this.canvas);
      this.listen();
      this.draw();
    }

    listen() {
      this.figure.querySelectorAll("[data-parameter]").forEach((button) => {
        button.addEventListener("click", () => this.toggle(button, this.hiddenParameters, Number(button.dataset.parameter)));
      });
      this.figure.querySelectorAll("[data-point]").forEach((button) => {
        button.addEventListener("click", () => this.toggle(button, this.hiddenPoints, Number(button.dataset.point)));
      });
      this.figure.querySelectorAll("[data-source]").forEach((button) => {
        button.addEventListener("click", () => this.toggle(button, this.hiddenSources, Number(button.dataset.source)));
      });
      this.figure.querySelectorAll("[data-image]").forEach((button) => {
        button.addEventListener("click", () => this.download(button));
      });
    }

    toggle(button, hidden, index) {
      if (hidden.has(index)) hidden.delete(index);
      else hidden.add(index);
      button.setAttribute("aria-pressed", String(!hidden.has(index)));
      this.draw();
    }

    visible(series) {
      return !this.hiddenParameters.has(series.parameter) && !this.hiddenPoints.has(series.point) && !this.hiddenSources.has(series.source);
    }

    /** ECharts data items of a series, with null items where the line must break. */
    items(series, color) {
      const { period, gap } = this.data;
      const limit = gapLimit(series.data, gap);
      const items = [];
      let previous = null;
      for (const row of series.data) {
        const [t, value] = row;
        if (previous !== null && t - previous > limit) items.push({ value: [(previous + t) * 500, null] });
        const qualified = period ? row[3] > 0 : row[2] !== "";
        const item = { value: [t * 1000, value], row };
        if (qualified) {
          item.itemStyle = { color: "#ffffff", borderColor: color, borderWidth: 1.5 };
          item.symbolSize = 9;
        }
        items.push(item);
        previous = t;
      }
      return items;
    }

    tooltip(params) {
      const { unit, period } = this.data;
      const { decimals } = this.drawn[params.seriesIndex];
      const row = params.data.row;
      const name = `<span style="color:${params.color}">●</span> ${escape(params.seriesName)}`;
      const units = unit ? ` ${escape(unit)}` : "";
      if (period) {
        const [t, mean, n, qualified] = row;
        const detail = `${n} muestra${n === 1 ? "" : "s"}${qualified ? `, ${qualified} con «&lt;» o «&gt;»` : ""}`;
        return `${name}<br>${periodText(t, period)}: <b>${number(mean, decimals)}</b>${units}<br><span style="color:${INK.soft}">${detail}</span>`;
      }
      const [t, value, qualifier, precision] = row;
      return `${name}<br>${whenText(t, precision)}: <b>${escape(qualifier)}${number(value, decimals)}</b>${units}`;
    }

    draw() {
      this.chart.setOption(this.option(), { replaceMerge: ["series", "dataZoom"] });
    }

    /** The visible series as a PNG, with a title and a legend, to paste in a report. */
    download(button) {
      const box = document.createElement("div");
      box.style.cssText = "position: fixed; left: -10000px; top: 0; width: 1100px; height: 620px;";
      document.body.appendChild(box);
      const chart = echarts.init(box, null, { locale: "ES", renderer: "canvas" });
      const option = this.option();
      const names = this.drawn.map((s) => s.name);
      const limits = [...new Set(this.data.limits.filter((l) => !this.hiddenPoints.has(l.point)).map((l) => l.text))];
      const rows = Math.ceil(names.length / 4);
      let title = button.dataset.imageTitle;
      // A zoomed chart (the explorer) is saved as it is seen, and its title says so.
      const [zoomed] = this.chart.getOption().dataZoom || [];
      if (zoomed && zoomed.startValue != null && (zoomed.start > 0 || zoomed.end < 100)) {
        option.xAxis.min = zoomed.startValue;
        option.xAxis.max = zoomed.endValue;
        title += ` (acercamiento: del ${dayText(zoomed.startValue / 1000)} al ${dayText(zoomed.endValue / 1000 - 1)})`; // the axis ends at 00:00 of the next day
      }
      option.title = {
        text: title,
        subtext: [...limits, this.data.period === "day" ? "Promedios diarios" : ""].filter(Boolean).join(" · "),
        left: 16,
        top: 10,
        textStyle: { fontFamily: FONT, fontSize: 16, fontWeight: 600, color: INK.text },
        subtextStyle: { fontFamily: FONT, fontSize: 12, color: INK.soft },
      };
      option.legend = {
        data: names, left: 16, right: 16, bottom: 10, itemWidth: 24, itemGap: 16,
        textStyle: { fontFamily: FONT, fontSize: 12, color: INK.text },
      };
      option.grid = { ...option.grid, left: 16, right: 24, top: 100, bottom: 24 + rows * 24 };
      option.dataZoom = [];
      chart.setOption(option);
      const link = document.createElement("a");
      link.href = chart.getDataURL({ type: "png", pixelRatio: 2, backgroundColor: "#ffffff" });
      link.download = button.dataset.image;
      link.click();
      chart.dispose();
      box.remove();
    }

    option() {
      const { parameters, points, sources, limits, start, end, unit } = this.data;
      const series = [];
      this.drawn = this.data.series.filter((s) => this.visible(s));
      for (const s of this.drawn) {
        const color = points[s.point].color;
        const dash = parameters[s.parameter].dash;
        const items = this.items(s, color);
        const many = items.length > MANY;
        series.push({
          type: "line",
          name: s.name,
          data: items,
          symbol: sources[s.source].symbol,
          symbolSize: items.length > 400 ? 5 : 7,
          showSymbol: !many,
          sampling: many ? "lttb" : undefined,
          connectNulls: false,
          color,
          lineStyle: { width: 1.5, color, opacity: 0.85, type: dash.length ? dash : "solid" },
          emphasis: { focus: "series", lineStyle: { width: 2 } },
          animation: false,
          z: 2,
        });
      }
      for (const limit of limits) {
        if (this.hiddenPoints.has(limit.point) || this.hiddenParameters.has(limit.parameter)) continue;
        for (const value of limit.values) {
          series.push({
            type: "line",
            name: limit.text,
            data: [[limit.from * 1000, value], [limit.to * 1000, value]],
            symbol: "none",
            silent: true,
            tooltip: { show: false },
            lineStyle: { type: [6, 4], width: 1.5, color: limit.color },
            animation: false,
            z: 1,
          });
        }
      }

      const zoom = "zoom" in this.figure.dataset;
      return {
        useUTC: true,
        animation: false,
        textStyle: { fontFamily: FONT, color: INK.text },
        grid: { left: 8, right: 16, top: 28, bottom: zoom ? 56 : 8, containLabel: true },
        tooltip: {
          trigger: "item",
          confine: true,
          formatter: (params) => this.tooltip(params),
          backgroundColor: "#ffffff",
          borderColor: INK.axis,
          textStyle: { color: INK.text, fontFamily: FONT, fontSize: 13 },
        },
        xAxis: {
          type: "time",
          min: start * 1000,
          max: end * 1000,
          axisLine: { lineStyle: { color: INK.axis } },
          axisTick: { lineStyle: { color: INK.axis } },
          // A week (the ICAV charts): one label per day, with its weekday.
          minInterval: this.data.days ? DAY * 1000 : undefined,
          axisLabel: {
            color: INK.soft,
            hideOverlap: true,
            formatter: this.data.days ? (v) => `${WEEKDAYS[new Date(v).getUTCDay()]} ${new Date(v).getUTCDate()}` : undefined,
          },
          splitLine: { show: false },
          // Only a guide line: if it also triggered the (per item) tooltip, ECharts would call the
          // formatter without an item after each redraw, and the redraw would stop there.
          axisPointer: { show: true, type: "line", triggerTooltip: false, lineStyle: { color: INK.faint }, label: { show: false } },
        },
        yAxis: {
          type: "value",
          scale: true,
          name: unit,
          nameTextStyle: { color: INK.soft, align: "left" },
          axisLine: { show: false },
          axisLabel: { color: INK.soft, formatter: axisNumber },
          splitLine: { lineStyle: { color: INK.grid } },
        },
        dataZoom: zoom ? [{ type: "slider", height: 20, bottom: 8, labelFormatter: (v) => dayText(v / 1000), borderColor: INK.axis }] : [],
        series,
      };
    }
  }

  function start() {
    document.querySelectorAll("figure[data-chart]").forEach((figure) => new Chart(figure));
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start);
  else start();
})();
