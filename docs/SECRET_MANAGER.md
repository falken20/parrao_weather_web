# Migración de credenciales a Google Cloud Secret Manager

Esta guía describe, paso a paso, cómo dejar de gestionar las credenciales
de la app con `credentials.yaml` / `app.deploy.yaml` y pasar a usar
**Google Cloud Secret Manager** desde App Engine.

> Rama del cambio: `feature/secret-manager`.
> El código ya soporta ambos modos: si una variable de entorno está
> definida, se usa tal cual; si no, y `ENV_PRO=Y` con `GCP_PROJECT_ID`
> configurado, se resuelve desde Secret Manager.

---

## 1. Resumen de cambios incluidos en esta rama

- `src/config.py`
  - Nuevo `_read_env(name, required)` con caché en memoria.
  - Si `ENV_PRO=Y` y existe `GCP_PROJECT_ID`, las variables ausentes
    se resuelven desde Secret Manager con `access_secret_version`.
  - El cliente y la dependencia se importan **de forma lazy** para no
    romper entornos locales / tests sin la librería instalada.
- `requirements.txt`
  - Añadida la dependencia `google-cloud-secret-manager==2.20.0`.
- `app.yaml`
  - Añadida la variable `GCP_PROJECT_ID`.
  - Eliminados los placeholders de claves; ahora todo se resuelve por
    Secret Manager.

---

## 2. Pre-requisitos

1. Tener `gcloud` instalado y autenticado:
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```
2. Habilitar la API de Secret Manager en el proyecto:
   ```bash
   gcloud services enable secretmanager.googleapis.com
   ```
3. Identificar la **service account** de App Engine. Por defecto:
   ```
   YOUR_PROJECT_ID@appspot.gserviceaccount.com
   ```

---

## 3. Crear los secretos

Crea un secreto por cada credencial. Política de replicación
`automatic` (1 location lógica) para no pagar versiones extra.

```bash
PROJECT_ID="YOUR_PROJECT_ID"

for SECRET in \
  API_KEY_WUNDERGROUND \
  STATION_ID \
  API_KEY_ECOWITT \
  APPLICATION_KEY \
  STATION_MAC \
  FLASK_SECRET_KEY \
  API_ACCESS_KEY; do
  gcloud secrets create "$SECRET" \
    --project="$PROJECT_ID" \
    --replication-policy="automatic"
done
```

> Si alguno ya existe, `gcloud` devolverá un error inocuo; puedes
> ignorarlo o filtrarlo.

---

## 4. Cargar los valores (versión inicial)

**Nunca** pases los secretos como argumento de línea de comandos (quedan
en el historial del shell). Usa stdin:

```bash
printf '%s' 'tu_api_key_real' | \
  gcloud secrets versions add API_KEY_WUNDERGROUND --data-file=- --project="$PROJECT_ID"
```

Repite para cada secreto. Para el `FLASK_SECRET_KEY` genera uno nuevo:

```bash
python -c "import secrets; print(secrets.token_hex(32))" | \
  gcloud secrets versions add FLASK_SECRET_KEY --data-file=- --project="$PROJECT_ID"
```

Verificar:

```bash
gcloud secrets versions access latest --secret=API_KEY_WUNDERGROUND --project="$PROJECT_ID"
```

---

## 5. Permisos de la service account de App Engine

Da acceso de **solo lectura** (`secretAccessor`) a la SA de App Engine
sobre los secretos. Lo más restrictivo es hacerlo secreto a secreto:

```bash
SA="${PROJECT_ID}@appspot.gserviceaccount.com"

for SECRET in \
  API_KEY_WUNDERGROUND \
  STATION_ID \
  API_KEY_ECOWITT \
  APPLICATION_KEY \
  STATION_MAC \
  FLASK_SECRET_KEY \
  API_ACCESS_KEY; do
  gcloud secrets add-iam-policy-binding "$SECRET" \
    --project="$PROJECT_ID" \
    --member="serviceAccount:$SA" \
    --role="roles/secretmanager.secretAccessor"
done
```

Si prefieres simplificar y dar acceso a nivel proyecto (menos seguro):

```bash
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:$SA" \
  --role="roles/secretmanager.secretAccessor"
