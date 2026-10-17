# Dashboard PTAR

**Dashboard PTAR** (repositorio `dashboard_PTAR`) es la aplicación web interna que reúne los datos de calidad y de operación de la PTAR de la Refinería de Barrancabermeja (Ecopetrol). Recibe los datos del laboratorio central (Labviewer), de BIOTA y Nalco. Reemplaza los Excel que hoy se editan a mano: valida los datos al ingresarlos, los guarda en un formato único y ofrece vistas de tendencias. Es una herramienta más de RefinIA (`refinia-portal`).

**La especificación completa está en [docs/REQUISITOS.md](docs/REQUISITOS.md). Léela antes de proponer o implementar cualquier cambio de alcance, de modelo de datos o de reglas.** Las decisiones abiertas están en su §15: no las des por resueltas; si una tarea depende de una, pregunta.

## Estado
- Fase 0 en código: proyecto base, usuarios con roles y ámbitos, login con bloqueo, catálogos y límites en el admin con registro de auditoría, estética RefinIA, pantallas por rol y archivos de despliegue. Falta el primer despliegue en Google Cloud.
- Fase 1 (importación del histórico) sin empezar: todavía no hay mediciones.

## Stack
- Igual que Avante (`../avante`), que es la referencia de cómo se hace todo:
  - Python 3.14, Django 6 y `uv` (`pyproject.toml` y `uv.lock`; no hay `requirements.txt`).
  - SQLite, también en producción, replicado con Litestream.
  - Plantillas de Django + HTMX servido desde `static/js/`, sin CDN. Sin SPA.
- Gráficas con ECharts 5.6.0 servido localmente, la misma versión del dashboard U044.
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
- Pruebas: `uv run python -m pytest`
- Revisión de producción: `DJANGO_SETTINGS_MODULE=config.settings.prod uv run python manage.py check --deploy` (requiere `SECRET_KEY` y `ALLOWED_HOSTS`)
- Migraciones: `uv run python manage.py makemigrations` / `uv run python manage.py migrate`
- Crear administrador (local): `uv run python manage.py createsuperuser`
- Google Cloud (Git Bash, desde la raíz del repo), como en Avante:
  - una vez: `bash scripts/gcp/setup.sh`;
  - en cada despliegue: `bash scripts/gcp/deploy.sh`;
  - primer administrador: `bash scripts/gcp/create-admin.sh`;
  - guía en `docs/DESPLIEGUE.md`.

## Estructura
- `config/settings/`: `base`, `dev`, `test` y `prod`. La sesión usa la cookie `__session` y el token CSRF vive en la sesión (Firebase Hosting).
- `apps/accounts`: `User` (modelo de usuario, con `role` y `capture_forms`), `permissions.py` (`reader_required`, `capture_required`), bloqueo por intentos fallidos (`lockout.py`), cambio de contraseña obligatorio (middleware) y `create_initial_admin`.
- `apps/catalog`: `Source`, `ProcessArea`, `SamplingPoint` y `PointAlias`, `Parameter` (rango físico), `Variable` (punto + parámetro + fuente, rango habitual), `Limit` (con vigencia; `Limit.objects.in_force(fecha)`), `CaptureForm` y `CaptureFormVariable`. Todo se gestiona en el admin.
- `apps/core`: `AuditEntry` y `audit.py` (`AuditedAdmin`: registra antes → después de cada cambio hecho en el admin, también en los inlines), `PrivateCacheMiddleware` (`Cache-Control: private`), `HtmxRedirectMiddleware` y la redirección de inicio por rol.
- `apps/capture`: página **Captura**; por ahora lista los formatos de la persona. Las rejillas llegan en la fase 3.
- `apps/dashboards`: **Variables importantes** y **Explorador**; por ahora vacías. Se construyen en la fase 2.
- Previstas: `apps/measurements` (mediciones, historial y validación) y `apps/imports` (importación del histórico con `import_maps/`, y exportaciones).
- `templates/`: `base.html` lleva la barra de RefinIA y el menú según el rol. `static/css/app.css` lleva los tokens y la barra copiados de `refinia-portal`.
- `docker/` (`start.sh`, `litestream.yml`), `Dockerfile`, `scripts/gcp/` y `docs/DESPLIEGUE.md`: despliegue en Cloud Run.
