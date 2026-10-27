# Dashboard PTAR

**Dashboard PTAR** (repositorio `dashboard_PTAR`) es la aplicación web interna que reúne los datos de calidad y de operación de la PTAR de la Refinería de Barrancabermeja (Ecopetrol). Recibe los datos del laboratorio central (Labviewer), de BIOTA y Nalco. Reemplaza los Excel que hoy se editan a mano: valida los datos al ingresarlos, los guarda en un formato único y ofrece vistas de tendencias. Es una herramienta más de RefinIA (`refinia-portal`).

**La especificación completa está en [docs/REQUISITOS.md](docs/REQUISITOS.md). Léela antes de proponer o implementar cualquier cambio de alcance, de modelo de datos o de reglas.** Las decisiones abiertas están en su §15: no las des por resueltas; si una tarea depende de una, pregunta.

## Estado
- Fase 0 hecha y desplegada: proyecto base, usuarios con roles y ámbitos, login con bloqueo, catálogos y límites en el admin con registro de auditoría, estética RefinIA, pantallas por rol.
- Producción: https://dashboard-ptar-248156452075.us-east1.run.app (servicio `dashboard-ptar`). Se despliega a mano con `scripts/gcp/deploy.sh`, como Avante, nunca con cada push: la base vive en el contenedor y un despliegue mientras alguien captura pierde esos cambios.
- Fase 1 (importación del histórico) implementada: mediciones con historial, catálogo inicial, mapeos e importación con informe. El histórico (unas 636.000 mediciones) está importado en la base local; falta revisar el informe y llevar la base a producción con `scripts/gcp/replace-db.sh` (decidido: la base local reemplaza la de producción).
- Fase 2 (variables importantes y explorador) implementada y desplegada. Los puntos de cada variable importante son datos (admin); la configuración inicial la crea la migración `dashboards/0002`. Solo hay un límite cargado (fenoles en BA-4010); los demás de §8 los carga el administrador.
- Fase 3 (captura, historial y exportaciones) implementada; las decisiones del 2026-10-20 están en §15. Los formatos iniciales los crea la migración `catalog/0004` desde `import_maps/` (solo variables con datos desde octubre de 2025).
- Fase 4 (gráficas del ICAV, §7.3) implementada: las 8 gráficas semanales de «Graficas» de la tabla 2, de lunes a domingo; la migración `dashboards/0004` crea la configuración inicial. La calificación del ICAV sigue pendiente (§15, pendiente 11).

## Stack
- Igual que Avante (`../avante`), que es la referencia de cómo se hace todo:
  - Python 3.14, Django 6 y `uv` (`pyproject.toml` y `uv.lock`; no hay `requirements.txt`).
  - SQLite, también en producción, replicado con Litestream.
  - Plantillas de Django + HTMX servido desde `static/js/`, sin CDN. Sin SPA.
- Gráficas con ECharts 5.6.0 servido localmente (`static/js/echarts.min.js`), la misma versión del dashboard U044.
- `openpyxl` para la importación del histórico y las exportaciones; `django-axes` para el bloqueo por intentos fallidos.
- Estética RefinIA: los tokens y la barra superior de `../refinia-portal/static/css/styles.css`, IBM Plex Sans y tema claro. Si la barra cambia allá, cambia aquí.
- Despliegue en Google Cloud:
  - Cloud Run, servicio `dashboard-ptar`, región `us-east1`, proyecto `project-76e49327-2ee1-47c7-861`.
  - Litestream → Cloud Storage, Cloud Build + Artifact Registry y Secret Manager.

## Convenciones
- Código, identificadores, commits y comentarios en **inglés**; interfaz y mensajes al usuario en **español**.
- Zona horaria `America/Bogota`. Los números se muestran con coma decimal; al capturar se acepta coma o punto.
- Configuración y secretos por variables de entorno, nunca en el código.
- Catálogos, límites y formatos de captura son **datos** (admin), no constantes en el código: añadir un punto, un parámetro o un límite no requiere programar.

## Reglas que no se deben romper
- **Los datos de la planta nunca van al repositorio:** ni Excel, ni CSV con valores, ni exportaciones, ni bases de datos. Los mapeos de importación (`import_maps/*.csv`) solo llevan encabezados.
- **Formato largo:** una medición es una variable (punto + parámetro + fuente) con fecha y hora, un valor numérico y un calificador opcional ("<" o ">"). Nunca una columna por variable.
- **No hay estados:** ND, FS, SB y similares significan que no se tiene un valor. Un dato que no hay (NaN) no se guarda: no hay fila.
- **Varias fuentes y varios puntos conviven** para la misma variable; ninguna fuente reemplaza a otra. La fuente es quien midió, no quien digitó.
- **Validación en el servidor:**
  - solo números (coma o punto decimal), opcionalmente con "<" o ">" delante;
  - si el parámetro tiene rango físico, fuera de él se rechaza; si la variable tiene rango habitual, fuera de él se pide confirmar;
  - **los rangos son opcionales:** la app tiene que funcionar sin ellos.
