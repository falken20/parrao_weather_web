#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PYTHON="$ROOT_DIR/venv/bin/python"
PORT="${PORT:-5000}"

is_port_in_use() {
  local port="$1"
  lsof -nP -iTCP:"$port" -sTCP:LISTEN >/dev/null 2>&1
}

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
