# Dashboard PTAR — Requisitos y lineamientos

> Documento vivo. Cuando una decisión cambie, se actualiza aquí primero.
> Última actualización: 2026-10-26. Hay decisiones abiertas (§15); lo que dependa de ellas está marcado como **pendiente**.

## 1. Contexto y objetivo

La PTAR de la Refinería de Barrancabermeja (Ecopetrol) trata las aguas aceitosas de toda la refinería. Actualmente se siguen sus parámetros de calidad y de operación en dos libros de Excel que varias personas editan todos los días:

- **Tabla de referencia 1** ("Tabla aliado química con Gráficas"): hoja «Entrada de Datos», una fila por hora desde junio de 2022. La llena el tablerista con lo que reporta Ecolab (antes Nalco).
- **Tabla de referencia 2** ("SEGUIMIENTO UT DESCONTAMINACIÓN NUEVO.xlsx"): datos diarios del laboratorio central (Labviewer), análisis de BIOTA (Fase I, BR-4081), separadores y agua agria, sodas gastadas, DIAPAC y Ecodiesel, más tablas dinámicas y gráficas.

Problemas de hoy (ver los números en §16):
- Es fácil escribir mal un dato y nada lo impide: pH de 73, temperaturas de 4900 °C, "7,,4", "asdfdf".
- Fechas duplicadas o fuera de orden, fórmulas rotas (`#DIV/0!`, `#REF!`) y columnas que cambian de lugar con el tiempo.
- Hacer gráficas y estadística descriptiva exige armar tablas dinámicas a mano.
- No queda registro de quién escribió o cambió cada dato.

**Objetivo:** reunir en una sola plataforma web los datos de calidad y de operación de la PTAR que hoy llegan por separado del laboratorio central (Labviewer), de BIOTA y Ecolab. Guardarlos en un formato único, validarlos en el momento en que se ingresan y automatizar su captura donde sea posible, para que los ingenieros puedan vigilar las variables críticas y analizar tendencias sin depender de hojas de cálculo editadas a mano.

**Beneficios esperados:**
- Datos limpios: lo imposible se rechaza al escribirlo, no se descubre en una gráfica.
- Una sola fuente de verdad, con el historial de quién registró o corrigió cada dato.
- Gráficas y estadística al momento, sin tablas dinámicas.
- Comparar fuentes y puntos de la misma variable. Por ejemplo, el fenol de BIOTA contra el del laboratorio, o el fenol en la entrada, el biorreactor y la salida.
- Respaldo continuo y exportaciones periódicas para los ingenieros.

## 2. Fuentes de datos y puntos de muestreo

**Principio:** una misma variable puede medirse con varias fuentes y en varios puntos del proceso. Todas se guardan y se pueden comparar; ninguna fuente reemplaza a otra.

**La fuente es quien midió, no quien escribió el dato.** Un análisis de BIOTA que digita el tablerista sigue siendo de BIOTA; quién lo digitó queda aparte, en el historial.

| Fuente | Qué mide | Cómo llega hoy | Frecuencia |
|---|---|---|---|
| **Labviewer** (laboratorio central) | Análisis de laboratorio de muchos puntos: BA-4001, BA-4010, BA-4055, DIAPAC, aguas agrias, metales, DBO, DQO… | Alguien los pasa de Labviewer a «Datos LABORATORIO». Consultar la base de Labviewer directamente es una meta posterior | Diaria, sin hora |
| **BIOTA** (aliado del tratamiento biológico) | BA-4001, entrada a BA-4009A, BA-4008, BA-4009A, BA-4080, BR-4081, BA-4010, bombas RAS y WAS; DIAPAC (afluente y cámaras A y B), Ecodiesel, separadores y agua agria, y sodas gastadas | Envía los análisis día a día; se transcriben al Excel. Formato por confirmar | 7 a. m. y 4 p. m. |
| **Ecolab** (aliado químico; antes Nalco) | BA-4001, BA-4005C/D, DNF, BA-4030A–D, CL-4080 | Registra en su propio sistema y le reporta al tablerista, que llena «Entrada de Datos» | Cada pocas horas |
| **PI** (DCS Siemens y Foxboro) | Variables de proceso, entre ellas los flujos de BA4005C/D (confirmado) | Hoy se transcriben a mano en «Entrada de Datos». La lectura automática desde PI es de una fase posterior | Cada hora en el Excel |
| Por confirmar | Los flujos y niveles del histórico de «Datos LABORATORIO» (recirculación, T-2590, T-4841, piscina pulmón y los clarificadores A y B) | «Datos LABORATORIO» | Diaria |

**Puntos de muestreo** (catálogo inicial; la agrupación es una propuesta que el administrador ajusta):

| Zona | Puntos |
|---|---|
| Entrada a la PTAR | BA-4001 (los ingenieros lo llaman "01") |
| Tratamiento primario | BA-4002, BA-4005A/B, BA-4005C/D, los clarificadores BA-4005A, BA-4005B, BA-4005C y BA-4005D, DNF (entrada y salida), BA-4030A–D |
| Tratamiento secundario | CL-4080 (entrada y salida) |
| Fase I (biológico) | BA-4055 (carga de Fase I), entrada a BA-4009A, BA-4008 ("08", biorreactor), BA-4009A, BA-4080 (salida, con datos hasta junio de 2025), BR-4081, bombas RAS MP-4051A/B/C y WAS MP-4042A/B/C |
| Vertimiento | BA-4010 ("10", vertedero, salida al río) y «BA-4010 vertimiento» (el bloque «BA-4010 CLARIFICADA» de Labviewer; pendiente: ¿son dos puntos? §15) |
| Corrientes de llegada | Separadores SE-3010, SE-3020, SE-3030, SE-3050, SE-3060; agua agria; sodas K-4090, K-4091, K-4092, K-4094, D-4006; DIAPAC (afluente, cámaras A y B); Ecodiesel; aguas agrias T-2590, T-4841, D-1170, D-305, D-307, T-308, D-503, D-554, D-4206 |

**Parámetros** (catálogo inicial): temperatura, pH, fenoles, SST, sólidos sedimentables (SSED), grasas y aceites (G&A), sólidos totales, DQO, DQO soluble, DBO5, nitrógeno total, N-NH3, fósforo total, sulfuros, H2S, RSH (mercaptanos), sulfatos, cloruros, conductividad, turbidez, hierro y otros metales (Cd, Cu, Cr, Ni, Pb, Se, V, Zn), oxígeno disuelto, recuento microbiológico (ufc/mL), índice volumétrico de lodos (IVL), relación alimento/microorganismos (F/M), flujo, nivel y tiempo de retención.

Las equivalencias entre nombres de fuentes distintas están pendientes (§15). Por ejemplo, "SS" de Labviewer y "SST" de BIOTA.

## 3. Alcance

### Versión 1
- Catálogos: fuentes, zonas, puntos de muestreo, parámetros, variables (punto + parámetro + fuente) y límites.
- Usuarios con roles y ámbitos de captura.
- Importación del histórico, una sola vez:
  - de la tabla 1, «Entrada de Datos»;
  - de la tabla 2, las hojas «Datos LABORATORIO», «FASE I», «A.AGRIAS SEP.», «K-SODAS», «BR 4081», «DIAPAC» y «ECODIESEL».
- Vista de **variables importantes** (§7.1).
- **Explorador de series** con estadística descriptiva (§7.2).
- **Gráficas del ICAV:** las gráficas semanales del informe, de lunes a domingo (§7.3).
- **Captura manual** validada, por formatos (§6). Al inicio todas las entradas son manuales.
- Historial de cambios de cada medición.
- Respaldo continuo y exportación a Excel (§10).

### Fuera de alcance en v1 (fases posteriores)
- **Análisis semanal automático** (la calificación del ICAV, §8). Sus reglas están por definir. Las gráficas del ICAV sí están en la versión 1 (§7.3).
- Consulta directa de la base de Labviewer.
- Lectura automática desde PI, empezando por los flujos de BA4005C/D.
- Carga desde archivos y otros formatos (por ejemplo, los que envía BIOTA).
- Reporte diario de Fase I (hoja «Datos Calidad Fase 1»).
- Alertas: por límite y por muestras faltantes según el programa de muestras (hoja «Programa Muestras»).
- Indicadores calculados: % de remoción, carga total, F/M, IVL. En el Excel sus fórmulas están rotas; la app los calculará a partir de las mediciones.

