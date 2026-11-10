# Lo que está por confirmar

Resumen de las decisiones abiertas de [REQUISITOS.md §15](REQUISITOS.md), con lo que hace la app mientras tanto. Los números son los de la lista de pendientes de §15. La lista que vale es la de REQUISITOS.md: cuando se decida algo, se actualiza primero allá y después aquí.

Ninguno de estos pendientes impide usar la app. Mientras no se decidan, la app no supone nada: guarda los datos por separado y deja el cambio para el admin.

## Sobre los datos

### 3. Formato de BIOTA
**Pregunta:** ¿en qué formato envía BIOTA sus análisis?

**Mientras tanto:** los tableristas los digitan a mano en el formato «BIOTA» (sección «Fase I»), como hoy en el Excel.

**Qué cambia al decidirlo:** con el formato se puede planear la carga desde archivo en una fase posterior.

### 4. Equivalencias de nombres
**Preguntas:**
- ¿"SS" de Labviewer es lo mismo que SST?
- ¿Cómo se relacionan H2S y RSH (Labviewer) con los sulfuros de BIOTA?
- ¿Qué es "S en aguas"?
- (También "NH3" frente a N-NH3 y "DBO" frente a DBO5.)

**Mientras tanto:** cada nombre es un parámetro aparte y no se mezcla con los otros. "DBO" de Labviewer no se da por DBO5.

**Qué cambia al decidirlo:** si son lo mismo, se cambia el parámetro de esas variables en el admin, sin reimportar. A partir de ahí se comparan en la misma gráfica.

### 5. «BA-4010» y «BA-4010 clarificada»
En la app, «BA-4010 clarificada» se llama «BA-4010 vertimiento» desde el 2026-11-09.

**Datos:** las dos columnas vienen de «Datos LABORATORIO».
- El mismo día tienen valores distintos (G&A de 12 y 4,4 el 1 de enero de 2023).
- «BA-4010» no tiene datos desde octubre de 2023.

**Preguntas:** ¿son dos puntos distintos? ¿Cuál de los dos es el vertimiento?

**Mientras tanto:** se guardan como dos puntos.

**Qué cambia al decidirlo:** cuál se compara con los límites de vertimiento y cuál se muestra en «Variables importantes».

### 7. Fuente de los flujos y niveles de «Datos LABORATORIO»
**Pregunta:** ¿quién mide estos datos?
- los flujos y niveles de «Datos LABORATORIO»: clarificadores A–D, recirculación, T-2590, T-4841 y piscina pulmón. Los de los clarificadores son el promedio diario de PI; desde el 2026-11-09 se capturan cada hora en «Flujos de carga» (PI), y del histórico se queda solo el flujo más completo: en C y D, el de PI por hora (el diario se borró del todo y ya no se importa); en A y B, el diario con «Por confirmar».

DIAPAC, Ecodiesel, separadores y agua agria («A.AGRIAS SEP.») y sodas gastadas («K-SODAS») se decidieron el 2026-11-09: son de BIOTA.

**Mientras tanto:** llevan la fuente provisional «Por confirmar». Ya ningún formato de **Captura** la usa: son solo datos del histórico.

**Qué cambia al decidirlo:** se cambia la fuente de esas variables en el admin, sin reimportar.

El detalle está en [FUENTES_POR_CONFIRMAR.md](FUENTES_POR_CONFIRMAR.md).

## Sobre los límites

### 6. Límites que no coinciden
Las dos tablas de referencia dan valores distintos.

| Qué | Hoja de límites (tabla 1) | «Datos Calidad Fase 1» |
|---|---|---|
| Ventana de pH | 6,4–8,5 | 6,5–8,5 |
| Temperatura máxima en BA-4001 | 40 °C | menos de 44 °C |
| SST máximo en BA-4001 | 470 mg/L | menor de 600 mg/L |
| Fenol máximo en BA-4001 | 55 mg/L | menor de 40 mg/L |

**Pregunta:** ¿cuál aplica en cada caso?

**Mientras tanto:** REQUISITOS.md usa los de la hoja de límites de la tabla 1, y la ventana de 6,4–8,5 es la que se dibuja en la vista de pH.

**Qué cambia al decidirlo:** el administrador carga el límite que aplique, con su vigencia. Los límites son datos, así que no hay que programar nada.

### 11. Reglas del análisis semanal (ICAV)
**Pregunta:** ¿cómo se califica cada semana?

**Mientras tanto:** la pestaña **ICAV** ya muestra las gráficas semanales del informe, de lunes a domingo (REQUISITOS.md §7.3), pero no califica la semana. «Hoja4» y «Rangos ICAV» de la tabla 2 no sirven de referencia.

**Cuándo se decide:** al llegar a esa fase.

## Sobre la operación

### 9. Retención del respaldo
**Pregunta:** ¿cuántos días de cambios guarda Litestream en el bucket?

**Mientras tanto:** 3 días, como Avante. La exportación semanal y su entrega a SharePoint ya están decididas.

### 10. Nombre de la app
**Pregunta:** ¿cómo se llama la herramienta?

**Mientras tanto:** «Dashboard PTAR».

## Decididos solo en parte

Están en las decisiones de §15, pero dejan algo para después:

- **Fuente oficial:** hoy se muestran todas las fuentes; cuál es la oficial para cada variable se escoge después.
- **Quién captura:** al inicio, los tableristas capturan todas las fuentes. Lo ideal es que después capture cada laboratorio; se define en el camino.
- **Valores dudosos del histórico** (pH 73, 4900 °C…): están importados, pero fuera de las gráficas y de la estadística. Una persona decide si cada uno se corrige o se borra.
