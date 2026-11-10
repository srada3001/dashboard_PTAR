# Origen de los datos de la base

Generado el 2026-10-20 a partir de la base de datos y de los mapeos de `import_maps/`. No contiene valores de la planta: solo describe de dónde sale cada variable.

**Cómo leerlo.** Una *variable* es un punto + un parámetro + una fuente (por ejemplo «BA-4010 · Fenoles · BIOTA»). Cada variable sale de una o más columnas de una tabla de Excel; la tabla vive dentro de una hoja de un libro. La fuente «Por confirmar» significa que todavía no se ha definido quién midió esas variables (queda como decisión abierta del proyecto).

## 1. Libros, hojas y tablas

| Libro de Excel | Hoja | Tabla de Excel | Mapeo | Variables | Mediciones |
|---|---|---|---|---|---|
| `Tabla aliado química con Graficas.xlsx` | «Entrada de Datos» | `Tabla1` | `import_maps/Tabla1.csv` | 45 | 441.520 |
| `SEGUIMIENTO UT DESCONTAMINACIÓN NUEVO.xlsx` | «BR 4081» | `BR_4081` | `import_maps/BR_4081.csv` | 5 | 10.765 |
| `SEGUIMIENTO UT DESCONTAMINACIÓN NUEVO.xlsx` | «DIAPAC» | `DIAPAC` | `import_maps/DIAPAC.csv` | 13 | 1.098 |
| `SEGUIMIENTO UT DESCONTAMINACIÓN NUEVO.xlsx` | «ECODIESEL» | `Ecodisel` | `import_maps/Ecodisel.csv` | 6 | 661 |
| `SEGUIMIENTO UT DESCONTAMINACIÓN NUEVO.xlsx` | «FASE I» | `FASE1` | `import_maps/FASE1.csv` | 73 | 109.351 |
| `SEGUIMIENTO UT DESCONTAMINACIÓN NUEVO.xlsx` | «A.AGRIAS SEP.» | `FenolAASepSoda4` | `import_maps/FenolAASepSoda4.csv` | 24 | 52.662 |
| `SEGUIMIENTO UT DESCONTAMINACIÓN NUEVO.xlsx` | «K-SODAS» | `FenolAASepSoda48` | `import_maps/FenolAASepSoda48.csv` | 18 | 2.449 |
| `SEGUIMIENTO UT DESCONTAMINACIÓN NUEVO.xlsx` | «Datos LABORATORIO» | `Laboratorio` | `import_maps/Laboratorio.csv` | 155 | 22.991 |

Las cargas se hicieron con `import_history` (lotes en Administración → Lotes de importación). Primera carga: 19/10/2026, con copias locales `tabla_referencia_1.xlsx` (Ecolab, antes Nalco) y `tabla_referencia_2.xlsx` (SEGUIMIENTO UT); actualizaciones del 20/10/2026 con los libros de este cuadro (Nalco hasta el 20/10, SEGUIMIENTO UT hasta el 13/10).

## 2. Parámetros del catálogo

| Código | Nombre | Unidad | Decimales | Rango físico mín. | Rango físico máx. | Variables |
|---|---|---|---|---|---|---|
| Cd | Cadmio | mg/L | 3 | 0,0 | — | 2 |
| Cloruros | Cloruros | mg/L | 2 | 0,0 | — | 2 |
| Conductividad | Conductividad a 25 °C | µS/cm | 1 | 0,0 | — | 2 |
| Cr | Cromo | mg/L | 3 | 0,0 | — | 2 |
| Cu | Cobre | mg/L | 3 | 0,0 | — | 2 |
| DBO | Demanda bioquímica de oxígeno (nombre de Labviewer) | mg/L | 1 | 0,0 | — | 2 |
| DBO5 | Demanda bioquímica de oxígeno a 5 días | mg/L | 1 | 0,0 | — | 0 |
| DQO | Demanda química de oxígeno | mg/L | 1 | 0,0 | — | 26 |
| DQO soluble | Demanda química de oxígeno soluble | mg/L | 1 | 0,0 | — | 1 |
| F/M | Relación alimento/microorganismos | — | 3 | 0,0 | — | 0 |
| Fenoles | Fenoles | mg/L | 2 | 0,0 | — | 24 |
| Flujo | Flujo | gpm | 0 | 0,0 | — | 12 |
| G&A | Grasas y aceites | mg/L | 2 | 0,0 | — | 26 |
| H2S | Sulfuro de hidrógeno | mg/L | 2 | 0,0 | — | 7 |
| Hierro | Hierro | mg/L | 3 | 0,0 | — | 8 |
| IVL | Índice volumétrico de lodos | mL/g | 1 | 0,0 | — | 0 |
| N total | Nitrógeno total | mg/L | 2 | 0,0 | — | 9 |
| N-NH3 | Nitrógeno amoniacal | mg/L | 2 | 0,0 | — | 5 |
| NH3 | Amoníaco (nombre de Labviewer) | mg/L | 2 | 0,0 | — | 4 |
| Ni | Níquel | mg/L | 3 | 0,0 | — | 2 |
| Nivel | Nivel | — | 1 | 0,0 | — | 1 |
| OD | Oxígeno disuelto | mg/L | 2 | 0,0 | — | 5 |
| P total | Fósforo total | mg/L | 2 | 0,0 | — | 3 |
| Pb | Plomo | mg/L | 3 | 0,0 | — | 2 |
| RSH | Mercaptanos | mg/L | 2 | 0,0 | — | 7 |
| Recuento | Recuento microbiológico | ufc/mL | 0 | 0,0 | — | 5 |
| S en aguas | Azufre en aguas (nombre de Labviewer) | mg/L | 2 | 0,0 | — | 2 |
| SS | Sólidos suspendidos (nombre de Labviewer) | mg/L | 1 | 0,0 | — | 10 |
| SSED | Sólidos sedimentables | mL/L | 1 | 0,0 | — | 5 |
| SST | Sólidos suspendidos totales | mg/L | 1 | 0,0 | — | 26 |
| ST | Sólidos totales | mg/L | 1 | 0,0 | — | 3 |
| Se | Selenio | mg/L | 3 | 0,0 | — | 2 |
| Sulfatos | Sulfatos | mg/L | 1 | 0,0 | — | 16 |
| Sulfuros | Sulfuros | mg/L | 2 | 0,0 | — | 3 |
| TRH | Tiempo de retención hidráulica | h | 1 | 0,0 | — | 1 |
| Temperatura | Temperatura | °C | 1 | 0,0 | 100,0 | 18 |
| Turbidez | Turbidez | NTU | 1 | 0,0 | — | 2 |
| V | Vanadio | mg/L | 3 | 0,0 | — | 2 |
| Zn | Zinc | mg/L | 3 | 0,0 | — | 2 |
| pH | pH | — | 2 | 0,0 | 14,0 | 34 |

## 3. Variables por tabla de Excel

Por cada tabla: la columna (encabezado exacto del Excel) → la variable a la que alimenta. Las columnas de una misma variable (7 a. m. y 4 p. m., por ejemplo) se agrupan. «Mediciones» es el total de la variable en la base, sin importar la tabla de origen; «dudosas» son las que están fuera del rango físico.

### Tabla1 — hoja «Entrada de Datos» de `Tabla aliado química con Graficas.xlsx`