El modelo de datos debe permitir añadir estas fases sin rehacerlo.

**Hojas que no se migran:**
- Las tablas dinámicas y las gráficas (pH, G&A, SST, °T, NTU, Fe, Graficas, GyA, Solidos, Nitrógeno, Fenol, Fenol AA, Sulfatos PTAR, Sulfatos SEP, Aguas Agrias): las reemplazan las vistas de la app. Las de «Graficas» de la tabla 2 son las del ICAV (§7.3).
- «Hoja4» y «Rangos ICAV»: son un ejemplo antiguo que ya no funciona; sus reglas y sus valores **no se toman como referencia**.
- «Radios»: fuera de alcance.

La hoja de límites de la tabla 1 (§16), «Datos Calidad Fase 1» y «Programa Muestras» sirven de insumo para los catálogos de límites y para las fases posteriores.

## 4. Usuarios, roles y autenticación

- Login con **usuario y contraseña** propios de la app, sin correo corporativo ni SSO.
- **Sin autorregistro:** el administrador crea las cuentas y restablece contraseñas. En el primer ingreso se obliga a cambiar la contraseña.
- Contraseñas con hash seguro (argon2).
- **Bloqueo de la cuenta tras 10 intentos fallidos consecutivos, durante 10 minutos**, por usuario y no por IP (`django-axes`). El administrador puede desbloquearla antes.
- **Una cuenta por persona, nunca compartida.** Por ejemplo, no hay una cuenta "tablerista" para los cuatro tableristas: el historial tiene que decir quién registró cada dato.
- Las personas se desactivan, **nunca se borran**, para conservar el historial.

**Roles** (tres):

| Rol | Lectura (vistas y gráficas) | Captura | Además |
|---|---|---|---|
| Administrador | Todo | Todo, sin límite de tiempo | Gestiona usuarios, roles, ámbitos, catálogos, rangos, límites y formatos de captura; corrige y borra cualquier dato; **es el único que ve Exportaciones** |
| Ingeniero | Todo | Solo en sus ámbitos (puede no tener ninguno: entonces es de solo lectura) | Corrige los datos de sus ámbitos de las últimas 48 horas, con historial |
| Capturista | **Ninguna** | Solo en sus ámbitos | Pensado para personal de los laboratorios |

- **Ámbito de captura:** los formatos de captura (§6) que un usuario puede llenar. Los asigna el administrador.
- **Una persona nueva es capturista** hasta que el administrador le asigne otro rol: por defecto, el rol con menos permisos.
- **Exportaciones es solo del administrador** (decidido el 2026-11-09). Los ingenieros siguen descargando en Excel lo que ven en el Explorador y en ICAV, y todas las gráficas como imagen.
- **El capturista no tiene acceso de lectura:** no ve vistas, gráficas, exportaciones ni datos de otros ámbitos. Al entrar va directo a Captura.
  - En sus formatos sí ve lo ya registrado para la fecha que elige, para no duplicar ni pisar datos.
  - Puede corregir o borrar **sus propias capturas de las últimas 48 horas**, solo en su ámbito. Lo demás lo ve, pero no lo cambia.
  - Puede llenar una celda vacía **solo si la muestra es de las últimas 48 horas** (por su fecha y hora). Más atrás, la celda queda de solo lectura; lo que falte de antes lo llena el administrador, el único sin límite de tiempo (decidido el 2026-11-09; antes eran 24 horas para corregir y no había límite para llenar).
- **Corrigen:** el ingeniero, cualquier dato de sus formatos registrado en las últimas 48 horas, y llena celdas vacías de muestras de las últimas 48 horas, como el capturista; el administrador, cualquier dato, sin límite de tiempo. Siempre con historial. (Hasta el 2026-11-09 el ingeniero no tenía límite.)
- **Quién captura:**
  - Al inicio, mientras todos se acostumbran a la herramienta, solo los **4 tableristas** ingresan datos, de todas las fuentes, como hoy: tienen asignados todos los formatos.
  - Los tableristas **tienen lectura**: su rol es Ingeniero, con todos los formatos.
  - Lo ideal es que después cada laboratorio ingrese los suyos, con sus propios usuarios de capturista. Se decidirá en el camino, porque requiere ponerse de acuerdo entre varios equipos. El modelo sirve igual para las dos formas.
- Cuando se adopte, la usarán **unas 10 a 20 personas**.
- Los permisos se verifican **en el servidor**, en cada vista.

## 5. Modelo de datos

Nombres de ejemplo en inglés para el código; la interfaz va en español.

- **User** (Usuario): modelo de usuario propio (`AUTH_USER_MODEL`) desde el inicio. Campos:
  - `username`, `full_name`, `is_active`;
  - `role` (administrador, ingeniero o capturista);
  - sus formatos de captura (M2M con `CaptureForm`).
- **Source** (Fuente): `code`, `name`, `description`. Labviewer, BIOTA, Ecolab, PI y las que se identifiquen.
- **ProcessArea** (Zona): `name`, `order`.
- **SamplingPoint** (Punto de muestreo): `code` canónico ("BA-4010"), `name` ("Vertedero, salida al río"), `area` (opcional), `order`, `is_active`, y alias para la importación ("BA4010", "BA 4010", "VERTEDERO BA4010"). Un alias pertenece a un solo punto.
- **Parameter** (Parámetro): `code`, `name`, `unit`, `decimals`, `is_active` y el **rango físico opcional** (`physical_min`, `physical_max`). Si está definido, lo que queda fuera de él es imposible y se rechaza; por ejemplo, un pH fuera de 0 a 14.
- **Variable**: punto + parámetro + fuente, única. Es lo que se captura, se importa y se grafica. Además tiene:
  - el **rango habitual opcional** (`typical_min`, `typical_max`): si está definido, fuera de él se pide confirmar. Si el parámetro tiene rango físico, el habitual debe quedar dentro de él;
  - la `time_resolution` (cada hora, 7 a. m. y 4 p. m., a. m. y p. m., diaria o eventual): define las celdas que tiene en la captura;
- **Measurement** (Medición):
  - `variable` y `taken_at` (fecha y hora de la muestra, hora de Bogotá).
  - `time_precision` (precisión de la hora): hora exacta, a. m., p. m. o solo el día. **No se inventan horas:** si la fuente solo da el día (Labviewer), se guarda el día; si solo dice "a. m." o "p. m." («A.AGRIAS SEP.»), se guarda eso. En esos casos `taken_at` es el inicio del periodo (00:00 para el día y la mañana, 12:00 para la tarde) y la interfaz muestra la fecha con "a. m.", "p. m." o sin hora. **Excepción, BIOTA** (decidido el 2026-11-09): BIOTA toma sus muestras a las 7 a. m. y, cuando las hay, a las 4 p. m., así que sus valores de "solo el día" y de "a. m." se guardan a las 07:00 y los de "p. m." a las 16:00.
  - `value`: siempre un número.
  - `qualifier` (calificador): vacío, `<` o `>`. "< 0,1" quiere decir que el valor está por debajo de 0,1, normalmente el límite de detección del laboratorio. `value` guarda el número que acompaña al signo.
  - **No hay estados.** ND, FS, SB, NA y similares significan que no se tiene un valor, y **un dato que no hay (NaN) no se guarda:** no hay fila.
  - `suspect` (dudoso): solo para valores del histórico fuera del rango físico (§9).
  - `origin`: captura manual, importación del histórico y, en fases posteriores, archivo o PI.
  - `created_by`, `created_at`, `updated_by`, `updated_at`.
  - **Única por (`variable`, `taken_at`):** no hay dos valores para la misma muestra. Volver a capturarla la corrige, con historial.
