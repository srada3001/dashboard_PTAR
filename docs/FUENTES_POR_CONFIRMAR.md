# Fuentes «Por confirmar»

En **Captura**, la etiqueta de cada tarjeta es la **fuente** del formato: quien midió los datos, no quien los digita. **«Por confirmar» no es un estado del formulario**, es una fuente provisional. Se usa para los datos del histórico cuya fuente nadie ha confirmado todavía. Puede ser el laboratorio central, un aliado, operación o PI.

Es la decisión abierta n.º 7 de [REQUISITOS.md §15](REQUISITOS.md). Cuando se sepa la fuente, se cambia en el admin la fuente de esas variables, sin reimportar. El detalle columna por columna está en [ORIGEN_DE_DATOS.md](ORIGEN_DE_DATOS.md).

## Datos con fuente «Por confirmar»

Desde el 2026-11-09 ningún formato de captura tiene la fuente «Por confirmar»: DIAPAC, Ecodiesel, separadores y agua agria, y sodas gastadas son de BIOTA. Solo quedan con ella datos del histórico de la hoja «Datos LABORATORIO» del libro «SEGUIMIENTO UT DESCONTAMINACIÓN NUEVO» (tabla 2, mapeo `import_maps/Laboratorio.csv`).

La hoja «Datos LABORATORIO» mezcla dos cosas. Sus análisis se asignaron a Labviewer. Los flujos y niveles no son análisis de laboratorio: lo más probable es que vengan de PI o de operación. Son estas 10 columnas:

- flujo de los clarificadores A, B, C y D (BA-4005A a BA-4005D; su captura por hora está en «Flujos de carga», de PI);
- flujo de entrega de recirculación;
- flujo de entrada y de salida de T-2590;
- flujo de entrada y de salida de T-4841;
- nivel de la piscina pulmón.

## Formatos con fuente confirmada

| Formato | Fuente | Libro | Hoja de Excel |
|---|---|---|---|
| Ecolab | Ecolab (antes Nalco) | Tabla aliado química (tabla 1) | «Entrada de Datos» |
| Flujos de carga | PI | Tabla aliado química (tabla 1) | «Entrada de Datos» (flujos de BA-4005C/D) y, desde el 2026-11-09, los de BA-4005A/B y la recirculación |
| BIOTA (secciones «Fase I», «DIAPAC», «Ecodiesel», «Aguas agrias a los separadores» y «Sodas gastadas») | BIOTA | SEGUIMIENTO UT DESCONTAMINACIÓN NUEVO (tabla 2) | «FASE I», «BR 4081», «DIAPAC», «ECODIESEL», «A.AGRIAS SEP.» y «K-SODAS» (todo menos Fase I, confirmado el 2026-11-09) |
| Laboratorio central | Labviewer | SEGUIMIENTO UT DESCONTAMINACIÓN NUEVO (tabla 2) | «Datos LABORATORIO», todo menos los 10 flujos y niveles |
