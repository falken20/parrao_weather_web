# Guía de Contribución

## 🚀 Configuración del Entorno de Desarrollo

### 1. Clonar el Repositorio
```bash
git clone <repository-url>
cd parrao_weather_web
```

### 2. Crear Entorno Virtual
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
pip install -r requirements-tests.txt
```

### 4. Configurar Variables de Entorno
Copiar `.env_template` a `.env` y configurar las credenciales:
```bash
cp .env_template .env
# Editar .env con tus claves API
```

### 5. Verificar Instalación
```bash
flask run
# La app debería estar disponible en http://localhost:5000
```

## 🧪 Testing

### Ejecutar Tests
```bash
# Opción 1: Usando el script
./check_app.sh

# Opción 2: Comando directo
coverage run -m pytest -v && coverage html --omit=*/venv/*,*/tests/*
```

### Ver Cobertura
```bash
# Generar reporte HTML
coverage html

# Ver en navegador (Mac)
open htmlcov/index.html

# Ver en navegador (Linux)
xdg-open htmlcov/index.html

# Ver en terminal
coverage report
```

### Requisitos de Testing
- ✅ **100% de cobertura de código**
- ✅ Todos los tests deben pasar
- ✅ Añadir tests para nueva funcionalidad
- ✅ Actualizar tests si modificas funcionalidad existente

## 📝 Estándares de Código

### Estilo Python
- Seguir **PEP 8**
- Usar **type hints**
- Documentar con **docstrings** (formato Google/NumPy)
- Máximo 100 caracteres por línea

### Ejemplo de Función Documentada
```python
def get_weather_data(station_id: str, api_key: str) -> dict:
    """
    Obtiene datos meteorológicos de una estación.
    
    Args:
        station_id: Identificador de la estación meteorológica
        api_key: Clave de API para autenticación
        
    Returns:
        Diccionario con los datos meteorológicos
        
    Raises:
        ValueError: Si station_id está vacío
        APIError: Si la API devuelve un error
    """
    pass
```

### Commits
- Usar mensajes descriptivos en español o inglés
- Formato sugerido: `tipo: descripción breve`
  - `feat: nueva funcionalidad`
  - `fix: corrección de bug`
  - `test: añadir/modificar tests`
  - `docs: documentación`
  - `refactor: refactorización`
  - `style: formateo de código`

## 🔄 Flujo de Trabajo

### 1. Crear Rama
```bash
git checkout -b feature/nombre-caracteristica
# o
git checkout -b fix/nombre-bug
```

### 2. Desarrollar
- Hacer cambios
- Añadir/actualizar tests
- Verificar que tests pasen
- Mantener cobertura al 100%

### 3. Verificar Calidad
```bash
# Ejecutar tests
./check_app.sh

# Verificar que la app funciona
flask run
# Probar en http://localhost:5000
```

### 4. Commit y Push
```bash
git add .
git commit -m "feat: descripción del cambio"
git push origin feature/nombre-caracteristica
```

### 5. Pull Request
- Crear PR con descripción detallada
- Incluir capturas si hay cambios visuales
- Referencias a issues relacionados

## 🐛 Reportar Bugs

### Información Necesaria
- Descripción del problema
- Pasos para reproducir
- Comportamiento esperado vs actual
- Versión de Python
- Sistema operativo
- Logs relevantes

### Formato
```markdown
**Descripción**
Descripción clara del bug

**Pasos para Reproducir**
1. Ir a '...'
2. Hacer click en '...'
3. Ver error

**Comportamiento Esperado**
Lo que debería suceder

**Comportamiento Actual**
Lo que sucede actualmente

**Entorno**
- Python: 3.10
- SO: macOS 14
- Flask: 2.x
```

## 💡 Proponer Mejoras

### Antes de Implementar
1. Verificar que no exista una issue similar
2. Crear una issue explicando la propuesta
3. Esperar feedback antes de empezar
4. Implementar tras aprobación

### En la Propuesta Incluir
- Problema que resuelve
- Solución propuesta
- Alternativas consideradas
- Impacto en código existente

## 📚 Recursos

- [Flask Documentation](https://flask.palletsprojects.com/)
- [pytest Documentation](https://docs.pytest.org/)
- [PEP 8 Style Guide](https://pep8.org/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)

## ❓ Ayuda

Si tienes preguntas:
- Revisar documentación existente
- Buscar en issues cerradas
- Crear nueva issue con tag `question`
- Contactar al maintainer: [@richionline](https://twitter.com/richionline)

## 📄 Licencia

Al contribuir, aceptas que tus contribuciones se licencian bajo la misma licencia del proyecto.
