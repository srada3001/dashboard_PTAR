# Despliegue del Dashboard PTAR en Google Cloud

Todo corre en Google Cloud, en el mismo proyecto de RefinIA y Avante:

| Pieza | Servicio |
|---|---|
| App web, con HTTPS y dominio `*.run.app` | **Cloud Run**, servicio `dashboard-ptar` (una sola instancia, CPU siempre asignada) |
| Base de datos | **SQLite** dentro de la app, copiada continuamente a **Cloud Storage** por **Litestream** |
| Construcción y almacenamiento de la imagen | **Cloud Build** + **Artifact Registry** (nada se construye en tu computador) |
| `SECRET_KEY` de Django | **Secret Manager** |

Los scripts de `scripts/gcp/` se ejecutan en **Git Bash**, desde la raíz del repositorio, con el `gcloud` que ya tienes instalado. Todo se crea en la región `us-east1`, salvo que exportes otra, por ejemplo `REGION=southamerica-east1`.

**Costo esperado:** cerca de la capa gratuita, como Avante. Cloud Run solo cobra mientras la app está encendida (mientras la usan y unos 15 minutos después). El bucket y las imágenes cuestan centavos.

## Cómo funciona la base de datos

1. **Al arrancar**, la app restaura la base desde Cloud Storage, aplica las migraciones y crea el primer administrador si se pidió.
2. **Mientras funciona**, Litestream copia cada cambio a Cloud Storage en aproximadamente un segundo.
3. **Litestream guarda 3 días de historial**, así que la base se puede restaurar a cualquier momento de ese período. La retención definitiva está pendiente (REQUISITOS.md §15).
4. **El bucket tiene versionado de objetos:** un archivo de la réplica sobrescrito o borrado se puede recuperar.

**Regla importante: despliega cuando nadie esté usando el dashboard.** Durante un despliegue, la versión vieja y la nueva conviven unos segundos, y los cambios hechos justo en ese momento se pierden. `deploy.sh` te avisa si alguien usó la app en los últimos 10 minutos.

---

## 1. Proyecto de Google Cloud

Se usa el proyecto que ya tienes. El dashboard corre con su propia cuenta de servicio, así que no se mezcla con las otras herramientas.

Comprueba que `gcloud` apunte al proyecto correcto:

```bash
gcloud config get-value project
```

Si no es el correcto, cambia `ID_DEL_PROYECTO` por el ID real:

```bash
gcloud config set project ID_DEL_PROYECTO
```

## 2. Preparar el proyecto (una sola vez)

```bash
bash scripts/gcp/setup.sh
```

El script:
- activa las APIs;
- crea el repositorio de imágenes;
- genera la `SECRET_KEY`;
- crea el bucket privado donde vive la copia de la base, con versionado;
- crea la cuenta de servicio `dashboard-ptar-run`, con acceso solo a su secreto y a su bucket.

Si se corta a mitad de camino, vuelve a ejecutarlo: los recursos que ya existen se conservan.

## 3. Desplegar

```bash
bash scripts/gcp/deploy.sh
```

1. Sube el código a Cloud Build, que construye la imagen.
2. Publica la app en Cloud Run con una sola instancia y CPU siempre asignada.

Al final imprime la dirección del dashboard, del estilo `https://dashboard-ptar-123456789012.us-east1.run.app`.

## 4. Crear tu usuario administrador

```bash
bash scripts/gcp/create-admin.sh
```

Pide el usuario (nombre corto) y el nombre completo, reinicia la app con ese pedido y muestra **una contraseña temporal**. Entra con ella: la app te pedirá cambiarla de inmediato.

- La contraseña temporal queda en los logs de Cloud Run, que solo ve quien administra el proyecto. Por eso es de un solo uso.
- Si ya existe un administrador, el script no crea otro.
- Las demás personas las creas desde **Administración** dentro de la app, cada una con su rol y sus formatos de captura.

## 5. Entrada desde RefinIA

La gente entra por **https://refinia-ptar.web.app** (REQUISITOS.md §15), como a las otras herramientas, o desde su tarjeta en la portada de RefinIA. La dirección de `run.app` sigue funcionando.

- El sitio `refinia-ptar` de Firebase Hosting pasa todas las peticiones al servicio `dashboard-ptar`. Su bloque está en `firebase.json` del repositorio `refinia-portal`, y se publica con cada push a `main` de ese repositorio.
- La sesión usa la cookie `__session`, la única que Firebase Hosting deja pasar a Cloud Run.
- Todas las respuestas llevan `Cache-Control: private`, para que la CDN de Firebase no guarde páginas de nadie.
- `https://refinia-ptar.web.app` está en `CSRF_TRUSTED_ORIGINS` (`scripts/gcp/config.sh`). Si se le conecta un dominio propio, hay que agregarlo ahí y volver a desplegar.
- Firebase corta las peticiones de más de 60 segundos. Si alguna tarda más, se entra por la dirección de `run.app`.

## 6. Actualizaciones

1. Haz commit de tus cambios. El despliegue avisa si hay cambios sin commit.
2. Cuando nadie esté usando el dashboard, ejecuta de nuevo:

```bash
bash scripts/gcp/deploy.sh
```

Las migraciones pendientes se aplican solas cuando arranca la nueva versión.

## Problemas comunes

**Logs de la app** (incluye la restauración de la base y las migraciones):

```bash
gcloud run services logs read dashboard-ptar --region us-east1 --limit 50
```

**Errores frecuentes:**
- **"PERMISSION_DENIED" durante el build o el despliegue:** vuelve a ejecutar `bash scripts/gcp/setup.sh`, que reaplica los permisos. Algunos permisos tardan un par de minutos en propagarse.
- **"Bad Request (400)":** estás entrando con una dirección que no termina en `.run.app`. Hay que agregarla a `ALLOWED_HOSTS` en `scripts/gcp/config.sh`.
- **"Prohibido (403) · CSRF" al enviar un formulario:** la dirección desde la que entras no está en `CSRF_TRUSTED_ORIGINS` (`scripts/gcp/config.sh`).
- **La primera carga tras un rato sin uso tarda unos segundos:** la app arranca y restaura la base. Es normal.
- **Nunca subas el máximo de instancias por encima de 1.** Cada instancia tendría su propia copia de la base, y los datos se separarían.
