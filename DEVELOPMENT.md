# Guía de Desarrollo - Parrao Weather Web

## 🏗️ Arquitectura de la Aplicación

### Diagrama de Componentes
```
┌─────────────────────────────────────────┐
│         Usuario / Navegador             │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│      Flask App (web.py)                 │
│  - Rutas HTTP                           │
│  - Renderizado de templates             │
│  - Manejo de sesiones                   │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│    Módulo Weather (weather.py)          │
│  - Integración con APIs                 │
│  - Procesamiento de datos               │
└──────┬──────────────────┬───────────────┘
       │                  │
       ▼                  ▼
┌──────────────┐   ┌─────────────────┐
│ EcoWitt API  │   │ Weather Under-  │
│              │   │ ground API      │
└──────────────┘   └─────────────────┘
```

### Módulos Principales

#### `main.py`
- Punto de entrada de la aplicación
- Inicializa Flask app desde `src.web`

#### `src/web.py`
- Define rutas Flask
- Renderiza templates con Jinja2
- Maneja requests HTTP

#### `src/weather.py`
- Interfaz con APIs meteorológicas
- Transformación y normalización de datos
- Cache de datos (si aplica)

#### `src/config.py`
- Carga variables de entorno
- Configuración de la aplicación
- Parámetros de APIs

#### `src/logger.py`
- Sistema de logging centralizado
- Configuración de niveles por entorno

#### `src/utils.py`
- Funciones auxiliares
- Helpers reutilizables

## 🔧 Configuración Local

### Requisitos Previos
- Python 3.10 o superior
- pip (gestor de paquetes Python)
- Google Cloud SDK (para deployment)
- Git

### Instalación Paso a Paso

1. **Clonar repositorio**
   ```bash
   git clone <repo-url>
   cd parrao_weather_web
   ```

2. **Crear entorno virtual**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-tests.txt
   ```

4. **Configurar variables de entorno**
   ```bash
   cp .env_template .env
   # Editar .env con tus credenciales
   ```

5. **Verificar instalación**
   ```bash
   python -c "from src.web import app; print('✅ OK')"
   ```

### Variables de Entorno Explicadas

```bash
# Entorno: N=desarrollo, Y=producción
ENV_PRO=N

# Nivel de logging
LEVEL_LOG=INFO  # Opciones: DEBUG, INFO, WARNING, ERROR, CRITICAL

# API Weather Underground
API_KEY_WUNDERGROUND=tu_clave_aqui
STATION_ID=ICERCE9  # ID de tu estación

# API EcoWitt
API_KEY_ECOWITT=tu_clave_aqui
APPLICATION_KEY=tu_application_key
STATION_MAC=BC:FF:4D:10:E4:C5  # MAC de tu estación
```

### Obtener Claves API

**Weather Underground:**
1. Registrarse en https://www.wunderground.com/member/api-keys
2. Crear una API key
3. Copiar al .env

**EcoWitt:**
1. Acceder a https://www.ecowitt.net/
2. Login → API keys
3. Generar nueva clave
4. Copiar al .env

## 🚀 Ejecutar la Aplicación

### Desarrollo Local
```bash
# Activar entorno virtual
source venv/bin/activate

# Ejecutar Flask
flask run

# O con variables específicas
flask run --host=0.0.0.0 --port=8080

# Con debug mode
flask run --debug
```

### Acceder a la Aplicación
- Local: http://localhost:5000
- Red local: http://tu-ip:5000

## 🧪 Testing y Quality Assurance

### Estructura de Tests
```
tests/
├── __init__.py
├── test_web.py       # Tests de rutas Flask
├── test_weather.py   # Tests de integración API
├── test_config.py    # Tests de configuración
└── test_utils.py     # Tests de utilidades
```

### Ejecutar Tests
```bash
# Todos los tests con coverage
./check_app.sh

# O manualmente
coverage run -m pytest -v
coverage report
coverage html

# Test específico
pytest tests/test_web.py -v

# Test con nombre específico
pytest tests/test_web.py::test_home_page -v