- **MeasurementHistory** (Historial): cada creación, corrección o borrado de una medición. Guarda la variable, la fecha y hora, el valor antes → después (vacío al crear o al borrar), quién, cuándo y un motivo opcional. **El historial nunca se borra**, así que borrar una medición no hace perder nada. Solo lectura. Excepción mientras la plataforma se construye (decidido el 2026-11-09): el usuario puede pedir borrar del todo datos repetidos o de prueba, con su historial. Cuando la plataforma entre en uso, la regla no tiene excepciones.
- **Limit** (Límite): `point`, `parameter`, `kind` (límite de vertimiento, máximo de diseño en la entrada, ventana operativa u otro), `min`, `max`, `valid_from`, `valid_to` y `reference` (de dónde sale). Aplica a todas las fuentes del par punto-parámetro. Cada muestra se evalúa con el límite vigente en su fecha. Dos límites del mismo tipo para el mismo punto y parámetro no pueden tener vigencias que se crucen: cuando un límite cambia, se le pone fecha de fin al anterior y se crea uno nuevo.
- **CaptureForm** (Formato de captura): `name`, `source`, `schedule` (cada hora, 7 a. m. y 4 p. m., diaria o eventual) y la lista ordenada de variables que lo componen. Cada variable puede llevar una sección (por ejemplo, «Fase I», «DIAPAC», «Ecodiesel», «Aguas agrias a los separadores» y «Sodas gastadas» en el formato «BIOTA»): la rejilla muestra las secciones una debajo de otra y, dentro de cada una, las variables de un mismo punto juntas. Se configura en el admin: añadir un punto o un parámetro no requiere programar.
- **ImportBatch** (Lote de importación): archivo, hoja y tabla, fecha, quién lo corrió, si fue en seco, conteos e informe. La creación de cada medición importada queda en el historial con su lote.
- **AuditEntry** (Registro de auditoría): cambios en usuarios, catálogos, rangos y límites. Solo lectura en el admin.

**Volumen:** unas 635.000 mediciones históricas (438.000 de la tabla 1 y 197.000 de la tabla 2) y menos de 300.000 nuevas al año. SQLite lo maneja sin problema.

## 6. Captura de datos

**Al inicio todas las entradas son manuales.** La consulta de Labviewer, la lectura de PI y la carga desde archivos llegarán en fases posteriores.

**Formatos de captura iniciales**, uno por cada hoja de hoy. Un formato reúne las variables de una fuente. Al inicio los tableristas tienen asignados todos los formatos (§4).

| Formato | Fuente | Forma | Hoy |
|---|---|---|---|
| Ecolab | Ecolab | Rejilla por hora: filas = las 24 horas del día elegido, columnas = punto × parámetro | «Entrada de Datos» |
| Flujos de carga | PI | Igual que Ecolab, cada hora: los flujos de los clarificadores BA-4005A a BA-4005D y de la recirculación | «Entrada de Datos» y «Datos LABORATORIO» |
| BIOTA | BIOTA | Cinco secciones, una debajo de otra. **Fase I:** por punto, muestras de 7 a. m. y 4 p. m., y las diarias. **DIAPAC:** afluente, cámara A y cámara B, una celda por día (domingo: afluente y cámaras; martes: cámaras). **Ecodiesel:** eventual, una celda por día. **Aguas agrias a los separadores:** agua agria y SE-3050, diarias; SE-3010, SE-3020, SE-3030 y SE-3060, a. m. y p. m. **Sodas gastadas:** K-4090 a K-4094 y D-4006, eventual | «FASE I», «BR 4081», «DIAPAC», «ECODIESEL», «A.AGRIAS SEP.» y «K-SODAS» |
| Laboratorio central | Labviewer | Diario, por punto | «Datos LABORATORIO» |

- Los flujos de carga se capturan a mano, cada hora, en el formato «Flujos de carga» hasta que se lean desde PI. Es un formato aparte porque un formato reúne variables de una sola fuente, y la de los flujos es PI.
- Los formatos iniciales los crea la app con las variables de cada hoja **que tienen datos desde octubre de 2025** (decidido el 2026-10-20). Las demás siguen en la base y en las vistas; el administrador las agrega a un formato si vuelven a medirse.
- Las celdas de cada variable salen de su frecuencia: cada hora (24 celdas), 7 a. m. y 4 p. m., solo 7 a. m., a. m. y p. m., o una por día (diaria y eventual). En «BIOTA» todo se captura a las 7 a. m.; la columna de 4 p. m. solo aparece para lo que todavía se mide en la tarde (hoy, BR-4081: pH, fenoles y SST). Un formato con variables por hora se muestra con las horas en filas; los demás, con las variables en filas y hasta cinco columnas de tiempo.

**Flujo:** el usuario elige un formato (solo ve los de su ámbito), la fecha y, si aplica, la hora; la app muestra las celdas de ese formato.
- **Cada celda se guarda sola al salir de ella** y muestra que quedó guardada. Si no pasa la validación, el error se muestra en la celda y no se guarda.
- Una celda vacía es un dato que no hay: no se guarda nada. Si el reporte dice ND, FS, SB o algo parecido, la celda se deja vacía.
- Si el laboratorio reporta "ND" en el sentido de "no detectado" y da el límite de detección, se escribe "<" con ese límite (por ejemplo, "<0,1"). Si no da el límite, la celda se deja vacía.
- Se llena con el teclado como en Excel: Tab y Enter para avanzar (Enter baja, Mayúsculas + Enter sube y Escape deshace lo escrito en la celda).
- La celda con el foco muestra abajo la variable, sus rangos, quién la registró y cuándo, y su historial.

**Validación en cada celda** (en el navegador para avisar al momento y en el servidor, que es el que decide):
- Solo números, opcionalmente con "<" o ">" delante. Valen la coma y el punto decimal ("7,4", "7.4", "<0,1", "> 500"); "7,,4", "7/4", "19+", "ND" o "asdfdf" no.
- **Rango físico** del parámetro, si está definido: fuera de él se rechaza (pH 73, SST negativo).
- **Rango habitual** de la variable, si está definido: fuera de él la app pide confirmar ("4 °C en BA-4001 está fuera del rango habitual. ¿Confirmas?").
- **Los rangos son opcionales.** La herramienta funciona sin ellos y se pueden ir definiendo con el uso; sin rango, basta con que el valor sea un número.
- Fecha y hora con selector; no se aceptan fechas futuras.
- No hay fórmulas en la captura: los cálculos los hace la app.

**Correcciones:** corregir o borrar un valor deja en el historial el valor anterior, quién lo cambió, cuándo y, si lo escribe, el motivo.
- Cambiar o vaciar una celda que ya tenía valor pide confirmar, con un campo para el motivo (opcional): así no se pisa un dato sin querer.
- Si otra persona cambió la celda mientras tanto, no se guarda: la app avisa y muestra el valor nuevo.
- Corregir un valor dudoso del histórico (§9) le quita la marca de dudoso, porque el valor nuevo pasa la validación.

## 7. Vistas

Gráficas con ECharts, como el dashboard U044.

### 7.1 Variables importantes (primera vista)