- **Historial:**
  - toda creación, corrección o borrado de una medición queda en el historial (valor anterior, quién, cuándo, motivo opcional);
  - el historial nunca se borra;
  - una sola medición por (variable, fecha y hora).
- **"Sin datos" nunca es "cumple"** en límites, indicadores ni en el análisis semanal.
- **Importación:**
  - "<10" se importa con su calificador; los demás valores no numéricos del histórico quedan como NaN (no se importan) y el informe los cuenta;
  - no se corrigen valores solos: los numéricos fuera del rango físico se importan marcados como dudosos, quedan fuera de las gráficas y de la estadística, y una persona decide;
  - no se inventan horas: si la fuente solo da el día, se guarda sin hora.
- **Roles:**
  - administrador, ingeniero (lee todo; captura solo en sus ámbitos) y capturista (**sin ninguna lectura**; captura solo en sus ámbitos);
  - al inicio, los tableristas capturan todas las fuentes;
  - los permisos se verifican en el servidor en cada vista;
  - una cuenta por persona, nunca compartida; las personas se desactivan, no se borran.
- **Límites** con vigencia: cada muestra se evalúa con el límite vigente en su fecha.
- **Base de datos en producción:** SQLite dentro del contenedor de Cloud Run, replicada por Litestream.
  - Por eso el servicio corre con **una sola instancia** (`--max-instances 1`) y **CPU siempre asignada**.
  - Los comandos de `manage.py` contra producción se ejecutan **al arrancar** el contenedor, nunca en un job aparte.
  - Desplegar cuando nadie esté usando la app.
- **Si se sirve detrás de Firebase Hosting** (`refinia-ptar.web.app`): Firebase solo deja pasar la cookie `__session`, así que se usa `SESSION_COOKIE_NAME = "__session"` y `CSRF_USE_SESSIONS = True`, y se responde con `Cache-Control: private`. Además, Firebase corta las peticiones de más de 60 segundos.