# Ver output detallado
pytest -vv -s
```

### Escribir Buenos Tests

**Ejemplo: Test de Ruta Flask**
```python
def test_home_page(client):
    """Test que la página home carga correctamente."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Parrao Weather' in response.data
```

**Ejemplo: Test con Mock de API**
```python
from unittest.mock import patch

def test_get_weather_data():
    """Test obtención de datos con API mockeada."""
    mock_response = {'temp': 25, 'humidity': 60}
    
    with patch('src.weather.requests.get') as mock_get:
        mock_get.return_value.json.return_value = mock_response
        result = get_weather_data('STATION123')
        
    assert result['temp'] == 25
    assert 'humidity' in result
```

### Coverage al 100%
- Cada función debe tener al menos un test
- Probar casos normales y edge cases
- Mockear APIs externas
- No testear código de librerías externas

## 📦 Deployment

### Google Cloud Platform (App Engine)

#### Pre-requisitos
```bash
# Instalar gcloud CLI
brew install --cask google-cloud-sdk  # macOS
# O desde https://cloud.google.com/sdk/docs/install

# Autenticar
gcloud auth login

# Configurar proyecto
gcloud config set project tu-proyecto-id
```

#### Configuración app.yaml
```yaml
runtime: python310
entrypoint: gunicorn -b :$PORT main:app

env_variables:
  ENV_PRO: "Y"
  LEVEL_LOG: "ERROR"
  # Otras variables...

handlers:
- url: /static
  static_dir: static
- url: /.*
  script: auto
```

#### Deploy
```bash
# Deploy a producción
gcloud app deploy

# Deploy con staging
gcloud app deploy --version=staging --no-promote

# Ver logs en tiempo real
gcloud app logs tail -s default

# Ver info de la app
gcloud app describe
```

### CI/CD (Opcional)

**GitHub Actions ejemplo:**
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - run: pip install -r requirements.txt -r requirements-tests.txt
      - run: coverage run -m pytest -v
      - run: coverage report --fail-under=100
```

## 🐛 Debugging

### Flask Debug Mode
```bash
# Activar debug
export FLASK_DEBUG=1
flask run

# Ver stack traces detallados en browser
```

### Logging
```python
from src.logger import logger

# En tu código
logger.info("Información general")
logger.warning("Advertencia")
logger.error("Error", exc_info=True)  # Incluye stacktrace
```

### Debugging en VSCode
Crear `.vscode/launch.json`:
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Flask",
      "type": "python",
      "request": "launch",
      "module": "flask",
      "env": {
        "FLASK_APP": "main.py",
        "FLASK_DEBUG": "1"
      },
      "args": ["run"],
      "jinja": true
    }
  ]
}
```

## 📊 Monitorización

### Logs en Producción
```bash
# Ver logs recientes
gcloud app logs read --limit=50

# Filtrar por nivel
gcloud app logs read --level=error

# Seguir logs en tiempo real
gcloud app logs tail -s default
```

### Métricas Importantes
- Tiempo de respuesta de APIs
- Rate limits de APIs externas
- Errores HTTP (4xx, 5xx)
- Uso de memoria/CPU en App Engine

## 🔒 Seguridad

### Checklist de Seguridad
- ✅ No commitear `.env` (en `.gitignore`)
- ✅ Usar HTTPS en producción
- ✅ Validar inputs de usuario
- ✅ Rate limiting en endpoints públicos
- ✅ Headers de seguridad (CSP, X-Frame-Options)
- ✅ Actualizar dependencias regularmente

### Rotar API Keys
1. Generar nuevas keys en servicios
2. Actualizar en GCP Secret Manager o variables de entorno
3. Deploy nueva versión
4. Revocar keys antiguas

## 📚 Recursos Adicionales

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Google App Engine Python](https://cloud.google.com/appengine/docs/standard/python3)
- [pytest Best Practices](https://docs.pytest.org/en/stable/goodpractices.html)
- [Python Testing with pytest](https://pythontest.com/pytest-book/)

## 💡 Tips y Trucos

### Performance
- Cachear respuestas de API cuando sea posible
- Usar CDN para assets estáticos
- Comprimir respuestas (gzip)
- Optimizar imágenes en `/static`

### Productividad
```bash
# Alias útiles para .bashrc/.zshrc
alias fr="flask run"
alias frd="flask run --debug"
alias pt="pytest -v"
alias ptc="coverage run -m pytest -v && coverage html"
```

### Git Hooks
Pre-commit hook para tests:
```bash
#!/bin/sh
# .git/hooks/pre-commit
coverage run -m pytest || exit 1
coverage report --fail-under=100 || exit 1
```

## ❓ Troubleshooting

### Error: "ModuleNotFoundError"
```bash
# Verificar que venv está activado
which python  # Debe apuntar a venv/bin/python

# Reinstalar dependencias
pip install -r requirements.txt
```

### Error: "API Key Invalid"
- Verificar que `.env` existe y tiene las keys
- Verificar que keys no tienen espacios extras
- Probar keys directamente en las APIs

### Tests Fallan
```bash
# Limpiar cache
find . -type d -name __pycache__ -exec rm -r {} +
find . -type f -name "*.pyc" -delete

# Reinstalar en modo editable
pip install -e .
```

### App No Carga en Browser
```bash
# Verificar que Flask está corriendo
ps aux | grep flask

# Verificar puerto
lsof -i :5000

# Probar con curl
curl http://localhost:5000
```