**pH, grasas y aceites (G&A), sólidos suspendidos totales, fenoles, DQO y temperatura**, en ese orden (decidido el 2026-11-09). Para cada una:
- Gráfica de los valores recientes (por defecto los últimos 30 días; se puede cambiar), con la línea del límite que aplique. En el pH, el límite es una ventana y se muestran las dos líneas, la mínima y la máxima.
- **Valor actual:** el último registrado, con su fecha, hora y fuente.
- **Máximo y mínimo de los últimos 7 días.**
- **Promedio de los últimos 7 días y de los últimos 30 días.**
- Los promedios son el promedio aritmético de las mediciones de la ventana, calculado por serie (punto + fuente).
- **Valores con calificador:** en la gráfica llevan un marcador propio. En la estadística cuentan como el peor caso: "<0,1" como 0,1 y ">500" como 500.
- **Fenoles:** **BA-4001 (01, entrada), BA-4008 (08, biorreactor) y BA-4010 (10, salida) en la misma gráfica**, cada punto con su color; además, «BA-4010 vertimiento» de Labviewer (desde el 2026-11-09).
- **Fuentes:** cada tarjeta muestra las series que se escogieron, cada una de un punto y una fuente. El color distingue el punto y la forma del marcador distingue la fuente. La fuente oficial para el cumplimiento se escogerá después.
- Los datos que no hay dejan un hueco en la gráfica. Los dudosos del histórico (§9) no se grafican ni entran en la estadística hasta que alguien los revise.
- **Series de cada tarjeta:** se configuran en la administración (Vistas → Variables importantes): un título y la lista de variables (punto + parámetro + fuente), en orden. Pueden ser de varios parámetros con la misma unidad (por ejemplo, SST de Ecolab y SS de Labviewer en «Sólidos suspendidos totales»), **hasta 8 puntos por gráfica**, uno por color: con más colores las series ya no se distinguen. Para comparar otras series está el explorador. (Hasta el 2026-11-09 cada tarjeta era un parámetro en unos puntos, con todas sus fuentes; no permitía quitar una fuente de un punto.)
- **Configuración del 2026-11-09** (se ajusta en la administración):
  - **pH:** Ecolab en BA-4001, BA-4005C, BA-4005D y CL-4080 salida.
  - **Grasas y aceites:** Labviewer en BA-4001 y BA-4010 vertimiento; Ecolab en BA-4005C, BA-4005D y CL-4080 salida.
  - **Sólidos suspendidos totales:** SST de Ecolab en BA-4001, BA-4005C, BA-4005D y CL-4080 salida; SS de Labviewer en BA-4001 y BA-4010 vertimiento.
  - **Fenoles:** BIOTA en BA-4001, BA-4008 y BA-4010; Labviewer en BA-4001 y BA-4010 vertimiento.
  - **DQO:** BIOTA en BA-4001, BA-4008 y BA-4010. Sin BA-4080 (sin datos desde junio de 2025), ni la DQO soluble, ni la entrada a BA-4009A; BA-4009A solo tiene DQO soluble.
  - **Temperatura:** Ecolab en BA-4001, BA-4005C, BA-4005D y CL-4080 salida.
  - Ninguna lleva DNF entrada, ni «BA-4010» de Labviewer (el bloque viejo, sin datos desde octubre de 2023).
- **Ventanas:** días calendario de Bogotá que terminan en la fecha «Hasta» (hoy, por defecto; se puede elegir otra para consultar el pasado). Los últimos 7 días al 19 de octubre son del 13 al 19, sin importar la hora, así que una muestra con solo el día cuenta en su día. La gráfica muestra 7, 30, 90 o 365 días; desde 90, con promedios diarios.
- **Fuera de límite, 7 días:** cuántas muestras de los últimos 7 días rompen el límite vigente en su fecha, de las que tienen límite. Sin muestras es «sin datos»; sin límite definido, «sin límite». Además, el último valor se marca si está fuera del límite.
- **Huecos:** la línea se corta cuando una serie pasa más de tres veces su intervalo habitual sin datos (y al menos un día), o cuando falta un día, una semana o un mes de promedios.
- En todas las gráficas se pueden ocultar puntos y fuentes. El eje es siempre lineal: no hay escala logarítmica (decidido el 2026-10-21).
- **Todas las gráficas se descargan como imagen** (PNG), para pegarlas en un informe (decidido el 2026-10-26): con título, unidad, fechas y leyenda, y solo lo que se está viendo (sin los puntos, fuentes o parámetros ocultos; en el explorador, con el acercamiento).

**Dónde se mide hoy cada una:**

| Variable | Límite en BA-4010 | Fuentes y puntos |
|---|---|---|
| Fenoles | 0,2 mg/L | BIOTA: BA-4001, BA-4008, BA-4010 · Labviewer: BA-4001, BA-4010 vertimiento |
| Temperatura | 40 °C (temperatura máxima) | Ecolab: BA-4001, BA-4005C/D, DNF, BA-4030A–D, CL-4080 · BIOTA: BA-4001, BA-4008, BA-4009A, BA-4010 |
| pH | Ventana (pendiente, §15) | Ecolab: BA-4001, BA-4005C/D, DNF, BA-4030A–D, CL-4080 · BIOTA: BA-4001, entrada a BA-4009A, BA-4008, BA-4009A, BR-4081, BA-4010 · Labviewer: casi sin datos (5 valores) |
| SST | 50 mg/L | Ecolab, BIOTA y Labviewer |
| G&A | 15 mg/L | Ecolab, Labviewer y BIOTA (este último en BA-4010 desde junio de 2025) |

### 7.2 Explorador de series
- Elegir uno o varios parámetros, sin máximo, cada uno con sus puntos y fuentes; superponer las series; rango de fechas (decidido el 2026-10-21).
  - Las fechas y el tipo de gráfica se piden una vez y valen para todos los parámetros.
  - Cada parámetro es un bloque: su lista desplegable y, debajo, los puntos y las fuentes que lo miden. «Añadir parámetro» agrega un bloque nuevo sin tocar los que ya están; cada bloque se puede quitar. Un parámetro va en un solo bloque.
  - Hasta 8 puntos por parámetro, por la misma razón que en §7.1. Si no se marca ninguna fuente, se toman todas las de ese parámetro.
  - **Una gráfica por unidad:** los parámetros con la misma unidad comparten gráfica y eje; cada unidad tiene su gráfica y su tabla de estadística, una debajo de otra, con el mismo eje de tiempo. Las gráficas siguen el orden de los bloques.
  - En una gráfica con varios parámetros, el color sigue siendo el punto y la forma la fuente; cada parámetro se distingue por el trazo de la línea (continua, punteada…) y se puede ocultar, como los puntos y las fuentes. Si entre todos los parámetros de la gráfica hay más de 8 puntos, los colores se repiten.
  - Por defecto, los últimos 90 días.
- Estadística descriptiva por serie: número de muestras, promedio, mediana, mínimo, máximo, desviación estándar, percentiles 10 y 90 y % de muestras por encima del límite.
  - Siempre con las mediciones sin agregar. Desviación estándar muestral (DESVEST.M de Excel) y percentiles con interpolación (PERCENTIL.INC).
  - **% fuera de límite:** de las muestras que tienen un límite vigente en su fecha, cuántas lo rompen, sea cual sea el tipo de límite del punto. Un rango (pH) se rompe por los dos lados.
  - Los dudosos no entran; la tabla dice cuántos se dejaron fuera en cada serie.
- Agregación diaria, semanal o mensual para las series largas.
  - Solo cambia lo que dibuja la gráfica. Automática: sin agregar hasta 3 meses, promedios diarios hasta 3 años y semanales para más; se puede elegir otra.
- Exportar a Excel lo que se está viendo, todos los parámetros en el mismo libro: hoja «Estadística», hoja «Mediciones» (formato largo: fecha, hora, punto, parámetro, fuente, calificador, valor, unidad y quién la registró) y, si la gráfica es de promedios, una hoja con ellos. Sin los dudosos.

### 7.3 Gráficas del ICAV
Las gráficas semanales que hoy se arman con las tablas dinámicas de la hoja «Graficas» de la tabla 2 («GyA», «Fenol», «Solidos»…) y se usan en el informe ICAV (decidido el 2026-10-26).
- **Semana de lunes a domingo** (decidido el 2026-10-26). Se elige con cualquier día de la semana; por defecto, la última semana completa (la que terminó el domingo). La semana en curso se puede ver: llega hasta hoy. Hay enlaces a la semana anterior y a la siguiente.
- **Un valor por día y por serie (punto + fuente):** el promedio de las mediciones de ese día, por ejemplo las de 7 a. m. y 4 p. m. de BIOTA. Una muestra con solo el día cuenta en su día.
  - Los valores con calificador cuentan como el peor caso y el promedio que los incluye lleva el marcador vacío.
  - Los dudosos no entran. Un día sin datos deja un hueco.
- **Cada gráfica es una lista de variables** (punto + parámetro + fuente), con título y orden, en la administración (Vistas → Gráficas del ICAV): añadir o quitar una serie no requiere programar.
  - Todas las variables de una gráfica tienen la misma unidad; puede haber varios parámetros, que se distinguen por el trazo, como en el explorador.
  - Hasta 8 puntos por gráfica (§7.1). El color es el punto y la forma, la fuente.
  - Se dibuja el límite vigente de cada punto, si lo hay.