| Punto | Parámetro | Fuente | Frecuencia | Encabezados del Excel | Hora que se asigna | Mediciones | Dudosas | Desde | Hasta |
|---|---|---|---|---|---|---|---|---|---|
| BA-4001 | SST | Ecolab | Cada hora | `SST BA4001` | la hora escrita en la fila | 14.023 | 1 | 2022-06-03 | 2026-10-20 |
| BA-4001 | Temperatura | Ecolab | Cada hora | `T° BA4001` | la hora escrita en la fila | 14.020 | 2 | 2022-06-03 | 2026-10-20 |
| BA-4001 | pH | Ecolab | Cada hora | `pH BA4001` | la hora escrita en la fila | 14.018 | 12 | 2022-06-03 | 2026-10-20 |
| BA-4005C | Flujo | PI | Cada hora | `Flujo \nBA4005C` | la hora escrita en la fila | 38.221 | 0 | 2022-06-03 | 2026-10-20 |
| BA-4005C | G&A | Ecolab | Cada hora | `G&A BA4005C` | la hora escrita en la fila | 4.668 | 0 | 2022-06-03 | 2026-10-20 |
| BA-4005C | Hierro | Ecolab | Cada hora | `Fe BA4005C` | la hora escrita en la fila | 4.092 | 0 | 2022-06-03 | 2026-05-16 |
| BA-4005C | SST | Ecolab | Cada hora | `SST BA4005C` | la hora escrita en la fila | 14.028 | 0 | 2022-06-03 | 2026-10-20 |
| BA-4005C | Temperatura | Ecolab | Cada hora | `T° \nBA4005C` | la hora escrita en la fila | 14.027 | 7 | 2022-06-03 | 2026-10-20 |
| BA-4005C | Turbidez | Ecolab | Cada hora | `NTU BA4005C` | la hora escrita en la fila | 13.959 | 0 | 2022-06-03 | 2026-10-20 |
| BA-4005C | pH | Ecolab | Cada hora | `pH BA4005C` | la hora escrita en la fila | 14.021 | 16 | 2022-06-03 | 2026-10-20 |
| BA-4005D | Flujo | PI | Cada hora | `Flujo BA4005D` | la hora escrita en la fila | 38.244 | 0 | 2022-06-03 | 2026-10-20 |
| BA-4005D | G&A | Ecolab | Cada hora | `G&A BA4005D` | la hora escrita en la fila | 4.669 | 0 | 2022-06-03 | 2026-10-20 |
| BA-4005D | Hierro | Ecolab | Cada hora | `Fe BA4005D` | la hora escrita en la fila | 4.085 | 0 | 2022-06-03 | 2026-05-16 |
| BA-4005D | SST | Ecolab | Cada hora | `SST BA4005D` | la hora escrita en la fila | 14.026 | 0 | 2022-06-03 | 2026-10-20 |
| BA-4005D | Temperatura | Ecolab | Cada hora | `T° BA4005D` | la hora escrita en la fila | 14.021 | 15 | 2022-06-03 | 2026-10-20 |
| BA-4005D | Turbidez | Ecolab | Cada hora | `NTU BA4005D` | la hora escrita en la fila | 13.929 | 0 | 2022-06-03 | 2026-10-20 |
| BA-4005D | pH | Ecolab | Cada hora | `pH BA4005D` | la hora escrita en la fila | 14.019 | 51 | 2022-06-03 | 2026-10-20 |
| BA-4030A | G&A | Ecolab | Cada hora | `G&A BA4030A` | la hora escrita en la fila | 4.367 | 0 | 2022-06-03 | 2026-10-20 |
| BA-4030A | SST | Ecolab | Cada hora | `SST BA4030A` | la hora escrita en la fila | 8.532 | 0 | 2022-06-03 | 2026-10-20 |
| BA-4030A | Temperatura | Ecolab | Cada hora | `T° BA4030A` | la hora escrita en la fila | 9.103 | 1 | 2022-06-04 | 2026-10-20 |
| BA-4030A | pH | Ecolab | Cada hora | `pH BA4030A` | la hora escrita en la fila | 8.533 | 9 | 2022-06-03 | 2026-10-20 |
| BA-4030B | G&A | Ecolab | Cada hora | `G&A BA4030B` | la hora escrita en la fila | 3.412 | 0 | 2022-06-03 | 2025-12-05 |
| BA-4030B | SST | Ecolab | Cada hora | `SST BA4030B` | la hora escrita en la fila | 6.640 | 0 | 2022-06-03 | 2025-12-05 |
| BA-4030B | Temperatura | Ecolab | Cada hora | `T° BA4030B` | la hora escrita en la fila | 6.006 | 2 | 2022-06-03 | 2025-12-05 |
| BA-4030B | pH | Ecolab | Cada hora | `pH BA4030B` | la hora escrita en la fila | 6.643 | 17 | 2022-06-03 | 2025-12-05 |
| BA-4030C | G&A | Ecolab | Cada hora | `G&A BA4030C` | la hora escrita en la fila | 3.973 | 0 | 2022-06-03 | 2026-10-20 |
| BA-4030C | SST | Ecolab | Cada hora | `SST BA4030C` | la hora escrita en la fila | 7.758 | 0 | 2022-06-03 | 2026-10-20 |
| BA-4030C | Temperatura | Ecolab | Cada hora | `T° BA4030C` | la hora escrita en la fila | 6.838 | 2 | 2022-06-03 | 2026-10-20 |
| BA-4030C | pH | Ecolab | Cada hora | `pH BA4030C` | la hora escrita en la fila | 7.765 | 10 | 2022-06-03 | 2026-10-20 |
| BA-4030D | G&A | Ecolab | Cada hora | `G&A BA4030D` | la hora escrita en la fila | 2.502 | 0 | 2024-01-13 | 2026-10-20 |
| BA-4030D | SST | Ecolab | Cada hora | `SST BA4030D` | la hora escrita en la fila | 4.905 | 0 | 2024-01-13 | 2026-10-20 |
| BA-4030D | Temperatura | Ecolab | Cada hora | `T° BA4030D` | la hora escrita en la fila | 3.910 | 3 | 2024-01-13 | 2026-10-20 |
| BA-4030D | pH | Ecolab | Cada hora | `pH BA4030D` | la hora escrita en la fila | 4.912 | 7 | 2024-01-13 | 2026-10-20 |
| CL-4080 entrada | G&A | Ecolab | Cada hora | `G&A \nIN CL4080` | la hora escrita en la fila | 4.763 | 0 | 2022-06-03 | 2026-10-20 |
| CL-4080 entrada | SST | Ecolab | Cada hora | `SST\nIN CL4080` | la hora escrita en la fila | 9.269 | 0 | 2022-06-03 | 2026-10-20 |
| CL-4080 entrada | Temperatura | Ecolab | Cada hora | `T°\nIN CL4080` | la hora escrita en la fila | 9.250 | 2 | 2022-06-03 | 2026-10-20 |
| CL-4080 entrada | pH | Ecolab | Cada hora | `pH \nIN CL4080` | la hora escrita en la fila | 9.280 | 10 | 2022-06-03 | 2026-10-20 |
| CL-4080 salida | G&A | Ecolab | Cada hora | `G&AOUTCL4080` | la hora escrita en la fila | 4.770 | 0 | 2022-06-03 | 2026-10-20 |
| CL-4080 salida | SST | Ecolab | Cada hora | `SSTOUTCL4080` | la hora escrita en la fila | 9.272 | 0 | 2022-06-03 | 2026-10-20 |
| CL-4080 salida | Temperatura | Ecolab | Cada hora | `TOUTCL4080` | la hora escrita en la fila | 9.247 | 2 | 2022-06-03 | 2026-10-20 |
| CL-4080 salida | pH | Ecolab | Cada hora | `pHOUTCL4080` | la hora escrita en la fila | 9.267 | 12 | 2022-06-03 | 2026-10-20 |
| DNF entrada | G&A | Ecolab | Cada hora | `G&A \nIN DNF` | la hora escrita en la fila | 4.734 | 0 | 2022-06-04 | 2026-10-20 |
| DNF entrada | SST | Ecolab | Cada hora | `SST\nIN DNF` | la hora escrita en la fila | 9.268 | 0 | 2022-06-04 | 2026-10-20 |
| DNF entrada | Temperatura | Ecolab | Cada hora | `T°\nIN DNF` | la hora escrita en la fila | 9.265 | 1 | 2022-06-04 | 2026-10-20 |
| DNF entrada | pH | Ecolab | Cada hora | `pH \nIN DNF` | la hora escrita en la fila | 9.266 | 11 | 2022-06-04 | 2026-10-20 |

Columna de fecha: `Fecha`.

Columnas que **no** se importan:

- `TOUTCL4081`: Columna sin valores numéricos.
- `TOUTCL4082`: Columna sin valores numéricos.
- `TOUTCL4083`: Columna sin valores numéricos.

### BR_4081 — hoja «BR 4081» de `SEGUIMIENTO UT DESCONTAMINACIÓN NUEVO.xlsx`

| Punto | Parámetro | Fuente | Frecuencia | Encabezados del Excel | Hora que se asigna | Mediciones | Dudosas | Desde | Hasta |
|---|---|---|---|---|---|---|---|---|---|
| BR-4081 | Fenoles | BIOTA | 7 a. m. y 4 p. m. | `BR4081 Fenol am`; `BR4081 Fenol pm` | 7:00 a. m. (fija), 4:00 p. m. (fija) | 2.693 | 0 | 2022-07-01 | 2026-10-13 |
| BR-4081 | Recuento | BIOTA | Diaria | `BR4081 Recuento` | 7:00 a. m. (fija; antes solo el día) | 1.246 | 0 | 2022-07-01 | 2026-10-11 |
| BR-4081 | SSED | BIOTA | 7 a. m. y 4 p. m. | `BR4081 S.SED am` | 7:00 a. m. (fija) | 1.453 | 0 | 2022-07-07 | 2026-10-13 |
| BR-4081 | SST | BIOTA | 7 a. m. y 4 p. m. | `BR4081 SST am`; `BR4081 SST pm` | 7:00 a. m. (fija), 4:00 p. m. (fija) | 2.687 | 0 | 2022-07-01 | 2026-10-13 |
| BR-4081 | pH | BIOTA | 7 a. m. y 4 p. m. | `BR4081 pH am`; `BR4081 pH pm` | 7:00 a. m. (fija), 4:00 p. m. (fija) | 2.686 | 0 | 2022-07-01 | 2026-10-13 |

Columna de fecha: `Fecha`.

### DIAPAC — hoja «DIAPAC» de `SEGUIMIENTO UT DESCONTAMINACIÓN NUEVO.xlsx`

| Punto | Parámetro | Fuente | Frecuencia | Encabezados del Excel | Hora que se asigna | Mediciones | Dudosas | Desde | Hasta |
|---|---|---|---|---|---|---|---|---|---|
| DIAPAC afluente | DQO | BIOTA | Eventual | `DQO` | 7:00 a. m. (fija; antes solo el día) | 82 | 0 | 2025-01-05 | 2026-10-12 |
| DIAPAC afluente | N total | BIOTA | Eventual | `N-T` | 7:00 a. m. (fija; antes solo el día) | 80 | 0 | 2025-01-05 | 2026-10-12 |
| DIAPAC afluente | P total | BIOTA | Eventual | `FOSFORO` | 7:00 a. m. (fija; antes solo el día) | 80 | 0 | 2025-01-05 | 2026-10-05 |
| DIAPAC cámara A | DQO | BIOTA | Eventual | `DQO5` | 7:00 a. m. (fija; antes solo el día) | 85 | 0 | 2025-01-03 | 2026-10-13 |
| DIAPAC cámara A | G&A | BIOTA | Eventual | `GYA` | 7:00 a. m. (fija; antes solo el día) | 86 | 0 | 2025-01-03 | 2026-10-13 |
| DIAPAC cámara A | Recuento | BIOTA | Eventual | `MICROBIOLOGIA` | 7:00 a. m. (fija; antes solo el día) | 14 | 0 | 2025-01-12 | 2026-06-28 |
| DIAPAC cámara A | SSED | BIOTA | Eventual | `SOL SED` | 7:00 a. m. (fija; antes solo el día) | 83 | 0 | 2025-01-05 | 2026-10-12 |
| DIAPAC cámara A | SST | BIOTA | Eventual | `SST `; `SST 6` | 7:00 a. m. (fija; antes solo el día) | 165 | 0 | 2025-01-03 | 2026-10-13 |
| DIAPAC cámara B | DQO | BIOTA | Eventual | `DQO7` | 7:00 a. m. (fija; antes solo el día) | 81 | 0 | 2025-01-07 | 2026-10-13 |
| DIAPAC cámara B | G&A | BIOTA | Eventual | `GYA9` | 7:00 a. m. (fija; antes solo el día) | 82 | 0 | 2025-01-07 | 2026-10-13 |
| DIAPAC cámara B | Recuento | BIOTA | Eventual | `MICROBIOLOGIA4` | 7:00 a. m. (fija; antes solo el día) | 16 | 0 | 2025-01-19 | 2026-10-12 |
| DIAPAC cámara B | SSED | BIOTA | Eventual | `SOL SED2` | 7:00 a. m. (fija; antes solo el día) | 82 | 0 | 2025-01-05 | 2026-10-12 |
| DIAPAC cámara B | SST | BIOTA | Eventual | `SST 3`; `SST 8` | 7:00 a. m. (fija; antes solo el día) | 162 | 0 | 2025-01-05 | 2026-10-13 |

Columna de fecha: `Fecha`.

Columnas que **no** se importan:

- `GYA10`: Sin cámara ni día en el encabezado (4 valores); decidido no importarla.

### Ecodisel — hoja «ECODIESEL» de `SEGUIMIENTO UT DESCONTAMINACIÓN NUEVO.xlsx`

| Punto | Parámetro | Fuente | Frecuencia | Encabezados del Excel | Hora que se asigna | Mediciones | Dudosas | Desde | Hasta |
|---|---|---|---|---|---|---|---|---|---|
| Ecodiesel | DQO | BIOTA | Eventual | `EcoDisel DQO` | 7:00 a. m. (fija; antes solo el día) | 113 | 0 | 2023-02-23 | 2026-08-13 |
| Ecodiesel | Fenoles | BIOTA | Eventual | `EcoDisel Fenol` | 7:00 a. m. (fija; antes solo el día) | 113 | 0 | 2023-02-23 | 2026-08-13 |
| Ecodiesel | G&A | BIOTA | Eventual | `EcoDisel GyA` | 7:00 a. m. (fija; antes solo el día) | 113 | 0 | 2023-03-06 | 2026-08-13 |
| Ecodiesel | SST | BIOTA | Eventual | `EcoDisel SST` | 7:00 a. m. (fija; antes solo el día) | 115 | 0 | 2023-02-23 | 2026-08-13 |
| Ecodiesel | Sulfatos | BIOTA | Eventual | `EcoDisel Sulfatos` | 7:00 a. m. (fija; antes solo el día) | 90 | 0 | 2023-08-09 | 2026-08-13 |
| Ecodiesel | pH | BIOTA | Eventual | `EcoDisel PH` | 7:00 a. m. (fija; antes solo el día) | 117 | 0 | 2023-02-23 | 2026-08-13 |

Columna de fecha: `Fecha`.

### FASE1 — hoja «FASE I» de `SEGUIMIENTO UT DESCONTAMINACIÓN NUEVO.xlsx`