## Datos de referencia
- Los Excel con datos reales están **fuera del repositorio**, en `C:\Users\srada\Desktop\referencia_ptar\`:
  - `tabla_referencia_1.xlsx`: aliado químico (Nalco), hoja «Entrada de Datos»;
  - `tabla_referencia_2.xlsx`: "SEGUIMIENTO UT DESCONTAMINACIÓN NUEVO", hojas «Datos LABORATORIO» a «ECODIESEL».
- **No van al repositorio**; `.gitignore` los excluye por si alguien los copia.
- Para leerlos con Python, abrirlos con `openpyxl` en `read_only=True`: el modo normal falla por las cachés de tablas dinámicas.
- «Hoja4» y «Rangos ICAV» de la tabla 2 son un ejemplo antiguo que ya no funciona: sus reglas y valores no se toman como referencia.
- En la importación, Claude revisa los valores que no se mapean automáticamente y **consulta al usuario cuando no pueda decidir**.

## Forma de trabajo
- Se desarrolla por fases (§14 de REQUISITOS.md). No adelantar fases sin que se pida.
- Si una decisión cambia, actualizar primero `docs/REQUISITOS.md`.
- Cada regla de validación, de permisos y de estadística lleva pruebas. La importación se prueba con los casos reales de §16 de REQUISITOS.md: "<10" (calificador), "7,,4" y "SB" (NaN), pH 73 (dudoso), horas a :59 y duplicados.

## Comandos
- Instalar dependencias: `uv sync`
- Servidor local (SQLite, `config.settings.dev`): `uv run python manage.py runserver 8010` (el 8000 lo usa Avante)
- Importar el histórico (idempotente; `--dry-run` simula): `uv run python manage.py import_history --user <admin> C:/Users/srada/Desktop/referencia_ptar/tabla_referencia_1.xlsx C:/Users/srada/Desktop/referencia_ptar/tabla_referencia_2.xlsx` (unos 2 minutos). El informe queda en Administración → Lotes de importación.
- Pruebas: `uv run python -m pytest`
- Preparar ya el archivo semanal (local): `uv run python manage.py weekly_export`
- Revisión de producción: `DJANGO_SETTINGS_MODULE=config.settings.prod uv run python manage.py check --deploy` (requiere `SECRET_KEY` y `ALLOWED_HOSTS`)
- Migraciones: `uv run python manage.py makemigrations` / `uv run python manage.py migrate`
- Crear administrador (local): `uv run python manage.py createsuperuser`
- Google Cloud (Git Bash, desde la raíz del repo), como en Avante:
  - una vez: `bash scripts/gcp/setup.sh`;
  - en cada despliegue: `bash scripts/gcp/deploy.sh`;
  - primer administrador: `bash scripts/gcp/create-admin.sh`;
  - reemplazar la base de producción por la local: `bash scripts/gcp/replace-db.sh db.sqlite3`;
  - guía en `docs/DESPLIEGUE.md`.

## Estructura
- `config/settings/`: `base`, `dev`, `test` y `prod`. La sesión usa la cookie `__session` y el token CSRF vive en la sesión (Firebase Hosting).
- `apps/accounts`: `User` (modelo de usuario, con `role` y `capture_forms`), `permissions.py` (`reader_required`, `capture_required`), bloqueo por intentos fallidos (`lockout.py`), cambio de contraseña obligatorio (middleware) y `create_initial_admin`.
- `apps/catalog`: `Source`, `ProcessArea`, `SamplingPoint` y `PointAlias`, `Parameter` (rango físico), `Variable` (punto + parámetro + fuente, rango habitual), `Limit` (con vigencia; `Limit.objects.in_force(fecha)`), `CaptureForm` y `CaptureFormVariable`. Todo se gestiona en el admin.
- `apps/core`: `AuditEntry` y `audit.py` (`AuditedAdmin`: registra antes → después de cada cambio hecho en el admin, también en los inlines), `PrivateCacheMiddleware` (`Cache-Control: private`), `HtmxRedirectMiddleware` y la redirección de inicio por rol.
- `apps/capture`: página **Captura** (§6).
  - `grid.py`: las celdas de cada variable según su frecuencia (`slots_of`), quién puede cambiar un valor (`may_change`: el capturista, solo lo suyo de las últimas 24 horas) y la rejilla de un formato para un día (`build`).
  - `views.py`: la rejilla, guardar una celda (`save_cell`, responde JSON: guardado, inválido, pide confirmar, conflicto…) y su historial. `static/js/capture.js` maneja el teclado, las confirmaciones con motivo y la barra de la celda.
- `apps/dashboards`: **Variables importantes**, **Explorador** e **ICAV** (§7).
  - `ImportantVariable`: un parámetro y sus puntos (hasta 8, `MAX_POINTS`), en el admin.
  - `stats.py`: muestras (sin dudosos), ventanas por días calendario, estadística descriptiva, límites con vigencia (`LimitBook`) y agregación.
  - `charts.py`: los datos de cada gráfica (color = punto, forma = fuente, límites, horas de Bogotá); `static/js/charts.js` las dibuja y descarga cada una como PNG con título y leyenda (`image()` da su nombre y su título).
  - `panels.py` (tarjetas de variables importantes), `explorer.py` (formulario y series) y `export.py` (Excel del explorador).
  - `WeeklyChart` y `WeeklyChartVariable`: las gráficas del ICAV, una lista de variables con la misma unidad (hasta 8 puntos), en el admin. `weekly.py`: la semana de lunes a domingo, los promedios diarios, la tabla y el Excel (una hoja por gráfica).
- `apps/measurements`: `Measurement` (formato largo; `time_precision`: hora exacta, a. m., p. m. o solo el día; `taken_at` es el inicio del periodo cuando no hay hora), `MeasurementHistory` (nunca se borra), `values.py` (qué es un valor: `parse_value`, rangos) y `records.py` (crear, corregir y borrar con historial; `version` detecta cambios de otra persona). En el admin, solo lectura: se corrige desde la captura.
- `apps/imports`: `ImportBatch` (con conteos e informe), `maps.py` (lee `import_maps/`), `catalog.py` (crea el catálogo inicial que falte), `workbook.py` (busca las tablas de Excel en el XML del libro y lee valores y fórmulas), `timeline.py` (redondeo y deducción de horas por la secuencia), `importer.py` y el comando `import_history`.
- `apps/exports`: página **Exportaciones** (§10): a demanda (larga o ancha por fuente, hasta 100.000 mediciones) y el archivo semanal (`WeeklyExport`, `weekly.py`), que `WeeklyExportMiddleware` dispara en segundo plano con la primera visita después del lunes. `workbook.py` escribe los Excel; `storage.py` los guarda en el bucket (`EXPORTS_BUCKET`) o en `exports/` en local.
- `import_maps/`: `catalog/*.csv` (fuentes, zonas, puntos con alias, parámetros con rango físico) y un mapeo por tabla de Excel (`Tabla1.csv`, `Laboratorio.csv`…), una fila por columna, buscada por su encabezado. Solo encabezados y códigos, nunca valores.
- `templates/`: `base.html` lleva la barra de RefinIA y el menú según el rol. `static/css/app.css` lleva los tokens y la barra copiados de `refinia-portal`.
- `docker/` (`start.sh`, `litestream.yml`, `fetch_seed.py`), `Dockerfile`, `scripts/gcp/` y `docs/DESPLIEGUE.md`: despliegue en Cloud Run. La carpeta de la réplica en el bucket es `LITESTREAM_PATH` (por defecto `db`); `replace-db.sh` empieza una nueva.