- Debajo de cada gráfica, una tabla con los promedios de cada día y cada serie.
- **Descargas:** cada gráfica como imagen (PNG), como todas las del dashboard (§7.1), y la semana en Excel, con una hoja por gráfica (días en filas, series en columnas).
- **Configuración inicial** (la crea la migración `dashboards/0004`; se ajusta en la administración):

| Gráfica | Series |
|---|---|
| Grasas y aceites | G&A en BA-4001, BA-4055 y BA-4010 vertimiento (Labviewer) y en BA-4010 (BIOTA) |
| Fenoles | BA-4001, BA-4009A, BA-4008 y BA-4010 (BIOTA) y BA-4010 vertimiento (Labviewer) |
| Sólidos suspendidos | SS en BA-4001, BA-4055 y BA-4010 vertimiento (Labviewer) y SST en BA-4010 (BIOTA) |
| Biorreactor BA-4008 (aguas agrias) | N total y N-NH3 en BA-4008 salida (BIOTA) |
| Nitrógeno | N total en BA-4008 entrada, BA-4008 salida, entrada a BA-4009A y BA-4010, y N-NH3 en BA-4008 salida y BA-4010 (BIOTA); N total en BA-4010 vertimiento (Labviewer) |
| Sulfatos de los separadores | SE-3010, SE-3020, SE-3030, SE-3050 y SE-3060 (BIOTA) |
| Sulfatos de la PTAR | entrada a BA-4009A, BA-4008, BA-4009A y BA-4010 (BIOTA) y BA-4010 vertimiento (Labviewer) |
| Fenoles en agua agria | Agua agria (BIOTA) |

  - Las columnas de Labviewer que usan las tablas dinámicas son las del bloque «BA-4010 CLARIFICADA», el punto «BA-4010 vertimiento» (pendiente 5).
  - "SS" de Labviewer y SST de BIOTA van en la misma gráfica como dos parámetros, sin darlos por equivalentes (pendiente 4).
- La calificación de la semana (el índice de «Hoja4» y su radar) no está aquí: sus reglas siguen pendientes (§8, pendiente 11).

## 8. Límites y cumplimiento

- **Fuentes de los límites:** la hoja de límites de la tabla 1 (límites de vertimiento de BA-4010 y máximos de diseño de BA-4001) y las ventanas operativas de «Datos Calidad Fase 1». Son datos con vigencia (§5), no números en el código.
- Valores de las variables importantes:

| Parámetro | BA-4010 (vertimiento) | BA-4001 (máximos) |
|---|---|---|
| Temperatura máxima | 40 °C | 40 °C |
| pH | 6,4–8,5 (pendiente, §15) | 6,4–8,5 (pendiente, §15) |
| SST | 50 mg/L | 470 mg/L |
| Grasas y aceites | 15 mg/L | 1230 mg/L |
| Fenoles | 0,2 mg/L | 55 mg/L |

- Las tablas de referencia no coinciden entre sí en algunos límites; queda pendiente cuál aplica (§15).
- **"Sin datos" nunca es "cumple".** Si en un período no hay mediciones, el resultado es "sin datos".

**Análisis semanal automático (ICAV, fase posterior):** se calculará solo cada semana. Sus reglas se definirán al llegar a esa fase. Las gráficas semanales del informe ya están en la app (§7.3). La hoja «Hoja4» de la tabla 2 (con «Rangos ICAV») es un ejemplo antiguo que ya no funciona y no se toma como referencia.

## 9. Migración del histórico

**Origen:**
- Tabla 1: tabla de Excel `Tabla1` de «Entrada de Datos» (junio de 2022 a octubre de 2026; unos 438.000 valores).
- Tabla 2: tablas de Excel `Laboratorio`, `FASE1`, `FenolAASepSoda4`, `FenolAASepSoda48`, `BR_4081`, `DIAPAC` y `Ecodisel` (unos 197.000 valores).

**Mapeo:**
- Un archivo por hoja, versionado en el repositorio, con una fila por columna de Excel: punto, parámetro, fuente y hora.
- La hora es la de la fila en la tabla 1; 07:00 o 16:00 en las muestras de 7 a. m. y 4 p. m.; y "solo el día" en las diarias. En las hojas de BIOTA («FASE I», «BR 4081», «DIAPAC», «ECODIESEL», «A.AGRIAS SEP.» y «K-SODAS»), las diarias y las de "a. m." van a las 07:00 y las de "p. m." a las 16:00 (decidido el 2026-11-09).
- El mapeo solo contiene encabezados, nunca valores. Las columnas se buscan por su encabezado, no por su posición; un encabezado que no está en el mapeo se reporta.
- No se importan las columnas de fórmulas (% de remoción, carga total, sumas, F/M, IVL) ni las vacías ("Blanco n", "ColumnaN"). Tampoco las celdas con fórmula dentro de columnas de datos (por ejemplo, un `=SUM(...)` pegado en una columna de RSH): no son mediciones.
- **Catálogo inicial:** `import_maps/catalog/` trae las fuentes, zonas, puntos y parámetros (con su rango físico). La importación crea los que falten, sin cambiar los que ya existen, y crea cada variable solo cuando tiene al menos un valor.
- **Fuente provisional «Por confirmar»** para los flujos y niveles de «Datos LABORATORIO» (clarificadores, recirculación, T-2590, T-4841, piscina pulmón). Cuando se sepa la fuente, se cambia en el admin la fuente de esas variables, sin reimportar. Los flujos de BA4005C/D de la tabla 1 son de PI.
- **Nombres sin equivalencia decidida** (§15, pendiente 4) se importan como parámetros aparte: "SS", "NH3", "H2S", "RSH", "S en aguas" y "DBO" de Labviewer no se mezclan con SST, N-NH3, sulfuros ni DBO5. Si después se decide que son lo mismo, basta cambiar el parámetro de esas variables en el admin.
- "BA-4010" y "BA-4010 clarificada" de «Datos LABORATORIO» se importan como dos puntos, «BA-4010» y «BA-4010 vertimiento» (§15, pendiente 5). El 2026-11-09 «BA-4010 clarificada» se renombró «BA-4010 vertimiento» (migración `catalog/0005`); el nombre anterior queda como alias. En «FASE I», "BA4008 ENTRADA" y "BA4008 SALIDA" (nitrógeno) son los puntos «BA-4008 entrada» y «BA-4008 salida».
- No se importan: «Tea 1» a «Tea 7» y el bloque de ácido (no se sabe qué miden; 4 valores cada uno) ni «GYA10» de «DIAPAC» (sin cámara).

**Normalización:**
- **Los valores no numéricos quedan como NaN:** no se importan.
  - Eso incluye los códigos (SB, FS, ND, NA, NR, F/S, Falla), los errores de digitación ("7,,4", "asdfdf") y los errores de fórmula.
  - El informe de la importación los cuenta y los lista, y los Excel originales se conservan como respaldo.
- **Valores con calificador:** "<10" se importa con calificador `<` y valor 10. En el histórico hay 21 casos, todos con "<"; no aparece ninguno con ">".
- Un texto que es un número limpio, como "5.6" guardado como texto, se lee como número.
- **Valores numéricos fuera del rango físico** (pH 73, 4900 °C, SST −332):
  - **nunca se corrigen solos**: se importan marcados como dudosos;
  - no entran en las gráficas ni en la estadística;
  - una persona decide si se corrigen (73 → 7,3) o se borran.
- Las horas corridas (06:59 → 07:00) se redondean a la hora.
- **Fechas mal escritas en la tabla 1** (por ejemplo, "2022-07-12 15:59" entre "2022-07-11 16:00" y "18:00", o filas que avanzan de a un día): la hora se **deduce por la secuencia** solo cuando las filas vecinas la fijan sin duda (entre 16:00 y 18:00 va 17:00; un tramo de n filas entre dos horas separadas n + 1 horas). Cada fecha deducida va al informe. Las filas cuya hora no se puede deducir no se importan y se reportan.
- Las fechas imposibles (años 1900 y 1903) y las futuras no se importan, salvo que la secuencia las deduzca; se reportan.
- **Duplicados:** si la misma variable tiene el mismo valor dos veces para la misma fecha y hora, se importa una vez. Si tiene valores distintos, **no se importa ninguno**: los dos van al informe y una persona captura después el correcto.