```

---

## 6. Configurar `app.yaml`

Edita [app.yaml](../app.yaml) y sustituye:

```yaml
GCP_PROJECT_ID: "REPLACE_WITH_YOUR_GCP_PROJECT_ID"
```

por el ID real del proyecto. **No** vuelvas a incluir las claves API
en este fichero ni en `app.deploy.yaml`.

---

## 7. Desplegar

Con el nuevo flujo, el deploy es directo:

```bash
gcloud app deploy app.yaml --project="$PROJECT_ID"
```

Comprueba los logs:

```bash
gcloud app logs tail -s default --project="$PROJECT_ID"
```

En el arranque deberías ver los mensajes habituales (`LOG LEVEL`, `CACHE`),
y **ninguna** traza con valores de API keys.

---

## 8. Verificación funcional

1. Abre la URL del servicio.
2. Comprueba en Cloud Logging que no aparece ninguna excepción de tipo
   `PermissionDenied` ni `NotFound` relacionada con `secretmanager`.
3. Si una variable falta o la SA no tiene permisos, `src/config.py`
   lanzará `RuntimeError("Required configuration value 'X' is not set")`
   y la instancia no arrancará: error temprano y explícito.

---

## 9. Limpieza del flujo antiguo

Una vez verificado el despliegue:

1. Borra del disco local:
   ```bash
   rm -f credentials.yaml app.deploy.yaml
   ```
2. (Recomendado) Elimina del repo el flujo basado en YAML mezclado:
   - `scripts/build_app_yaml.sh`
   - Cualquier referencia en `README.md` y `run_app.sh` al modo
     `--deploy` con credenciales en fichero.
3. Confirma que `.gitignore` sigue cubriendo `credentials.yaml`,
   `app.deploy.yaml` y `.env`.
4. Confirma que `.gcloudignore` también los excluye para que jamás
   acaben en el bundle subido a App Engine.

---

## 10. Rotación de secretos

Rotación recomendada cada 90 días o ante sospecha de fuga.

```bash
# 1. Subir nueva versión
printf '%s' 'nuevo_valor' | \
  gcloud secrets versions add API_KEY_WUNDERGROUND --data-file=- --project="$PROJECT_ID"

# 2. Reiniciar instancias para que recarguen el secreto
gcloud app versions list --service=default --project="$PROJECT_ID"
gcloud app deploy app.yaml --project="$PROJECT_ID"   # nuevo deploy = nuevas instancias

# 3. Desactivar/destruir versión antigua
gcloud secrets versions disable 1 --secret=API_KEY_WUNDERGROUND --project="$PROJECT_ID"
gcloud secrets versions destroy 1 --secret=API_KEY_WUNDERGROUND --project="$PROJECT_ID"
```

> El código actual cachea el valor en memoria del proceso, así que
> **no** detecta una nueva versión sin reiniciar. Si necesitas
> rotación caliente, lanza un redeploy o cambia el cache para que
> caduque cada N minutos.

---

## 11. Desarrollo local

Sigues usando `.env` (cargado por `python-dotenv`). En local no se
contacta con Secret Manager porque `ENV_PRO=N`.

Recomendaciones:

- Mantén `.env` fuera de git (ya lo está en `.gitignore`).
- `chmod 600 .env` para evitar lecturas accidentales.
- Para probar el flujo de Secret Manager en local:
  1. `gcloud auth application-default login`
  2. Exporta `ENV_PRO=Y` y `GCP_PROJECT_ID=tu_proyecto`
  3. Deja sin definir la variable que quieres traer de Secret Manager.

---

## 12. Coste estimado

Para esta app (≤ 8 secretos, acceso en arranque cacheado en memoria):

- 6 versiones activas gratis al mes → cubre el caso normal.
- 10.000 accesos / mes gratis → más que suficiente.
- Coste real esperado: **0 €/mes**.

Tarifas oficiales: <https://cloud.google.com/secret-manager/pricing>.

---

## 13. Troubleshooting

| Síntoma | Causa probable | Acción |
|---|---|---|
| `RuntimeError: Required configuration value 'X' is not set` | Falta el secreto o la SA no tiene permisos | Crear/cargar versión y dar `secretAccessor` |
| `google.api_core.exceptions.PermissionDenied: 403` | IAM mal asignado | Re-ejecutar el `add-iam-policy-binding` |
| `google.api_core.exceptions.NotFound: 404` | Nombre del secreto distinto del esperado | Verifica que el nombre del secreto coincide **exactamente** con la variable (`API_KEY_WUNDERGROUND`, etc.) |
| El valor antiguo persiste tras rotar | Cache en memoria del proceso | Redeploy / reinicio de instancias |
| `ModuleNotFoundError: google.cloud.secretmanager` | Falta dependencia | `pip install -r requirements.txt` |

---

## 14. Checklist final

- [ ] API de Secret Manager habilitada.
- [ ] 7 secretos creados y con al menos una versión.
- [ ] SA de App Engine con `roles/secretmanager.secretAccessor`.
- [ ] `app.yaml` con `GCP_PROJECT_ID` real y sin claves API.
- [ ] Deploy correcto y app funcionando.
- [ ] `credentials.yaml`, `app.deploy.yaml` y flujo antiguo eliminados.
- [ ] Claves antiguas (las que estaban en `.env` / `credentials.yaml`)
      rotadas y revocadas en los proveedores (Wunderground, EcoWitt).