| Punto | Parámetro | Fuente | Frecuencia | Encabezados del Excel | Hora que se asigna | Mediciones | Dudosas | Desde | Hasta |
|---|---|---|---|---|---|---|---|---|---|
| BA-4001 | DQO | BIOTA | 7 a. m. y 4 p. m. | `BA4001 DQO 7 AM`; `BA4001 DQO 4 PM` | 7:00 a. m. (fija), 4:00 p. m. (fija) | 1.553 | 0 | 2022-07-11 | 2026-10-13 |
| BA-4001 | Fenoles | BIOTA | 7 a. m. y 4 p. m. | `BA4001 FENOL 7 AM`; `BA4001 FENOL 4 PM` | 7:00 a. m. (fija), 4:00 p. m. (fija) | 2.757 | 0 | 2022-07-01 | 2026-10-13 |
| BA-4001 | SST | BIOTA | 7 a. m. y 4 p. m. | `BA4001 SST 7 AM`; `BA4001 SST 4 PM` | 7:00 a. m. (fija), 4:00 p. m. (fija) | 2.725 | 0 | 2022-07-01 | 2026-10-13 |
| BA-4001 | Sulfuros | BIOTA | 7 a. m. y 4 p. m. | `BA4001 SULFUROS 7 AM`; `BA4001 SULFUROS 4 PM` | 7:00 a. m. (fija), 4:00 p. m. (fija) | 2.584 | 0 | 2022-07-01 | 2026-10-13 |
| BA-4001 | Temperatura | BIOTA | 7 a. m. y 4 p. m. | `BA4001 T 7 AM`; `BA4001 T 4 PM` | 7:00 a. m. (fija), 4:00 p. m. (fija) | 2.757 | 0 | 2022-07-01 | 2026-10-13 |
| BA-4001 | pH | BIOTA | 7 a. m. y 4 p. m. | `BA4001 PH 7 AM`; `BA4001 PH 4 PM` | 7:00 a. m. (fija), 4:00 p. m. (fija) | 2.758 | 1 | 2022-07-01 | 2026-10-13 |
| BA-4008 | DQO | BIOTA | 7 a. m. y 4 p. m. | `BA4008 DQO` | 7:00 a. m. (fija) | 971 | 0 | 2024-02-01 | 2026-10-13 |
| BA-4008 | Fenoles | BIOTA | 7 a. m. y 4 p. m. | `BA4008 FENOL 7 AM`; `BA4008 FENOL 4 PM` | 7:00 a. m. (fija), 4:00 p. m. (fija) | 978 | 0 | 2024-02-01 | 2026-10-13 |
| BA-4008 | G&A | BIOTA | 7 a. m. y 4 p. m. | `BA4008 GYA` | 7:00 a. m. (fija) | 940 | 0 | 2024-03-01 | 2026-10-13 |
| BA-4008 | OD | BIOTA | 7 a. m. y 4 p. m. | `BA4008 OD 7 AM`; `BA4008 OD 4 PM` | 7:00 a. m. (fija), 4:00 p. m. (fija) | 1.538 | 0 | 2024-02-09 | 2026-10-13 |
| BA-4008 | P total | BIOTA | Diaria | `BA4008 P-TOTAL` | 7:00 a. m. (fija; antes solo el día) | 752 | 0 | 2024-09-02 | 2026-10-09 |
| BA-4008 | SST | BIOTA | 7 a. m. y 4 p. m. | `BA4008 SST` | 7:00 a. m. (fija) | 973 | 0 | 2024-02-01 | 2026-10-13 |
| BA-4008 | Sulfatos | BIOTA | Diaria | `BA4008 SULFATOS` | 7:00 a. m. (fija; antes solo el día) | 968 | 0 | 2024-02-01 | 2026-10-13 |
| BA-4008 | Temperatura | BIOTA | 7 a. m. y 4 p. m. | `BA4008 T 7 AM`; `BA4008 T 4 PM` | 7:00 a. m. (fija), 4:00 p. m. (fija) | 1.598 | 0 | 2024-02-01 | 2026-10-13 |
| BA-4008 | pH | BIOTA | 7 a. m. y 4 p. m. | `BA4008 pH 7 AM`; `BA4008 pH 4 PM` | 7:00 a. m. (fija), 4:00 p. m. (fija) | 1.598 | 1 | 2024-02-01 | 2026-10-13 |
| BA-4008 entrada | N total | BIOTA | Diaria | `BA4008 ENTRADA N-Total` | 7:00 a. m. (fija; antes solo el día) | 782 | 0 | 2024-03-03 | 2026-10-13 |
| BA-4008 entrada | N-NH3 | BIOTA | Diaria | `BA4008 ENTRADA N-NH3` | 7:00 a. m. (fija; antes solo el día) | 7 | 0 | 2025-03-11 | 2025-03-17 |
| BA-4008 salida | N total | BIOTA | Diaria | `BA4008 SALIDA N-Total` | 7:00 a. m. (fija; antes solo el día) | 812 | 0 | 2024-03-04 | 2026-10-13 |
| BA-4008 salida | N-NH3 | BIOTA | Diaria | `BA4008 SALIDA N-NH3` | 7:00 a. m. (fija; antes solo el día) | 905 | 0 | 2024-04-01 | 2026-10-13 |
| BA-4009A | DQO soluble | BIOTA | 7 a. m. y 4 p. m. | `Monitoreo BA 4009A DQO SOL 7 AM`; `Monitoreo BA 4009A DQO SOL 4 PM` | 7:00 a. m. (fija), 4:00 p. m. (fija) | 2.267 | 0 | 2022-07-01 | 2026-10-13 |
| BA-4009A | Fenoles | BIOTA | 7 a. m. y 4 p. m. | `Monitoreo BA 4009A FENOL 7 AM`; `Monitoreo BA 4009A FENOL 4 PM` | 7:00 a. m. (fija), 4:00 p. m. (fija) | 2.756 | 0 | 2022-07-01 | 2026-10-13 |
| BA-4009A | Flujo | BIOTA | Diaria | `Monitoreo BA-4009A FLUJO\ngal/min` | 7:00 a. m. (fija; antes solo el día) | 7 | 0 | 2025-03-11 | 2025-03-17 |
| BA-4009A | OD | BIOTA | 7 a. m. y 4 p. m. | `Monitoreo BA 4009A OD 7 AM`; `Monitoreo BA 4009A OD 4 PM` | 7:00 a. m. (fija), 4:00 p. m. (fija) | 2.685 | 0 | 2022-07-01 | 2026-10-13 |
| BA-4009A | Recuento | BIOTA | Diaria | `Monitoreo BA 4009A RECUENTO (ufc/mI)` | 7:00 a. m. (fija; antes solo el día) | 1.333 | 0 | 2022-07-01 | 2026-10-11 |
| BA-4009A | SSED | BIOTA | 7 a. m. y 4 p. m. | `Monitoreo BA 4009A S.SED 7 AM`; `Monitoreo BA 4009A S.SED 4 PM` | 7:00 a. m. (fija), 4:00 p. m. (fija) | 2.756 | 0 | 2022-07-01 | 2026-10-13 |
| BA-4009A | SST | BIOTA | 7 a. m. y 4 p. m. | `Monitoreo BA 4009A SST 7 AM`; `Monitoreo BA 4009A SST 4 PM7` | 7:00 a. m. (fija), 4:00 p. m. (fija) | 2.757 | 0 | 2022-07-01 | 2026-10-13 |
| BA-4009A | Sulfatos | BIOTA | Diaria | `Monitoreo BA4009A\nSULFATOS` | 7:00 a. m. (fija; antes solo el día) | 1.508 | 0 | 2022-07-01 | 2026-10-13 |
| BA-4009A | TRH | BIOTA | Diaria | `Monitoreo BA-4009A TRH\nHORAS` | 7:00 a. m. (fija; antes solo el día) | 7 | 0 | 2025-03-11 | 2025-03-17 |
| BA-4009A | Temperatura | BIOTA | 7 a. m. y 4 p. m. | `Monitoreo BA 4009A T 7 AM`; `Monitoreo BA 4009A T 4 PM` | 7:00 a. m. (fija), 4:00 p. m. (fija) | 2.757 | 1 | 2022-07-01 | 2026-10-13 |
| BA-4009A | pH | BIOTA | 7 a. m. y 4 p. m. | `Monitoreo BA 4009A PH 7 AM`; `Monitoreo BA 4009A PH 4 PM` | 7:00 a. m. (fija), 4:00 p. m. (fija) | 2.757 | 0 | 2022-07-01 | 2026-10-13 |
| BA-4009A entrada | DQO | BIOTA | 7 a. m. y 4 p. m. | `Entrada a BA 4009A DQO 7 am`; `Entrada a BA 4009A DQO 4 pm` | 7:00 a. m. (fija), 4:00 p. m. (fija) | 1.013 | 0 | 2024-01-02 | 2026-10-13 |
| BA-4009A entrada | Fenoles | BIOTA | 7 a. m. y 4 p. m. | `Entrada a BA 4009A FENOL 7 am`; `Entrada a BA 4009A FENOL 4 pm` | 7:00 a. m. (fija), 4:00 p. m. (fija) | 1.608 | 0 | 2024-01-02 | 2026-10-13 |
| BA-4009A entrada | G&A | BIOTA | Diaria | `Entrada a BA 4009A \nGyA` | 7:00 a. m. (fija; antes solo el día) | 963 | 0 | 2024-01-02 | 2026-10-13 |
| BA-4009A entrada | Hierro | BIOTA | Diaria | `Entrada a BA 4009A Hierro` | 7:00 a. m. (fija; antes solo el día) | 249 | 0 | 2026-02-04 | 2026-10-13 |
| BA-4009A entrada | N total | BIOTA | Diaria | `Entrada a BA 4009A \nN-Total` | 7:00 a. m. (fija; antes solo el día) | 831 | 0 | 2024-01-02 | 2026-10-13 |
| BA-4009A entrada | N-NH3 | BIOTA | Diaria | `Entrada a BA 4009A \nN-NH3` | 7:00 a. m. (fija; antes solo el día) | 949 | 0 | 2024-01-02 | 2026-10-13 |
| BA-4009A entrada | OD | BIOTA | 7 a. m. y 4 p. m. | `Entrada a BA 4009A O.D 7 am`; `Entrada a BA 4009A O.D 4 pm` | 7:00 a. m. (fija), 4:00 p. m. (fija) | 1.537 | 0 | 2024-01-02 | 2026-10-13 |
| BA-4009A entrada | SST | BIOTA | 7 a. m. y 4 p. m. | `Entrada a BA 4009A SST 7 am`; `Entrada a BA 4009A SST 4 pm` | 7:00 a. m. (fija), 4:00 p. m. (fija) | 1.609 | 0 | 2024-01-02 | 2026-10-13 |
| BA-4009A entrada | Sulfatos | BIOTA | Diaria | `Entrada a BA 4009A \nSULFATOS` | 7:00 a. m. (fija; antes solo el día) | 950 | 0 | 2024-01-02 | 2026-10-13 |
| BA-4009A entrada | Sulfuros | BIOTA | 7 a. m. y 4 p. m. | `Entrada a BA 4009A SULFUROS 7 am`; `Entrada a BA 4009A SULFUROS 4 pm` | 7:00 a. m. (fija), 4:00 p. m. (fija) | 1.434 | 0 | 2024-01-02 | 2026-10-13 |
| BA-4009A entrada | Temperatura | BIOTA | 7 a. m. y 4 p. m. | `Entrada a BA 4009A T. °C 7 am`; `Entrada a BA 4009A T. °C 4 pm` | 7:00 a. m. (fija), 4:00 p. m. (fija) | 1.609 | 0 | 2024-01-02 | 2026-10-13 |
| BA-4009A entrada | pH | BIOTA | 7 a. m. y 4 p. m. | `Entrada a BA 4009A pH 7 am`; `Entrada a BA 4009A pH 4 pm` | 7:00 a. m. (fija), 4:00 p. m. (fija) | 1.609 | 0 | 2024-01-02 | 2026-10-13 |
| BA-4010 | DQO | BIOTA | 7 a. m. y 4 p. m. | `VERTEDERO BA4010 DQO 7 AM`; `VERTEDERO BA4010 DQO 4 PM` | 7:00 a. m. (fija), 4:00 p. m. (fija) | 2.326 | 0 | 2022-07-01 | 2026-10-13 |
| BA-4010 | Fenoles | BIOTA | 7 a. m. y 4 p. m. | `VERTEDERO BA4010 FENOL 7 AM`; `VERTEDERO BA4010 FENOL 4 PM` | 7:00 a. m. (fija), 4:00 p. m. (fija) | 2.747 | 0 | 2022-07-01 | 2026-10-13 |
| BA-4010 | G&A | BIOTA | Diaria | `GyA BA4010` | 7:00 a. m. (fija; antes solo el día) | 498 | 0 | 2025-06-01 | 2026-10-13 |
| BA-4010 | Hierro | BIOTA | Diaria | `VERTEDERO BA4010 Hierro` | 7:00 a. m. (fija; antes solo el día) | 250 | 0 | 2026-02-04 | 2026-10-13 |
| BA-4010 | N total | BIOTA | Diaria | `VERTEDERO BA4010 N-TOTAL` | 7:00 a. m. (fija; antes solo el día) | 1.384 | 0 | 2022-07-05 | 2026-10-13 |
| BA-4010 | N-NH3 | BIOTA | Diaria | `VERTEDERO BA4010 N-NH3` | 7:00 a. m. (fija; antes solo el día) | 1.486 | 0 | 2022-07-05 | 2026-10-13 |
| BA-4010 | OD | BIOTA | 7 a. m. y 4 p. m. | `VERTEDERO BA4010 OD 7 AM`; `VERTEDERO BA4010 OD 4 PM` | 7:00 a. m. (fija), 4:00 p. m. (fija) | 2.685 | 0 | 2022-07-01 | 2026-10-13 |
| BA-4010 | Recuento | BIOTA | Diaria | `VERTEDERO BA4010 RECUENTO (ufc/ml)` | 7:00 a. m. (fija; antes solo el día) | 1.020 | 0 | 2023-06-01 | 2026-10-11 |
| BA-4010 | SST | BIOTA | 7 a. m. y 4 p. m. | `VERTEDERO BA4010 SST 7 AM`; `VERTEDERO BA4010 SST 4 PM1` | 7:00 a. m. (fija), 4:00 p. m. (fija) | 2.756 | 0 | 2022-07-01 | 2026-10-13 |
| BA-4010 | Sulfatos | BIOTA | Diaria | `VERTEDERO BA4010 SULFATOS` | 7:00 a. m. (fija; antes solo el día) | 1.446 | 0 | 2022-07-05 | 2026-10-13 |
| BA-4010 | Sulfuros | BIOTA | 7 a. m. y 4 p. m. | `VERTEDERO BA4010 SULFUROS 7 AM`; `VERTEDERO BA4010 SULFUROS 4 PM` | 7:00 a. m. (fija), 4:00 p. m. (fija) | 2.582 | 0 | 2022-07-01 | 2026-10-13 |
| BA-4010 | Temperatura | BIOTA | 7 a. m. y 4 p. m. | `VERTEDERO BA4010 T 7 AM`; `VERTEDERO BA4010 T 4 PM` | 7:00 a. m. (fija), 4:00 p. m. (fija) | 2.757 | 0 | 2022-07-01 | 2026-10-13 |
| BA-4010 | pH | BIOTA | 7 a. m. y 4 p. m. | `VERTEDERO BA4010 PH 7 AM`; `VERTEDERO BA4010 PH 4 PM` | 7:00 a. m. (fija), 4:00 p. m. (fija) | 2.756 | 0 | 2022-07-01 | 2026-10-13 |
| BA-4080 | DQO | BIOTA | 7 a. m. y 4 p. m. | `SALIDA BA4080 DQO 7 AM`; `SALIDA BA4080 DQO 4 PM` | 7:00 a. m. (fija), 4:00 p. m. (fija) | 1.082 | 0 | 2022-07-01 | 2025-06-16 |
| BA-4080 | Fenoles | BIOTA | 7 a. m. y 4 p. m. | `SALIDA BA4080 FENOL 7 AM`; `SALIDA BA4080 FENOL 4 PM` | 7:00 a. m. (fija), 4:00 p. m. (fija) | 2.098 | 0 | 2022-07-01 | 2025-06-16 |
| BA-4080 | G&A | BIOTA | Diaria | `SALIDA BA4080 GyA` | 7:00 a. m. (fija; antes solo el día) | 1.070 | 0 | 2022-07-01 | 2025-06-17 |
| BA-4080 | N total | BIOTA | Diaria | `SALIDA BA4080 N-TOTAL` | 7:00 a. m. (fija; antes solo el día) | 1.025 | 0 | 2022-07-02 | 2025-06-16 |
| BA-4080 | N-NH3 | BIOTA | Diaria | `SALIDA BA4080 N-NH3` | 7:00 a. m. (fija; antes solo el día) | 1.011 | 0 | 2022-07-01 | 2025-06-16 |
| BA-4080 | OD | BIOTA | 7 a. m. y 4 p. m. | `SALIDA BA4080 OD 7 AM`; `SALIDA BA4080 OD 4 PM` | 7:00 a. m. (fija), 4:00 p. m. (fija) | 2.027 | 0 | 2022-07-01 | 2025-06-17 |
| BA-4080 | P total | BIOTA | Diaria | `SALIDA BA4080\nFÓSFORO` | 7:00 a. m. (fija; antes solo el día) | 599 | 0 | 2022-12-04 | 2025-03-17 |
| BA-4080 | SSED | BIOTA | Diaria | `SALIDA BA4080\nS.SED` | 7:00 a. m. (fija; antes solo el día) | 96 | 0 | 2022-11-01 | 2025-03-17 |
| BA-4080 | SST | BIOTA | 7 a. m. y 4 p. m. | `SALIDA BA4080 SST 7 AM`; `SALIDA BA4080 SST 4 PM` | 7:00 a. m. (fija), 4:00 p. m. (fija) | 2.098 | 0 | 2022-07-01 | 2025-06-16 |
| BA-4080 | Sulfatos | BIOTA | Diaria | `SALIDA BA4080 SULFATOS` | 7:00 a. m. (fija; antes solo el día) | 1.027 | 0 | 2022-07-01 | 2025-06-16 |
| BA-4080 | Temperatura | BIOTA | 7 a. m. y 4 p. m. | `SALIDA BA4080 T 7 AM`; `SALIDA BA4080 T 4 PM` | 7:00 a. m. (fija), 4:00 p. m. (fija) | 2.099 | 0 | 2022-07-01 | 2025-06-17 |
| BA-4080 | pH | BIOTA | 7 a. m. y 4 p. m. | `SALIDA BA4080 PH 7 AM`; `SALIDA BA4080 PH 4 PM` | 7:00 a. m. (fija), 4:00 p. m. (fija) | 2.098 | 0 | 2022-07-01 | 2025-06-16 |
| MP-4042A | SST | BIOTA | 7 a. m. y 4 p. m. | `MP4042A 7 AM`; `MP4042A 4 PM` | 7:00 a. m. (fija), 4:00 p. m. (fija) | 142 | 0 | 2023-11-28 | 2026-09-14 |
| MP-4042B | SST | BIOTA | 7 a. m. y 4 p. m. | `MP4042B 7 AM`; `MP4042B 4 PM` | 7:00 a. m. (fija), 4:00 p. m. (fija) | 213 | 0 | 2023-11-28 | 2026-10-09 |
| MP-4042C | SST | BIOTA | 7 a. m. y 4 p. m. | `MP4042C 7 AM`; `MP4042C 4 PM` | 7:00 a. m. (fija), 4:00 p. m. (fija) | 96 | 0 | 2023-12-03 | 2026-09-25 |
| MP-4051A | SST | BIOTA | 7 a. m. y 4 p. m. | `MP4051A 7 AM`; `MP4051A 4 PM` | 7:00 a. m. (fija), 4:00 p. m. (fija) | 1.161 | 0 | 2022-08-27 | 2026-10-13 |
| MP-4051B | SST | BIOTA | 7 a. m. y 4 p. m. | `MP4051B 7 AM`; `MP4051B 4 PM` | 7:00 a. m. (fija), 4:00 p. m. (fija) | 1.576 | 0 | 2022-07-17 | 2026-10-12 |
| MP-4051C | SST | BIOTA | 7 a. m. y 4 p. m. | `MP4051C 7 AM`; `MP4051C 4 PM` | 7:00 a. m. (fija), 4:00 p. m. (fija) | 1.233 | 0 | 2022-07-17 | 2026-09-27 |

