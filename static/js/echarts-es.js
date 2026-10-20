/* Spanish months and days for ECharts' time axes, as in the U044 dashboard.
   charts.js starts its charts with { locale: "ES" }. */

echarts.registerLocale("ES", {
  time: {
    month: ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
      "agosto", "septiembre", "octubre", "noviembre", "diciembre"],
    monthAbbr: ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sept", "oct", "nov", "dic"],
    dayOfWeek: ["domingo", "lunes", "martes", "miércoles", "jueves", "viernes", "sábado"],
    dayOfWeekAbbr: ["dom", "lun", "mar", "mié", "jue", "vie", "sáb"],
  },
});