**Proceso:**
- Un script idempotente, que se puede correr en seco (`--dry-run`), y un informe de lo que no se pudo mapear, quedó como NaN o quedó dudoso. Volver a correrlo no duplica nada ni cambia lo que ya está en la base: un valor que ya existe con otro número se reporta y no se toca.
- **Se importa en local y se revisa el informe allí.** Después, la base local reemplaza la de producción (decidido el 2026-10-18): se pierde lo que se haya creado en producción, y viaja lo que haya en la base local, también sus usuarios. El procedimiento está en `docs/DESPLIEGUE.md`.
- **Claude (el asistente de desarrollo) revisa uno por uno los valores que no se mapean automáticamente** y propone su mapeo. **Cuando no puede decidir con certeza, consulta al usuario** antes de importar. No se inventan mapeos dudosos.
- Los Excel originales se conservan fuera del repositorio como respaldo.

## 10. Respaldo y exportaciones

- **Respaldo continuo:** Litestream copia cada cambio de la base a un bucket privado de Cloud Storage en aproximadamente un segundo, como en Avante. Se activa el versionado de objetos del bucket. La retención está pendiente (Avante usa 3 días).
- **Respaldos de largo plazo** (decidido el 2026-10-28): copias de la base en la carpeta `respaldos\dashboard_ptar\` del OneDrive de Ecopetrol del administrador, como en Avante. Se hacen solas antes de cada despliegue y a voluntad, con `Descargar respaldos.cmd` de la carpeta `respaldos\`. No hay copias programadas. Se conservan todas. Cada respaldo también descarga a `respaldos\dashboard_ptar\exportaciones\` los archivos semanales que falten.
- **Página Exportaciones:** solo la ve el administrador y solo tiene el archivo semanal (decidido el 2026-11-09). Hasta esa fecha también tenía «Exportar ahora» (un rango de fechas y fuentes, al momento), y la veían los ingenieros; se quitó. Para un rango, está el Excel del Explorador.
- **Exportación automática semanal** (decidido el 2026-10-20): **cada lunes** aparece en Exportaciones un archivo con **todos los datos hasta el domingo**, en dos formas. Se guarda en la carpeta `exports/` del bucket.
  - larga, una hoja por año: una fila por medición, con fecha, hora, punto, parámetro, fuente, calificador, valor, si es dudoso y quién la registró;
  - ancha, por fuente: parecida a las hojas de hoy, para quien quiera seguir trabajando en Excel: una hoja por fuente, una fila por fecha y hora, una columna por punto y parámetro. Sin los dudosos.
  - La app lo prepara sola en segundo plano en cuanto recibe la primera visita después del lunes a las 00:00 (con los tableristas capturando, en minutos). Tarda unos minutos.
  - Se conservan todos; la página muestra los más recientes.
- **SharePoint:** una persona descarga el archivo semanal y lo sube a mano (decidido el 2026-10-20). Automatizar la entrega (Power Automate o Microsoft Graph) queda para después; depende de permisos de TI.
- El procedimiento de restauración se documenta en `docs/DESPLIEGUE.md` y se prueba.

## 11. Stack técnico y despliegue

El mismo de Avante, para mantener una sola forma de trabajar:
- **Backend:** Python 3.14, Django 6, `uv` (`pyproject.toml` y `uv.lock`).
- **Frontend:** plantillas de Django + **HTMX** (servido desde `static/js/`, sin CDN) + **ECharts 5.6.0** servido localmente, la misma versión del dashboard U044. Sin SPA.
- **Base de datos:** SQLite, también en producción, replicada con Litestream.
- **Otras dependencias:** `openpyxl` (importación y exportación), `django-axes`, `argon2-cffi`, `django-environ`, `whitenoise`, `gunicorn`.
- **Estética RefinIA:** los tokens de color y la barra superior de `refinia-portal/static/css/styles.css` (bloque "Barra superior — común a todas las herramientas"), IBM Plex Sans y IBM Plex Sans Condensed, tema claro. Si la barra cambia en el portal, cambia aquí.
- **Despliegue en Google Cloud:**
  - Cloud Run, servicio `dashboard-ptar`, región `us-east1`, proyecto `project-76e49327-2ee1-47c7-861` (el mismo de RefinIA y Avante).
  - **Una sola instancia** con **CPU siempre asignada**, porque la base vive dentro del contenedor. Por la misma razón, las migraciones y el primer administrador se ejecutan al arrancar el contenedor.
  - Cloud Build y Artifact Registry construyen y guardan la imagen; Secret Manager guarda `SECRET_KEY`.
  - Scripts en `scripts/gcp/` y guía en `docs/DESPLIEGUE.md`.
- **Dirección:** https://refinia-ptar.web.app, con su tarjeta en `refinia-portal`. Es un sitio de Firebase Hosting (`refinia-ptar`) que reenvía a Cloud Run, como las otras herramientas; la dirección de `run.app` sigue funcionando. **Ojo:**
  - Firebase Hosting solo deja pasar a Cloud Run la cookie llamada `__session`. Las otras herramientas usan la contraseña de nginx, que no depende de cookies; esta app usa login con sesión.
  - Por eso, detrás de Firebase hay que usar `SESSION_COOKIE_NAME = "__session"` y `CSRF_USE_SESSIONS = True`, y responder con `Cache-Control: private`.
  - Firebase además corta las peticiones de más de 60 segundos, así que las exportaciones grandes se preparan en segundo plano.
- **Zona horaria** `America/Bogota`; interfaz en español (`LANGUAGE_CODE = "es"`).
- **Configuración** por variables de entorno. Ningún secreto en el repositorio.

## 12. Seguridad

- HTTPS obligatorio; cookies `Secure` y `HttpOnly`; `DEBUG = False` en producción.
- Bloqueo de la cuenta tras 10 intentos fallidos consecutivos, durante 10 minutos.
- Los permisos se verifican en el servidor en cada vista. Aunque manipule la URL, un capturista no puede leer nada y nadie puede capturar fuera de su ámbito.
- **Los datos de la planta nunca van al repositorio.** `.gitignore` excluye los Excel, los CSV (salvo los mapeos de importación, que solo tienen encabezados) y las exportaciones.
- El archivo semanal solo lo descarga el administrador, y el Excel del Explorador y de ICAV, los usuarios con lectura; no hay URLs públicas.
- Cada medición guarda su historial de cambios, que nunca se borra.

## 13. Experiencia de usuario

- **Capturar debe ser más rápido que en Excel:** teclado (Tab y Enter), encabezados fijos y celdas que muestran al momento si quedaron guardadas o por qué no.
- Interfaz en español. Los números se muestran con coma decimal; al capturar se acepta coma o punto.
- Menú: **Variables importantes**, **Explorador**, **ICAV**, **Exportaciones** (solo para el administrador), **Captura** (solo para quien tenga ámbitos) y **Administración** (solo para el administrador). El capturista solo ve **Captura**.
- Las vistas de lectura deben poder usarse desde el celular.

## 14. Fases de desarrollo

| Fase | Contenido | Criterio de "listo" |
|---|---|---|
| 0 | Proyecto base, usuario propio con roles y ámbitos, login con bloqueo, catálogos, rangos y límites en el admin, estética RefinIA, despliegue mínimo con Litestream | El administrador crea usuarios y catálogos; un capturista entra y solo ve Captura |
| 1 | Importación del histórico de las dos tablas, con informe y revisión | El histórico completo está en la base y el informe está revisado |
| 2 | Variables importantes y explorador de series con estadística | El fenol en 01, 08 y 10 y las otras cuatro variables se consultan sin Excel |
| 3 | Captura manual validada por formatos, historial de cambios y exportación a Excel (a demanda y periódica) | Los tableristas dejan de llenar el Excel |
| 4 | Gráficas semanales del ICAV, de lunes a domingo | Las gráficas del informe ICAV se sacan de la app, sin tablas dinámicas |
| Al entrar en uso | **Quitar la importación desde Excel** (`apps/imports`, `import_maps/` y el comando `import_history`): desde ese momento los datos solo entran por la captura. Con ella desaparece el nombre «Nalco», que solo queda en los mapeos para leer el Excel histórico (decidido el 2026-11-09) | La app no tiene importación desde Excel ni ninguna mención a Nalco |
| Luego | Análisis semanal automático (calificación del ICAV), consulta de Labviewer, lectura de PI, carga desde archivos, reporte diario de Fase I, alertas, indicadores calculados | — |

La importación va antes que las vistas porque una vista sin datos no sirve, y porque es la mejor prueba del modelo de datos.

Cada fase se entrega funcionando y con pruebas. Prioridad de las pruebas:
- **Validación:** números con coma o punto, calificadores, rangos definidos y rangos ausentes.
- **Permisos:** capturista sin lectura y ámbitos de captura.
- **Estadística:** ventanas de 7 y 30 días, calificadores, huecos y dudosos.
- **Importación:** mapeo, NaN, calificadores, dudosos e idempotencia.

## 15. Decisiones

### Decidido el 2026-10-14
- **Valores no numéricos del histórico:** quedan como NaN (no se importan), salvo los que llevan "<" o ">", que se importan con su calificador.
- **Calificador sí, estado no:**
  - una medición puede llevar "<" o ">" delante del número, como ya aparece en los registros;
  - no hay estados: ND, FS, SB y similares significan que no se tiene un valor, y simplemente no se registra.
- **Calificador en la estadística:** cuenta como el peor caso ("<0,1" como 0,1 y ">500" como 500). En la gráfica, esos valores llevan un marcador distinto.
- **Valores imposibles del histórico** (pH 73, 4900 °C): se importan marcados como dudosos, fuera de las gráficas y de la estadística, hasta que una persona decida si se corrigen o se borran.
- **Rangos opcionales:** la herramienta debe operar sin tenerlos todos definidos.
- **Fuentes en la vista:** se muestran todas; la oficial se escoge después.
- **Variables importantes:** fenoles, temperatura, pH, SST y G&A. El SSED no va en la vista. (Desde el 2026-11-09: pH, G&A, sólidos suspendidos totales, fenoles, DQO y temperatura, §7.1.)
- **Promedios:** de los últimos 7 y de los últimos 30 días.
- **Fenol:** la vista muestra solo 01, 08 y 10.
- **Quién captura:** al inicio, solo los 4 tableristas, todas las fuentes. Lo ideal es que después capture cada laboratorio; se define en el camino.
- **Usuarios:** unos 10 a 20 cuando se adopte.
- **Entrada:** manual al inicio. La consulta de la base de Labviewer es una meta posterior.
- **PI:** los flujos están en PI. Su lectura automática es posterior.
- **«Hoja4»** y sus rangos son un ejemplo antiguo: no se toman como referencia.
- **Repositorio:** https://github.com/srada3001/dashboard_PTAR. Los archivos de referencia no van al repositorio.

### Decidido el 2026-10-17
- **Dirección:** https://refinia-ptar.web.app, por Firebase Hosting, como las otras herramientas de RefinIA (§11). La de `run.app` sigue funcionando.

### Decidido el 2026-10-18 (importación del histórico, §9)
- **Hora a. m. / p. m.:** se guarda como "a. m." o "p. m.", sin suponer una hora. Por eso la medición tiene una precisión de la hora (exacta, a. m., p. m. o solo el día) en lugar de "hora conocida sí/no".
- **Fechas mal escritas en «Entrada de Datos»:** se deducen por la secuencia cuando las vecinas las fijan sin duda; las demás no se importan.
- **Duplicados con valores distintos:** no se importa ninguno; van al informe.
- **Fuente de separadores y agua agria, sodas, DIAPAC, Ecodiesel y de los flujos de «Datos LABORATORIO»:** provisional, «Por confirmar» (pendiente 7). DIAPAC, Ecodiesel, separadores y agua agria, y sodas se decidieron el 2026-11-09: son de BIOTA.
- **BA4008 ENTRADA y SALIDA:** dos puntos nuevos, «BA-4008 entrada» y «BA-4008 salida».
- **«Flujo Entrega Recirculacion»:** punto «Recirculación». **«GYA10»**, teas y ácido: no se importan.
- **"DBO" de Labviewer:** parámetro aparte, sin asumir que es DBO5.
- **Producción:** la base local, con el histórico importado y revisado, reemplaza la de producción.

### Decidido el 2026-10-20 (captura y exportaciones, §4, §6 y §10)
- **Tableristas:** tienen lectura (rol Ingeniero, con todos los formatos).
- **Capturista:** ve lo ya registrado en sus formatos y corrige o borra sus propias capturas de las últimas 24 horas, solo en su ámbito. (Desde el 2026-11-09, 48 horas, §4.)
- **Columnas sin datos recientes:** los formatos iniciales solo traen variables con datos desde octubre de 2025.
- **Rejilla de Ecolab (antes Nalco):** las 24 horas del día elegido.
- **Flujos de BA-4005C/D:** en un formato aparte, «Flujos de PI» (desde el 2026-11-09, «Flujos de carga»).
- **Exportación automática:** semanal; cada lunes, un archivo con todos los datos hasta el domingo, para descargar en la app. Una persona lo sube a SharePoint a mano.

### Decidido el 2026-10-26 (gráficas del ICAV, §7.3)
- **Gráficas del ICAV:** una pestaña con las 8 gráficas semanales de la hoja «Graficas» de la tabla 2, configurables en la administración.
- **Semana:** de lunes a domingo.
- La calificación de la semana sigue pendiente (pendiente 11).
- **Imagen de las gráficas:** todas las gráficas del dashboard se descargan como PNG, no solo las del ICAV (§7.1).

### Decidido el 2026-11-09 (BA-4010 vertimiento, DIAPAC, Ecodiesel, el formato de BIOTA, los flujos de carga y el historial durante la construcción, §3, §5 y §6)
- **Historial durante la construcción:** mientras la plataforma se construye, el usuario puede pedir borrar del todo datos repetidos o de prueba, también de su historial. Cuando la plataforma entre en uso, el historial nunca se borra.
- **DIAPAC es de BIOTA.** Sus variables pasan de «Por confirmar» a BIOTA, con sus mediciones (migración `catalog/0007`).
- **Formato «BIOTA»:** el formato «BIOTA Fase I» se llama «BIOTA» y tiene dos secciones: «Fase I» (lo que ya tenía) y, debajo, «DIAPAC». El formato «DIAPAC» desaparece; quien lo tenía asignado recibe «BIOTA».
- **48 horas para capturistas e ingenieros:** el capturista corrige o borra sus propias capturas de las últimas 48 horas (antes 24); el ingeniero, cualquier captura de sus formatos de las últimas 48 horas (antes sin límite). Los dos llenan celdas vacías solo de muestras de las últimas 48 horas. **Solo el administrador** corrige, borra o llena datos más antiguos, incluido el histórico importado y los dudosos (§4).
- **Exportaciones:** solo el archivo semanal, y solo para el administrador. Se quitó «Exportar ahora» (§10).
- **Nalco ahora es Ecolab.** La fuente y el formato de captura se llaman «Ecolab» (migración `catalog/0014`), con sus variables y mediciones. La importación sigue leyendo el Excel de Nalco: `import_maps/Tabla1.csv` dice «Nalco» y la importación lo entiende como Ecolab.
- **Importación desde Excel:** se quita cuando la plataforma entre en uso (§14). Con ella desaparece el nombre «Nalco».
- **Horas de BIOTA:** BIOTA muestrea en la mañana, a las 7 a. m.; antes también a las 4 p. m. (la tarde se dejó de medir el 2026-07-04, salvo en BR-4081). La columna «Día» de BIOTA no era un promedio ni una copia de la mañana: eran otros parámetros que se analizan una vez al día (G&A, sulfatos, nitrógeno, hierro, recuento, fósforo) y las hojas eventuales. Por eso:
  - en la captura, BIOTA tiene solo la columna de 7 a. m., y la de 4 p. m. para las variables con datos de la tarde desde septiembre de 2026 (hoy, pH, fenoles y SST de BR-4081). No hay columnas «Día», «a. m.» ni «p. m.»;
  - en el histórico, los valores de BIOTA de "solo el día" y de "a. m." pasan a las 07:00, y los de "p. m." a las 16:00, sin cambiar la fecha (migración `catalog/0013`). El historial de cada valor se mueve con él. Así una celda de 7 a. m. de un día pasado muestra el valor que ya existe y no se escribe otro;
  - las variables de BIOTA quedan con la frecuencia «7 a. m.», salvo las que siguen con 4 p. m.
- **Separadores y agua agria, y sodas gastadas, también son de BIOTA.** Sus variables (agua agria, SE-3010 a SE-3060, K-4090 a K-4094 y D-4006) pasan a BIOTA, con sus mediciones, y van como dos secciones más del formato «BIOTA», debajo de Ecodiesel: «Aguas agrias a los separadores» y «Sodas gastadas». Sus dos formatos desaparecen; quien los tenía recibe «BIOTA» (migración `catalog/0011`). La rejilla mantiene las variables en filas aunque tenga cinco columnas de tiempo (7:00, 16:00, a. m., p. m. y día); solo un formato con variables por hora pone las horas en filas.
- **Clarificadores A–D = BA-4005A a BA-4005D.** «Clarificador A» a «Clarificador D» de «Datos LABORATORIO» son los mismos equipos: A y B pasan a llamarse BA-4005A y BA-4005B, y C y D se unen a los puntos BA-4005C y BA-4005D que ya existían (los nombres anteriores quedan como alias). Migración `catalog/0009`.
- **Formato «Flujos de carga»**, cada hora, de PI: los flujos de BA-4005A a BA-4005D y de la recirculación. Reemplaza a «Flujos de PI» (que tenía los de C y D) y a «Flujos y niveles del laboratorio» (que era diario), porque son los mismos flujos: el valor diario de «Datos LABORATORIO» es el promedio de los valores por hora de PI (en C y D, igual al 2 % en el 85 % y el 77 % de los días). Quien tenía alguno de los dos recibe «Flujos de carga».
- **Un solo flujo en el histórico:** donde un clarificador tiene los dos (el diario de «Datos LABORATORIO» y el de PI por hora), se queda solo el más completo, el de PI por hora. El otro se borra del todo, con su historial, porque son datos repetidos y la plataforma todavía se construye (migración `catalog/0010`); sus columnas («ClarifiC Flujo» y «ClarifiD Flujo») ya no se importan. Hoy pasa en BA-4005C y BA-4005D. En BA-4005A, BA-4005B y la recirculación solo hay el diario, con la fuente «Por confirmar».
- **Ecodiesel también es de BIOTA.** Sus variables pasan a BIOTA, con sus mediciones, y van en una tercera sección del formato «BIOTA», «Ecodiesel», debajo de DIAPAC. El formato «Ecodiesel» desaparece; quien lo tenía asignado recibe «BIOTA» (migración `catalog/0008`).
- **Cámaras de DIAPAC:** las cinco variables de cada cámara (SSED, SST, recuento, DQO y G&A) van juntas bajo su cámara, sin separar las del domingo de las del martes.

1. ~~**Tableristas**~~: decidido el 2026-10-20.
2. ~~**Capturista**~~: decidido el 2026-10-20.
3. **BIOTA:** ¿en qué formato envía sus análisis?
4. **Equivalencias de nombres:** ¿"SS" (Labviewer) es SST? ¿Cómo se relacionan H2S y RSH (Labviewer) con sulfuros (BIOTA)? ¿Qué es "S en aguas"?
5. **"BA-4010" y "BA-4010 clarificada"** de «Datos LABORATORIO» (en la app, «BA-4010» y «BA-4010 vertimiento»):
   - el mismo día tienen valores distintos (por ejemplo, G&A de 12 y 4,4 el 1 de enero de 2023);
   - "BA-4010" no tiene datos desde octubre de 2023;
   - ¿son dos puntos? ¿Cuál es el vertimiento?
6. **Límites que no coinciden:**
   - Ventana de pH: 6,4–8,5 en la hoja de límites de la tabla 1 y 6,5–8,5 en «Datos Calidad Fase 1». Es la que se dibuja en la vista de pH.
   - Entrada: los máximos de BA-4001 (40 °C, SST 470, fenol 55) contra «Datos Calidad Fase 1» (menos de 44 °C, SST menor de 600, fenol menor de 40).
7. **Fuente** de los flujos y niveles de «Datos LABORATORIO» (recirculación, T-2590, T-4841, piscina pulmón y el histórico diario de los clarificadores A y B). Mientras tanto, «Por confirmar». (DIAPAC, Ecodiesel, separadores y agua agria, y sodas: decidido el 2026-11-09, son de BIOTA.)
8. ~~**Columnas casi vacías**~~: decidido el 2026-10-20 (no entran en los formatos iniciales).
9. **Respaldo:** la exportación semanal y la entrega a SharePoint se decidieron el 2026-10-20; falta la retención de Litestream (hoy 3 días, como Avante).
10. **Nombre** de la app.
11. **Reglas del análisis semanal (ICAV):** se definen al llegar a esa fase. Las gráficas ya están (§7.3); falta cómo se califica la semana.

## 16. Archivos de referencia

Están fuera del repositorio, en `C:\Users\srada\Desktop\referencia_ptar\`.

| Archivo | Contenido |
|---|---|
| `tabla_referencia_1.xlsx` | "Tabla aliado química con Gráficas". «Entrada de Datos» (tabla `Tabla1`, A7:AW38434), «Resolución 0631», «Programa Muestras», «Datos Calidad Fase 1», «Radios» y tablas dinámicas ocultas |
| `tabla_referencia_2.xlsx` | "mine"; en realidad "SEGUIMIENTO UT DESCONTAMINACIÓN NUEVO.xlsx" (así lo nombran sus conexiones de Power Pivot). Hojas «Datos LABORATORIO» a «ECODIESEL» (§9), hojas de resumen, y «Hoja4» y «Rangos ICAV» (ejemplo antiguo, no es referencia) |

### Hallazgos de calidad de los datos (2026-10-08)

Justifican las validaciones de §6 y sirven de casos de prueba para la importación.

- **Unos 200 valores físicamente imposibles** en «Entrada de Datos»: pH de 73, 42 o 674 (se perdió el decimal); temperaturas de 4900, 4000 y 543 °C; un SST de −332. También en «FASE I» (pH 84, 398 °C) y en «A.AGRIAS SEP.» (pH 74).
- **Unos 900 textos en celdas numéricas** en «Entrada de Datos»:
  - códigos: SB ×642, FS ×176, ND, NA, F/S y Falla;
  - errores de digitación: "7,,4", "6,8/", "19+", "asdfdf" y "1522+C9104:C9128";
  - fechas que Excel convirtió por su cuenta, dentro de celdas de pH y de SST.
- **Fechas:**
  - «Entrada de Datos»: 56 fechas y horas duplicadas, 18 fuera de orden, horas corridas a :59 (de arrastrar) y una fecha de 1903. Hay filas creadas por adelantado hasta el 20 de octubre de 2026.
  - «K-SODAS»: una fecha de 1900 y 6 duplicadas. «DIAPAC»: 5 duplicadas. Otras hojas: 1 o 2.
- **Fórmulas rotas:** unas 3.300 celdas con `#DIV/0!`, `#REF!` o `#VALUE!` en «Datos LABORATORIO» (% de remoción, carga total) y 415 `#REF!` en el F/M de «FASE I».
- **Valores bajo el límite de detección como texto:** solo 21, todos "<10", y solo en una parte de cada columna; ninguna columna los usa siempre y no hay ningún ">".
  - Nitrógeno total de BIOTA en BA-4080 y BA-4010: 10 días cada uno, los mismos (17 al 27 de noviembre de 2022, salvo el 24). El resto de esas columnas son números, incluidos unos 300 valores por debajo de 10 (3,2; 4,6…).
  - DQO de SE-3010 (a. m.): un solo día, el 13 de diciembre de 2022.
- **«DIAPAC»:** columnas repetidas con sufijos ("SOL SED2", "SST 3", "DQO5", "GYA9") porque hay dos cámaras y dos días de muestreo.
- **Columnas casi vacías:** BA4002 (un solo valor), teas y ácido (4 valores en enero de 2023).