Columna de fecha: `Fecha`.

Columnas que **no** se importan:

- `Blanco 1`: Columna separadora, vacía.
- `Blanco 2`: Columna separadora, vacía.
- `Blanco 3`: Columna separadora, vacía.
- `Monitoreo BA 4009A ALIMENTO`: F/M: fórmula (casi toda #REF!). La app lo calculará.
- `Monitoreo BA 4009A VOL LODO`: IVL: fórmula. La app lo calculará.
- `Blanco 4`: Columna separadora, vacía.
- `Blanco 5`: Columna separadora, vacía.
- `Blanco 7`: Columna separadora, vacía.

### FenolAASepSoda4 — hoja «A.AGRIAS SEP.» de `SEGUIMIENTO UT DESCONTAMINACIÓN NUEVO.xlsx`

| Punto | Parámetro | Fuente | Frecuencia | Encabezados del Excel | Hora que se asigna | Mediciones | Dudosas | Desde | Hasta |
|---|---|---|---|---|---|---|---|---|---|
| Agua agria | DQO | BIOTA | Diaria | `AA DQO` | 7:00 a. m. (fija; antes solo el día) | 1.543 | 0 | 2022-07-04 | 2026-10-13 |
| Agua agria | Fenoles | BIOTA | Diaria | `AA Fenol` | 7:00 a. m. (fija; antes solo el día) | 1.547 | 0 | 2022-07-01 | 2026-10-13 |
| Agua agria | Temperatura | BIOTA | Diaria | `AA Temp` | 7:00 a. m. (fija; antes solo el día) | 1.547 | 0 | 2022-07-01 | 2026-10-13 |
| Agua agria | pH | BIOTA | Diaria | `AA ph` | 7:00 a. m. (fija; antes solo el día) | 1.548 | 0 | 2022-07-01 | 2026-10-13 |
| SE-3010 | DQO | BIOTA | a. m. y p. m. | `SE3010 DQO am`; `SE3010 DQO pm` | 7:00 a. m., 4:00 p. m. (fijas; antes mañana y tarde) | 2.672 | 0 | 2022-07-01 | 2026-10-13 |
| SE-3010 | Fenoles | BIOTA | a. m. y p. m. | `SE3010 Fenol am`; `SE3010 Fenol pm` | 7:00 a. m., 4:00 p. m. (fijas; antes mañana y tarde) | 2.674 | 0 | 2022-07-01 | 2026-10-13 |
| SE-3010 | Sulfatos | BIOTA | a. m. y p. m. | `SEP3010 SO4`; `SEP3010 SO42` | 7:00 a. m., 4:00 p. m. (fijas; antes mañana y tarde) | 2.433 | 0 | 2023-02-13 | 2026-10-13 |
| SE-3010 | pH | BIOTA | a. m. y p. m. | `SE3010 ph am`; `SE3010 ph pm` | 7:00 a. m., 4:00 p. m. (fijas; antes mañana y tarde) | 2.602 | 0 | 2022-08-09 | 2026-10-13 |
| SE-3020 | DQO | BIOTA | a. m. y p. m. | `SEO3020 DQO AM`; `SEP 3020 DQO PM` | 7:00 a. m., 4:00 p. m. (fijas; antes mañana y tarde) | 2.763 | 0 | 2022-07-01 | 2026-10-13 |
| SE-3020 | Fenoles | BIOTA | a. m. y p. m. | `SEP3020 Fenol`; `SEP3020 FENOL PM` | 7:00 a. m., 4:00 p. m. (fijas; antes mañana y tarde) | 2.761 | 0 | 2022-07-01 | 2026-10-13 |
| SE-3020 | Sulfatos | BIOTA | a. m. y p. m. | `SEP3020 SO4`; `SEP3020 SO42` | 7:00 a. m., 4:00 p. m. (fijas; antes mañana y tarde) | 1.723 | 0 | 2024-02-27 | 2026-10-13 |
| SE-3020 | pH | BIOTA | a. m. y p. m. | `SEP3020 pH AM`; `SEP3020 PH PM` | 7:00 a. m., 4:00 p. m. (fijas; antes mañana y tarde) | 2.760 | 1 | 2022-07-01 | 2026-10-13 |
| SE-3030 | DQO | BIOTA | a. m. y p. m. | `SE3030 DQO am`; `SE3030 DQO pm` | 7:00 a. m., 4:00 p. m. (fijas; antes mañana y tarde) | 2.672 | 0 | 2022-07-01 | 2026-10-13 |
| SE-3030 | Fenoles | BIOTA | a. m. y p. m. | `SE3030 Fenol am`; `SE3030 Fenol pm` | 7:00 a. m., 4:00 p. m. (fijas; antes mañana y tarde) | 2.672 | 0 | 2022-07-01 | 2026-10-13 |
| SE-3030 | Sulfatos | BIOTA | a. m. y p. m. | `SEP3030 SO4`; `SEP3030 SO42` | 7:00 a. m., 4:00 p. m. (fijas; antes mañana y tarde) | 2.431 | 0 | 2023-02-13 | 2026-10-13 |
| SE-3030 | pH | BIOTA | a. m. y p. m. | `SE3030 ph am`; `SE3030 ph pm` | 7:00 a. m., 4:00 p. m. (fijas; antes mañana y tarde) | 2.603 | 0 | 2022-08-09 | 2026-10-13 |
| SE-3050 | DQO | BIOTA | Diaria | `SE3050 DQO` | 7:00 a. m. (fija; antes solo el día) | 1.510 | 0 | 2022-07-01 | 2026-09-06 |
| SE-3050 | Fenoles | BIOTA | Diaria | `SE3050 Fenol` | 7:00 a. m. (fija; antes solo el día) | 1.509 | 0 | 2022-07-01 | 2026-09-06 |
| SE-3050 | Sulfatos | BIOTA | Diaria | `sep3050SO4` | 7:00 a. m. (fija; antes solo el día) | 905 | 0 | 2024-03-04 | 2026-09-06 |
| SE-3050 | pH | BIOTA | Diaria | `SE3050 ph` | 7:00 a. m. (fija; antes solo el día) | 1.510 | 0 | 2022-07-01 | 2026-09-06 |
| SE-3060 | DQO | BIOTA | a. m. y p. m. | `SE3060 DQO am`; `SE3060 DQO pm` | 7:00 a. m., 4:00 p. m. (fijas; antes mañana y tarde) | 2.643 | 0 | 2022-07-01 | 2026-10-13 |
| SE-3060 | Fenoles | BIOTA | a. m. y p. m. | `SE3060 Fenol am`; `SE3060 Fenol pm` | 7:00 a. m., 4:00 p. m. (fijas; antes mañana y tarde) | 2.644 | 0 | 2022-07-01 | 2026-10-13 |
| SE-3060 | Sulfatos | BIOTA | a. m. y p. m. | `SEP 3060 SO4`; `SEP 3060 SO42` | 7:00 a. m., 4:00 p. m. (fijas; antes mañana y tarde) | 2.415 | 0 | 2023-02-13 | 2026-10-13 |
| SE-3060 | pH | BIOTA | a. m. y p. m. | `SE3060 ph am`; `SE3060 ph pm` | 7:00 a. m., 4:00 p. m. (fijas; antes mañana y tarde) | 2.575 | 0 | 2022-08-09 | 2026-10-13 |

Columna de fecha: `Fecha`.

### FenolAASepSoda48 — hoja «K-SODAS» de `SEGUIMIENTO UT DESCONTAMINACIÓN NUEVO.xlsx`

| Punto | Parámetro | Fuente | Frecuencia | Encabezados del Excel | Hora que se asigna | Mediciones | Dudosas | Desde | Hasta |
|---|---|---|---|---|---|---|---|---|---|
| D-4006 | DQO | BIOTA | Eventual | `D4006 DQO` | 7:00 a. m. (fija; antes solo el día) | 32 | 0 | 2022-08-01 | 2023-08-07 |
| D-4006 | Fenoles | BIOTA | Eventual | `D4006 Fenol` | 7:00 a. m. (fija; antes solo el día) | 32 | 0 | 2022-08-01 | 2023-08-07 |
| D-4006 | pH | BIOTA | Eventual | `D4006 ph` | 7:00 a. m. (fija; antes solo el día) | 29 | 1 | 2022-07-24 | 2023-07-30 |
| K-4090 | DQO | BIOTA | Eventual | `K4090 DQO` | 7:00 a. m. (fija; antes solo el día) | 181 | 0 | 2023-04-19 | 2026-10-13 |
| K-4090 | Fenoles | BIOTA | Eventual | `K4090 Fenol` | 7:00 a. m. (fija; antes solo el día) | 181 | 0 | 2023-04-19 | 2026-10-13 |
| K-4090 | pH | BIOTA | Eventual | `K4090 ph` | 7:00 a. m. (fija; antes solo el día) | 181 | 0 | 2023-04-19 | 2026-10-13 |
| K-4091 | DQO | BIOTA | Eventual | `K4091 DQO` | 7:00 a. m. (fija; antes solo el día) | 467 | 0 | 2022-07-04 | 2026-10-12 |
| K-4091 | Fenoles | BIOTA | Eventual | `K4091 Fenol` | 7:00 a. m. (fija; antes solo el día) | 473 | 0 | 2022-07-04 | 2026-10-12 |
| K-4091 | Sulfatos | BIOTA | Eventual | `K4091 Sulfato` | 7:00 a. m. (fija; antes solo el día) | 313 | 0 | 2023-08-16 | 2026-10-12 |
| K-4091 | pH | BIOTA | Eventual | `K4091 ph` | 7:00 a. m. (fija; antes solo el día) | 472 | 0 | 2022-07-04 | 2026-10-12 |
| K-4092 | DQO | BIOTA | Eventual | `K4092 DQO` | 7:00 a. m. (fija; antes solo el día) | 4 | 0 | 2023-09-14 | 2025-06-10 |
| K-4092 | Fenoles | BIOTA | Eventual | `K4092 Fenol` | 7:00 a. m. (fija; antes solo el día) | 4 | 0 | 2023-09-14 | 2024-04-08 |
| K-4092 | Sulfatos | BIOTA | Eventual | `K4092 Sulfato` | 7:00 a. m. (fija; antes solo el día) | 4 | 0 | 2023-09-14 | 2024-04-08 |
| K-4092 | pH | BIOTA | Eventual | `K4092 ph` | 7:00 a. m. (fija; antes solo el día) | 4 | 0 | 2023-09-14 | 2024-04-08 |
| K-4094 | DQO | BIOTA | Eventual | `K4094 DQO` | 7:00 a. m. (fija; antes solo el día) | 18 | 0 | 2023-08-30 | 2024-02-21 |
| K-4094 | Fenoles | BIOTA | Eventual | `K4094 Fenol` | 7:00 a. m. (fija; antes solo el día) | 18 | 0 | 2023-08-30 | 2024-02-21 |
| K-4094 | Sulfatos | BIOTA | Eventual | `K4094 Sulfato` | 7:00 a. m. (fija; antes solo el día) | 18 | 0 | 2023-08-30 | 2024-02-21 |
| K-4094 | pH | BIOTA | Eventual | `K4094 ph` | 7:00 a. m. (fija; antes solo el día) | 18 | 0 | 2023-08-30 | 2024-02-21 |

Columna de fecha: `Fecha`.

### Laboratorio — hoja «Datos LABORATORIO» de `SEGUIMIENTO UT DESCONTAMINACIÓN NUEVO.xlsx`

| Punto | Parámetro | Fuente | Frecuencia | Encabezados del Excel | Hora que se asigna | Mediciones | Dudosas | Desde | Hasta |
|---|---|---|---|---|---|---|---|---|---|
| Alquilación | pH | Labviewer | Diaria | `Alquilación pH` | solo el día (sin hora) | 92 | 0 | 2023-01-04 | 2023-04-15 |
| Amador | pH | Labviewer | Diaria | `Amador pH` | solo el día (sin hora) | 92 | 0 | 2023-01-04 | 2023-04-15 |
| BA-4001 | Conductividad | Labviewer | Diaria | `BA4001` | solo el día (sin hora) | 214 | 0 | 2024-03-20 | 2026-10-11 |
| BA-4001 | DQO | Labviewer | Diaria | `BA4001 DQO` | solo el día (sin hora) | 249 | 0 | 2023-01-01 | 2026-10-07 |
| BA-4001 | Fenoles | Labviewer | Diaria | `BA4001 Fenol` | solo el día (sin hora) | 294 | 0 | 2023-01-01 | 2026-10-08 |
| BA-4001 | G&A | Labviewer | Diaria | `BA4001 G&A` | solo el día (sin hora) | 1.312 | 0 | 2023-01-01 | 2026-10-13 |
| BA-4001 | H2S | Labviewer | Diaria | `BA4001 H2S` | solo el día (sin hora) | 180 | 0 | 2023-01-01 | 2026-10-11 |
| BA-4001 | Hierro | Labviewer | Diaria | `BA4001 FE` | solo el día (sin hora) | 1 | 0 | 2023-10-30 | 2023-10-30 |
| BA-4001 | N total | Labviewer | Diaria | `BA-4001 NITROGENO TOTAL` | solo el día (sin hora) | 158 | 0 | 2023-01-05 | 2026-10-08 |
| BA-4001 | RSH | Labviewer | Diaria | `BA4001 RSH` | solo el día (sin hora) | 184 | 0 | 2023-01-01 | 2026-10-11 |
| BA-4001 | SS | Labviewer | Diaria | `BA4001 SS` | solo el día (sin hora) | 563 | 0 | 2023-01-01 | 2026-10-12 |
| BA-4001 | ST | Labviewer | — | `BA4001 ST` | solo el día (sin hora) | 0 | 0 | — | — |
| BA-4002 | DQO | Labviewer | Diaria | `BA4002 DQO` | solo el día (sin hora) | 1 | 0 | 2025-08-21 | 2025-08-21 |
| BA-4002 | Fenoles | Labviewer | Diaria | `BA4002 Fenol` | solo el día (sin hora) | 1 | 0 | 2025-08-21 | 2025-08-21 |
| BA-4002 | G&A | Labviewer | Diaria | `BA4002 G&A` | solo el día (sin hora) | 1 | 0 | 2025-08-21 | 2025-08-21 |
| BA-4002 | H2S | Labviewer | Diaria | `BA4002 H2S` | solo el día (sin hora) | 1 | 0 | 2025-08-21 | 2025-08-21 |
| BA-4002 | NH3 | Labviewer | Diaria | `BA4002 NH3` | solo el día (sin hora) | 1 | 0 | 2025-08-21 | 2025-08-21 |
| BA-4002 | RSH | Labviewer | Diaria | `BA4002 RSH` | solo el día (sin hora) | 1 | 0 | 2025-08-21 | 2025-08-21 |
| BA-4002 | SS | Labviewer | Diaria | `BA4002 SS` | solo el día (sin hora) | 1 | 0 | 2025-08-21 | 2025-08-21 |
| BA-4002 | ST | Labviewer | Diaria | `BA4002 ST` | solo el día (sin hora) | 1 | 0 | 2025-08-21 | 2025-08-21 |
| BA-4005A/B | G&A | Labviewer | Diaria | `BA4005A/B G&A` | solo el día (sin hora) | 283 | 0 | 2023-01-01 | 2023-10-22 |
| BA-4005A/B | H2S | Labviewer | Diaria | `BA4005A/B H2S` | solo el día (sin hora) | 39 | 0 | 2023-01-02 | 2023-10-09 |
| BA-4005A/B | NH3 | Labviewer | Diaria | `BA4005A/B NH3` | solo el día (sin hora) | 37 | 0 | 2023-01-05 | 2023-10-05 |
| BA-4005A/B | RSH | Labviewer | Diaria | `BA4005A/B RSH` | solo el día (sin hora) | 39 | 0 | 2023-01-02 | 2023-10-09 |
| BA-4005A/B | SS | Labviewer | Diaria | `BA4005A/B SS` | solo el día (sin hora) | 283 | 0 | 2023-01-01 | 2023-10-22 |
| BA-4005C/D | G&A | Labviewer | Diaria | `BA4005C/D G&A` | solo el día (sin hora) | 807 | 0 | 2023-01-02 | 2026-04-20 |
| BA-4005C/D | H2S | Labviewer | Diaria | `BA4005C/D H2S` | solo el día (sin hora) | 2 | 0 | 2026-02-08 | 2026-03-22 |
| BA-4005C/D | Hierro | Labviewer | Diaria | `BA4005C/D FE` | solo el día (sin hora) | 57 | 0 | 2023-01-07 | 2026-03-21 |
| BA-4005C/D | NH3 | Labviewer | — | `BA4005C/D NH3` | solo el día (sin hora) | 0 | 0 | — | — |
| BA-4005C/D | RSH | Labviewer | Diaria | `BA4005C/D RSH` | solo el día (sin hora) | 2 | 0 | 2026-02-08 | 2026-03-22 |
| BA-4005C/D | SS | Labviewer | Diaria | `BA4005C/D SS` | solo el día (sin hora) | 818 | 0 | 2023-01-02 | 2026-04-20 |
| BA-4010 | DQO | Labviewer | Diaria | `BA4010 DQO` | solo el día (sin hora) | 36 | 0 | 2023-01-05 | 2023-10-12 |
| BA-4010 | Fenoles | Labviewer | Diaria | `BA4010 Fenol` | solo el día (sin hora) | 48 | 0 | 2023-01-02 | 2023-10-16 |
| BA-4010 | G&A | Labviewer | Diaria | `BA4010 G&A` | solo el día (sin hora) | 282 | 0 | 2023-01-01 | 2023-10-23 |
| BA-4010 | H2S | Labviewer | Diaria | `BA4010 H2S` | solo el día (sin hora) | 43 | 0 | 2023-01-02 | 2023-10-23 |
| BA-4010 | NH3 | Labviewer | Diaria | `BA4010 NH3` | solo el día (sin hora) | 59 | 0 | 2023-01-02 | 2023-10-12 |
| BA-4010 | RSH | Labviewer | Diaria | `BA4010 RSH` | solo el día (sin hora) | 43 | 0 | 2023-01-02 | 2023-10-23 |
| BA-4010 | SS | Labviewer | Diaria | `BA4010 SS` | solo el día (sin hora) | 282 | 0 | 2023-01-01 | 2023-10-23 |
| BA-4010 | ST | Labviewer | Diaria | `BA4010 ST` | solo el día (sin hora) | 280 | 0 | 2023-01-01 | 2023-10-12 |
| BA-4010 vertimiento | Cd | Labviewer | Diaria | `BA-4010 CADMIO ` | solo el día (sin hora) | 172 | 0 | 2023-01-02 | 2026-10-12 |
| BA-4010 vertimiento | Cloruros | Labviewer | Diaria | `BA4010 CL` | solo el día (sin hora) | 165 | 0 | 2023-01-02 | 2026-10-12 |
| BA-4010 vertimiento | Conductividad | Labviewer | Diaria | `BA4010  CONDUCTIVIDAD`; `Columna4` | solo el día (sin hora) | 53 | 0 | 2023-04-10 | 2026-10-12 |
| BA-4010 vertimiento | Cr | Labviewer | Diaria | `BA-4010 CROMO ` | solo el día (sin hora) | 172 | 0 | 2023-01-02 | 2026-10-12 |
| BA-4010 vertimiento | Cu | Labviewer | Diaria | `BA-4010 COBRE ` | solo el día (sin hora) | 172 | 0 | 2023-01-02 | 2026-10-12 |
| BA-4010 vertimiento | DBO | Labviewer | Diaria | `BA-4010 DBO` | solo el día (sin hora) | 229 | 0 | 2023-01-04 | 2026-10-07 |
| BA-4010 vertimiento | DQO | Labviewer | Diaria | `BA-4010 DQO` | solo el día (sin hora) | 292 | 0 | 2023-01-02 | 2026-10-13 |
| BA-4010 vertimiento | Fenoles | Labviewer | Diaria | `BA4010 Fenol ` | solo el día (sin hora) | 351 | 0 | 2023-01-01 | 2026-10-12 |
| BA-4010 vertimiento | G&A | Labviewer | Diaria | `BA4010 G&A ` | solo el día (sin hora) | 552 | 0 | 2023-01-01 | 2026-10-12 |
| BA-4010 vertimiento | H2S | Labviewer | Diaria | `BA4010 H2S ` | solo el día (sin hora) | 181 | 0 | 2023-01-01 | 2026-10-11 |
| BA-4010 vertimiento | Hierro | Labviewer | Diaria | `BA-4010 FE` | solo el día (sin hora) | 172 | 0 | 2023-01-02 | 2026-10-12 |
| BA-4010 vertimiento | N total | Labviewer | Diaria | `BA-4010 NITROGENO TOTAL` | solo el día (sin hora) | 182 | 0 | 2023-01-04 | 2026-10-07 |
| BA-4010 vertimiento | NH3 | Labviewer | — | `BA4010 NH3 ` | solo el día (sin hora) | 0 | 0 | — | — |
| BA-4010 vertimiento | Ni | Labviewer | Diaria | `BA-4010 NIQUEL` | solo el día (sin hora) | 172 | 0 | 2023-01-02 | 2026-10-12 |
| BA-4010 vertimiento | P total | Labviewer | — | `BA-4010 FOSFORO TOTAL` | solo el día (sin hora) | 0 | 0 | — | — |
| BA-4010 vertimiento | Pb | Labviewer | Diaria | `BA-4010 PLOMO` | solo el día (sin hora) | 172 | 0 | 2023-01-02 | 2026-10-12 |
| BA-4010 vertimiento | RSH | Labviewer | Diaria | `BA4010 RSH ` | solo el día (sin hora) | 181 | 0 | 2023-01-01 | 2026-10-11 |
| BA-4010 vertimiento | S en aguas | Labviewer | Diaria | `BA-4010  S` | solo el día (sin hora) | 178 | 0 | 2023-01-02 | 2026-10-12 |
| BA-4010 vertimiento | SS | Labviewer | Diaria | `BA4010 SS ` | solo el día (sin hora) | 544 | 0 | 2023-01-01 | 2026-10-12 |
| BA-4010 vertimiento | Se | Labviewer | Diaria | `BA-4010 SELENIO` | solo el día (sin hora) | 171 | 0 | 2023-01-02 | 2026-10-12 |
| BA-4010 vertimiento | Sulfatos | Labviewer | Diaria | `BA-4010  SULFATO` | solo el día (sin hora) | 175 | 0 | 2023-01-02 | 2026-10-12 |
| BA-4010 vertimiento | Temperatura | Labviewer | Diaria | `BA-4010  T°` | solo el día (sin hora) | 1 | 0 | 2023-04-10 | 2023-04-10 |
| BA-4010 vertimiento | V | Labviewer | Diaria | `BA-4010 VANADIO` | solo el día (sin hora) | 171 | 0 | 2023-01-02 | 2026-10-12 |
| BA-4010 vertimiento | Zn | Labviewer | Diaria | `BA-4010 ZINC` | solo el día (sin hora) | 171 | 0 | 2023-01-02 | 2026-10-12 |
| BA-4010 vertimiento | pH | Labviewer | Diaria | `BA-4010 Ph` | solo el día (sin hora) | 3 | 0 | 2026-07-29 | 2026-08-03 |
| BA-4055 | Cd | Labviewer | Diaria | `BA-4055 CADMIO` | solo el día (sin hora) | 176 | 0 | 2023-01-02 | 2026-10-05 |
| BA-4055 | Cloruros | Labviewer | Diaria | `BA-4055 CL` | solo el día (sin hora) | 164 | 0 | 2023-01-02 | 2026-10-05 |
| BA-4055 | Cr | Labviewer | Diaria | `BA-4055 CROMO` | solo el día (sin hora) | 176 | 0 | 2023-01-02 | 2026-10-05 |
| BA-4055 | Cu | Labviewer | Diaria | `BA-4055 COBRE` | solo el día (sin hora) | 176 | 0 | 2023-01-02 | 2026-10-05 |
| BA-4055 | DBO | Labviewer | Diaria | `BA-4055 DBO` | solo el día (sin hora) | 200 | 0 | 2023-01-04 | 2026-10-07 |
| BA-4055 | DQO | Labviewer | Diaria | `BA-4055 DQO` | solo el día (sin hora) | 263 | 0 | 2023-01-06 | 2026-10-13 |
| BA-4055 | Fenoles | Labviewer | Diaria | `BA-4055Fenol` | solo el día (sin hora) | 228 | 0 | 2023-01-01 | 2026-10-07 |
| BA-4055 | G&A | Labviewer | Diaria | `BA-4055 G&A` | solo el día (sin hora) | 572 | 0 | 2023-01-02 | 2026-10-12 |
| BA-4055 | H2S | Labviewer | Diaria | `BA-4055 H2S` | solo el día (sin hora) | 176 | 0 | 2023-01-01 | 2026-10-11 |
| BA-4055 | Hierro | Labviewer | Diaria | `BA-4055 FE` | solo el día (sin hora) | 176 | 0 | 2023-01-02 | 2026-10-05 |
| BA-4055 | N total | Labviewer | Diaria | `BA-4055 NITROGENO TOTAL` | solo el día (sin hora) | 185 | 0 | 2023-01-04 | 2026-09-30 |
| BA-4055 | NH3 | Labviewer | Diaria | `BA-4055NH3` | solo el día (sin hora) | 1 | 0 | 2023-04-10 | 2023-04-10 |
| BA-4055 | Ni | Labviewer | Diaria | `BA-4055 NIQUEL` | solo el día (sin hora) | 176 | 0 | 2023-01-02 | 2026-10-05 |
| BA-4055 | P total | Labviewer | — | `BA-4055 FOSFORO TOTAL` | solo el día (sin hora) | 0 | 0 | — | — |
| BA-4055 | Pb | Labviewer | Diaria | `BA-4055PLOMO` | solo el día (sin hora) | 176 | 0 | 2023-01-02 | 2026-10-05 |
| BA-4055 | RSH | Labviewer | Diaria | `BA-4055 RSH` | solo el día (sin hora) | 179 | 0 | 2023-01-01 | 2026-10-11 |
| BA-4055 | S en aguas | Labviewer | Diaria | `BA-4055 S` | solo el día (sin hora) | 173 | 0 | 2023-01-02 | 2026-10-05 |
| BA-4055 | SS | Labviewer | Diaria | `BA-4055 SS` | solo el día (sin hora) | 550 | 0 | 2023-01-01 | 2026-10-12 |
| BA-4055 | Se | Labviewer | Diaria | `BA-4055 SELENIO` | solo el día (sin hora) | 175 | 0 | 2023-01-02 | 2026-10-05 |
| BA-4055 | Sulfatos | Labviewer | Diaria | `BA-4055  SULFATO` | solo el día (sin hora) | 174 | 0 | 2023-01-02 | 2026-10-05 |
| BA-4055 | Temperatura | Labviewer | — | `BA-4055 T°` | solo el día (sin hora) | 0 | 0 | — | — |
| BA-4055 | V | Labviewer | Diaria | `BA-4055 VANADIO` | solo el día (sin hora) | 176 | 0 | 2023-01-02 | 2026-10-05 |
| BA-4055 | Zn | Labviewer | Diaria | `BA-4055 ZINC` | solo el día (sin hora) | 176 | 0 | 2023-01-02 | 2026-10-05 |
| BA-4055 | pH | Labviewer | Diaria | `BA-4055 Ph` | solo el día (sin hora) | 2 | 2 | 2025-08-20 | 2025-10-29 |
| BA-4005A | Flujo | Por confirmar | Diaria | `ClarifiA Flujo` | solo el día (sin hora) | 1.304 | 0 | 2023-01-01 | 2026-10-13 |
| BA-4005B | Flujo | Por confirmar | Diaria | `ClarifiB Flujo` | solo el día (sin hora) | 1.304 | 0 | 2023-01-01 | 2026-10-13 |
| BA-4005C | Flujo | Por confirmar | Diaria | `ClarifiC Flujo` | solo el día (sin hora) | 1.283 | 0 | 2023-01-01 | 2026-10-13 |
| BA-4005D | Flujo | Por confirmar | Diaria | `ClarifiD Flujo` | solo el día (sin hora) | 1.283 | 0 | 2023-01-01 | 2026-10-13 |
| D-1170 | H2S | Labviewer | — | `D1170 H2S` | solo el día (sin hora) | 0 | 0 | — | — |
| D-1170 | NH3 | Labviewer | — | `D1170 NH3` | solo el día (sin hora) | 0 | 0 | — | — |
| D-1170 | RSH | Labviewer | — | `D1170 RSH` | solo el día (sin hora) | 0 | 0 | — | — |
| D-1170 | pH | Labviewer | — | `D1170 pH` | solo el día (sin hora) | 0 | 0 | — | — |
| D-305 | H2S | Labviewer | — | `D305 H2S` | solo el día (sin hora) | 0 | 0 | — | — |
| D-305 | NH3 | Labviewer | — | `D305 NH3` | solo el día (sin hora) | 0 | 0 | — | — |
| D-305 | RSH | Labviewer | — | `D305 RSH` | solo el día (sin hora) | 0 | 0 | — | — |
| D-305 | pH | Labviewer | — | `D305 pH` | solo el día (sin hora) | 0 | 0 | — | — |
| D-307 | H2S | Labviewer | — | `D307 H2S` | solo el día (sin hora) | 0 | 0 | — | — |
| D-307 | NH3 | Labviewer | — | `D307 NH3` | solo el día (sin hora) | 0 | 0 | — | — |
| D-307 | RSH | Labviewer | — | `D307 RSH` | solo el día (sin hora) | 0 | 0 | — | — |
| D-307 | pH | Labviewer | — | `D307 pH` | solo el día (sin hora) | 0 | 0 | — | — |
| D-4206 | H2S | Labviewer | — | `D4206 H2S` | solo el día (sin hora) | 0 | 0 | — | — |
| D-4206 | NH3 | Labviewer | — | `D4206 NH3` | solo el día (sin hora) | 0 | 0 | — | — |
| D-4206 | RSH | Labviewer | — | `D4206 RSH` | solo el día (sin hora) | 0 | 0 | — | — |
| D-4206 | pH | Labviewer | — | `D4206 pH` | solo el día (sin hora) | 0 | 0 | — | — |
| D-503 | H2S | Labviewer | — | `D503 H2S` | solo el día (sin hora) | 0 | 0 | — | — |
| D-503 | NH3 | Labviewer | — | `D503 NH3` | solo el día (sin hora) | 0 | 0 | — | — |
| D-503 | RSH | Labviewer | — | `D503 RSH` | solo el día (sin hora) | 0 | 0 | — | — |
| D-503 | pH | Labviewer | — | `D503 pH` | solo el día (sin hora) | 0 | 0 | — | — |
| D-554 | H2S | Labviewer | — | `D554 H2S` | solo el día (sin hora) | 0 | 0 | — | — |
| D-554 | NH3 | Labviewer | — | `D554 NH3` | solo el día (sin hora) | 0 | 0 | — | — |
| D-554 | RSH | Labviewer | — | `D554 RSH` | solo el día (sin hora) | 0 | 0 | — | — |
| D-554 | pH | Labviewer | — | `D554 pH` | solo el día (sin hora) | 0 | 0 | — | — |
| DIAPAC efluente | DQO | Labviewer | Diaria | `DIAPAC DQO` | solo el día (sin hora) | 89 | 0 | 2023-10-28 | 2026-10-08 |
| DIAPAC efluente | G&A | Labviewer | Diaria | `DIAPAC G&A` | solo el día (sin hora) | 193 | 0 | 2023-11-02 | 2026-10-10 |
| DIAPAC efluente | SS | Labviewer | Diaria | `DIAPAC SS` | solo el día (sin hora) | 194 | 0 | 2023-11-02 | 2026-10-10 |
| DIAPAC efluente | ST | Labviewer | Diaria | `DIAPAC ST` | solo el día (sin hora) | 2 | 0 | 2026-04-30 | 2026-06-11 |
| DNF entrada | G&A | Labviewer | Diaria | `DNF ENTRADA G&A` | solo el día (sin hora) | 67 | 0 | 2023-07-05 | 2023-10-13 |
| DNF entrada | SS | Labviewer | Diaria | `DNF ENTRADA SS` | solo el día (sin hora) | 66 | 0 | 2023-07-05 | 2023-10-12 |
| DNF salida | G&A | Labviewer | Diaria | `DNF SALIDA G&A` | solo el día (sin hora) | 67 | 0 | 2023-07-05 | 2023-10-13 |
| DNF salida | SS | Labviewer | Diaria | `DNF SALIDA SS` | solo el día (sin hora) | 66 | 0 | 2023-07-05 | 2023-10-12 |
| Piscina pulmón | Nivel | Por confirmar | Diaria | `Ppulmon Nivel` | solo el día (sin hora) | 92 | 0 | 2023-01-04 | 2023-04-15 |
| Piscina pulmón | pH | Labviewer | Diaria | `Ppulmon pH` | solo el día (sin hora) | 92 | 0 | 2023-01-04 | 2023-04-15 |
| Recirculación | Flujo | Por confirmar | Diaria | `Flujo Entrega Recirculacion` | solo el día (sin hora) | 1.000 | 0 | 2023-09-28 | 2026-10-13 |
| T-2590 entrada | Flujo | Por confirmar | Diaria | `T2590IN Flujo` | solo el día (sin hora) | 5 | 0 | 2023-01-05 | 2023-02-04 |
| T-2590 entrada | H2S | Labviewer | — | `T2590IN H2S` | solo el día (sin hora) | 0 | 0 | — | — |
| T-2590 entrada | NH3 | Labviewer | — | `T2590IN NH3` | solo el día (sin hora) | 0 | 0 | — | — |
| T-2590 entrada | RSH | Labviewer | — | `T2590IN RSH` | solo el día (sin hora) | 0 | 0 | — | — |
| T-2590 entrada | pH | Labviewer | — | `T2590IN pH` | solo el día (sin hora) | 0 | 0 | — | — |
| T-2590 salida | Flujo | Por confirmar | Diaria | `T2590OUT Flujo` | solo el día (sin hora) | 5 | 0 | 2023-01-05 | 2023-02-04 |
| T-2590 salida | H2S | Labviewer | — | `T2590OUT H2S` | solo el día (sin hora) | 0 | 0 | — | — |
| T-2590 salida | NH3 | Labviewer | — | `T2590OUT NH3` | solo el día (sin hora) | 0 | 0 | — | — |
| T-2590 salida | RSH | Labviewer | — | `T2590OUT RSH` | solo el día (sin hora) | 0 | 0 | — | — |
| T-2590 salida | pH | Labviewer | — | `T2590OUT pH` | solo el día (sin hora) | 0 | 0 | — | — |
| T-308 entrada | H2S | Labviewer | — | `T308IN H2S` | solo el día (sin hora) | 0 | 0 | — | — |
| T-308 entrada | NH3 | Labviewer | — | `T308IN NH3` | solo el día (sin hora) | 0 | 0 | — | — |
| T-308 entrada | RSH | Labviewer | — | `T308IN RSH` | solo el día (sin hora) | 0 | 0 | — | — |
| T-308 entrada | pH | Labviewer | — | `T308IN pH` | solo el día (sin hora) | 0 | 0 | — | — |
| T-308 salida | H2S | Labviewer | — | `T308OUT H2S` | solo el día (sin hora) | 0 | 0 | — | — |
| T-308 salida | NH3 | Labviewer | — | `T308OUT NH3` | solo el día (sin hora) | 0 | 0 | — | — |
| T-308 salida | RSH | Labviewer | — | `T308OUT RSH` | solo el día (sin hora) | 0 | 0 | — | — |
| T-308 salida | pH | Labviewer | — | `T308OUT pH` | solo el día (sin hora) | 0 | 0 | — | — |
| T-4841 entrada | Flujo | Por confirmar | Diaria | `T4841IN Flujo` | solo el día (sin hora) | 5 | 0 | 2023-01-05 | 2023-02-04 |
| T-4841 entrada | H2S | Labviewer | — | `T4841IN H2S` | solo el día (sin hora) | 0 | 0 | — | — |
| T-4841 entrada | NH3 | Labviewer | — | `T4841IN NH3` | solo el día (sin hora) | 0 | 0 | — | — |
| T-4841 entrada | RSH | Labviewer | — | `T4841IN RSH` | solo el día (sin hora) | 0 | 0 | — | — |
| T-4841 entrada | pH | Labviewer | — | `T4841IN pH` | solo el día (sin hora) | 0 | 0 | — | — |
| T-4841 salida | Flujo | Por confirmar | Diaria | `T4841OUT Flujo` | solo el día (sin hora) | 5 | 0 | 2023-01-05 | 2023-02-04 |
| T-4841 salida | H2S | Labviewer | — | `T4841OUT H2S` | solo el día (sin hora) | 0 | 0 | — | — |
| T-4841 salida | NH3 | Labviewer | — | `T4841OUT NH3` | solo el día (sin hora) | 0 | 0 | — | — |
| T-4841 salida | RSH | Labviewer | — | `T4841OUT RSH` | solo el día (sin hora) | 0 | 0 | — | — |
| T-4841 salida | pH | Labviewer | — | `T4841OUT pH` | solo el día (sin hora) | 0 | 0 | — | — |

Columna de fecha: `Fecha`.

Columnas que **no** se importan:

- `TOTAL FLUJO CLARIFICADORES`: Suma de los cuatro clarificadores (fórmula).
- `Raspador Falla`: Texto, no es una medición.
- `Observaciones`: Texto, no es una medición.
- `Afluente no conforme`: Texto, no es una medición.
- `BA4005C/D Temp`: Columna sin valores.
- `Columna1`: Columna vacía.
- `Columna2`: Columna vacía.
- `Acido Carga H2S`: No se sabe qué mide (4 valores de enero de 2023); decidido no importarla.
- `Acido H2SO4`: No se sabe qué mide (4 valores de enero de 2023); decidido no importarla.
- `Acido Carga`: No se sabe qué mide (4 valores de enero de 2023); decidido no importarla.
- `Tea 1`: No se sabe qué mide (4 valores de enero de 2023); decidido no importarla.
- `Tea 2`: No se sabe qué mide (4 valores de enero de 2023); decidido no importarla.
- `Tea 3`: No se sabe qué mide (4 valores de enero de 2023); decidido no importarla.
- `Tea 4`: No se sabe qué mide (4 valores de enero de 2023); decidido no importarla.
- `Tea 6`: No se sabe qué mide (4 valores de enero de 2023); decidido no importarla.
- `Tea 7`: No se sabe qué mide (4 valores de enero de 2023); decidido no importarla.
- `Suma Teas`: Suma de las teas.
- `Columna3`: Fórmula rota (#REF!).
- `Frac Verti`: Fórmula rota (#REF!).
- `Fra Reuso`: Fórmula rota (#REF!).
- `% remo G&A`: Fórmula (% de remoción).
- `% remo SS`: Fórmula (% de remoción).
- `%Remo G&A 05A/B`: Fórmula (% de remoción).
- `%Remo SS 05A/B`: Fórmula (% de remoción).
- `%Remo G&A 05C/D`: Fórmula (% de remoción).
- `%Remo SS 05C/D`: Fórmula (% de remoción).
- `Carga Total`: Fórmula (carga total).

## 4. Variables sin tabla de Excel

Ninguna: todas las variables del catálogo salen de una tabla de Excel.

Mediciones capturadas a mano en la app (no vienen de Excel): 0.
