#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PYTHON="$ROOT_DIR/venv/bin/python"
PORT="${PORT:-5000}"

usage() {
  cat <<'EOF'
Uso:
  ./run_app.sh
    Arranca la app local en un puerto libre (5000-5010).

  ./run_app.sh --deploy [base_yaml] [credentials_yaml] [output_yaml] [gcloud_args...]
    Genera output_yaml usando scripts/build_app_yaml.sh y hace deploy con gcloud.

Ejemplos:
  ./run_app.sh --deploy
  ./run_app.sh --deploy app.yaml credentials.yaml app.deploy.yaml --quiet
EOF
}

is_port_in_use() {
  local port="$1"
  lsof -nP -iTCP:"$port" -sTCP:LISTEN >/dev/null 2>&1
}

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
  usage
  exit 0
fi

if [[ "${1:-}" == "--deploy" ]]; then
  shift

  BASE_FILE="app.yaml"
  CREDENTIALS_FILE="credentials.yaml"
  OUTPUT_FILE="app.deploy.yaml"

  if [[ $# -ge 1 ]]; then
    BASE_FILE="$1"
    shift
  fi
  if [[ $# -ge 1 ]]; then
    CREDENTIALS_FILE="$1"
    shift
  fi
  if [[ $# -ge 1 ]]; then
    OUTPUT_FILE="$1"
    shift
  fi

  if ! command -v gcloud >/dev/null 2>&1; then
    echo "No se encuentra gcloud en PATH."
    exit 1
  fi

  echo "Generando $OUTPUT_FILE con $BASE_FILE + $CREDENTIALS_FILE..."
  "$ROOT_DIR/scripts/build_app_yaml.sh" "$BASE_FILE" "$CREDENTIALS_FILE" "$OUTPUT_FILE"

  echo "Desplegando con gcloud app deploy $OUTPUT_FILE $*"
  exec gcloud app deploy "$OUTPUT_FILE" "$@"
fi

if [[ -x "$VENV_PYTHON" ]]; then
  if is_port_in_use "$PORT"; then
    echo "Puerto $PORT ocupado, buscando puerto libre..."
    for candidate in 5001 5002 5003 5004 5005 5006 5007 5008 5009 5010; do
      if ! is_port_in_use "$candidate"; then
        PORT="$candidate"
        echo "Usando puerto alternativo: $PORT"
        break
      fi
    done
  fi

  if is_port_in_use "$PORT"; then
    echo "No hay puertos libres entre 5000 y 5010."
    echo "Puedes lanzar con un puerto manual: PORT=5050 ./run_app.sh"
    exit 1
  fi

  export PORT
  echo "Arrancando app en http://127.0.0.1:$PORT"
  exec "$VENV_PYTHON" "$ROOT_DIR/main.py"
fi

echo "No se ha encontrado el entorno virtual en $ROOT_DIR/venv"
echo "Crea el venv o ajusta el script para tu entorno."
exit 1
