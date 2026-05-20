# Carga y uso de credenciales en GCP (App Engine)

Este documento explica **cómo se cargan y cómo se usan** las credenciales en este proyecto cuando despliegas en Google Cloud Platform.

## Resumen rápido

- GCP **no** lee `credentials.yaml` directamente.
- En local, se genera `app.deploy.yaml` combinando:
  - `app.yaml` (base)
  - `credentials.yaml` (secretos)
- El deploy se hace con `app.deploy.yaml`.
- App Engine expone `env_variables` como variables de entorno.
- La aplicación las consume con `os.environ`.

## Flujo paso a paso

1. Crear archivo local de credenciales:

```bash
cp credentials.yaml.example credentials.yaml
```

2. Rellenar `credentials.yaml` con valores reales (no subir a git).

3. Generar archivo de deploy:

```bash
./scripts/build_app_yaml.sh
```

Esto crea `app.deploy.yaml` con las variables de `credentials.yaml` dentro de `env_variables`.

4. Desplegar a App Engine:

```bash
gcloud app deploy app.deploy.yaml
```

## Flujo automático recomendado

También puedes usar el script de proyecto, que lo hace en cadena:

```bash
./run_app.sh --deploy
```

Internamente:

- ejecuta `scripts/build_app_yaml.sh`
- genera `app.deploy.yaml`
- ejecuta `gcloud app deploy app.deploy.yaml`

## Dónde se leen las variables en el código

- `src/config.py`
  - `API_KEY_WUNDERGROUND`
  - `STATION_ID`
  - `API_KEY_ECOWITT`
  - `APPLICATION_KEY`
  - `STATION_MAC`
  - `GA_MEASUREMENT_ID`

- `src/web.py`
  - `FLASK_SECRET_KEY`
  - `ENV_PRO`
  - `FLASK_DEBUG`

- `src/api.py`
  - `API_ACCESS_KEY`

## Comportamiento en producción

- Si `ENV_PRO=Y`, el código exige variables críticas.
- Si falta `FLASK_SECRET_KEY` en producción, la app falla al arrancar por seguridad.

## Archivos relevantes

- `app.yaml`: configuración base sin secretos hardcodeados.
- `credentials.yaml`: secretos locales (no versionado).
- `app.deploy.yaml`: archivo generado para despliegue.
- `scripts/build_app_yaml.sh`: script de composición.
- `run_app.sh`: helper de deploy automático con `--deploy`.

## Seguridad recomendada

- No subir `credentials.yaml` ni `app.deploy.yaml` al repositorio.
- Rotar claves periódicamente.
- Preferir Secret Manager en producción cuando sea posible.
