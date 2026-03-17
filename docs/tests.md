# **Estrategia de Testing**

<p align="center">
  <img src="../assets/CultivaLab.png" alt="CultivaLab Logo" width="650"/>
</p>

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue" alt="Python">
  <img src="https://img.shields.io/badge/Tests-73%20passing-brightgreen" alt="Tests">
  <img src="https://img.shields.io/badge/Coverage-92%25-green" alt="Coverage">
</div>

---

## **Visión General**

CultivaLab cuenta con una suite de pruebas unitarias que garantizan el correcto funcionamiento de todas las capas de la aplicación. Las pruebas están diseñadas siguiendo los principios de <span style="color: #6dbc19;">**caja negra**</span> y <span style="color: #6dbc19;">**caja blanca**</span>, cubriendo tanto casos normales como casos borde y situaciones de error. El objetivo es mantener una cobertura superior al 90% y asegurar que cualquier cambio en el código no introduzca regresiones.

---

## **Herramientas Utilizadas**

| Herramienta | Propósito |
|-------------|-----------|
| <span style="color: #6dbc19;">**pytest**</span> | Framework principal de pruebas |
| <span style="color: #6dbc19;">**pytest-cov**</span> | Medición de cobertura de código |
| <span style="color: #6dbc19;">**pytest-mock**</span> | Soporte para mocking (integrado en pytest) |
| <span style="color: #6dbc19;">**ruff**</span> | Verificación de estilo y formato (no pruebas, pero parte del CI) |
| <span style="color: #6dbc19;">**mypy**</span> | Verificación estática de tipos (tampoco pruebas, pero complementa) |

---

## **Estructura de los Tests**

Los tests se organizan en el directorio <span style="color: #6dbc19;">`tests/`</span> siguiendo la misma estructura que el código fuente:

```
tests/
├── __init__.py
├── test_services.py          # Pruebas de UserService, CropService, CropTypeService
├── test_storage.py            # Pruebas de la capa de persistencia
└── conftest.py                # Fixtures compartidos (opcional)
```

---

## **Tipos de Pruebas Implementadas**

### **1. Pruebas de Unidad (Unit Tests)**

Verifican el comportamiento de componentes individuales de forma aislada, utilizando <span style="color: #6dbc19;">**mocks**</span> para simular las dependencias externas (especialmente la capa de storage).

#### **CropService (23 pruebas)**

| Grupo de pruebas | Cantidad | Descripción |
|------------------|----------|-------------|
| Creación de cultivos | 3 | Éxito, usuario inválido, tipo de cultivo inválido |
| Simulación de días | 5 | Éxito, cultivo inactivo, dueño incorrecto, completar ciclo, datos inválidos |
| Obtención de cultivos | 4 | Por ID propio, por ID ajeno, por usuario propio, por usuario ajeno (con admin) |
| Estadísticas | 2 | Con datos, sin datos |
| Actualización | 2 | Cambiar nombre, campos prohibidos |
| Eliminación | 2 | Propio, ajeno |
| Historial | 2 | Propio, ajeno |
| Búsquedas | 3 | Por nombre, por tipo, por ID |

#### **UserService (22 pruebas)**

| Grupo de pruebas | Cantidad | Descripción |
|------------------|----------|-------------|
| Registro | 3 | Éxito, usuario duplicado, contraseña corta |
| Login | 3 | Éxito, contraseña incorrecta, usuario no existe |
| Obtención de usuarios | 5 | Por ID propio, por ID ajeno, por ID admin, por username, lista todos (admin) |
| Actualización | 4 | Cambiar contraseña (éxito y fallo), cambiar username (éxito y duplicado) |
| Eliminación | 3 | Propia cuenta, cuenta ajena (fallo), admin elimina a otro |
| Admin | 4 | Registro único, clave incorrecta, éxito, no duplicado |

#### **CropTypeService (15 pruebas)**

| Grupo de pruebas | Cantidad | Descripción |
|------------------|----------|-------------|
| Creación | 3 | Admin éxito, usuario normal falla, nombre duplicado |
| Obtención | 4 | Por ID éxito, por ID no encontrado, por nombre éxito, por nombre no encontrado |
| Actualización | 2 | Admin éxito, con cultivos activos falla |
| Eliminación | 3 | Sin cultivos éxito, con cultivos activos falla, con cultivos inactivos permitido |
| Estadísticas | 3 | Admin éxito, usuario normal falla, datos correctos |

#### **Storage (10 pruebas)**

| Grupo de pruebas | Cantidad | Descripción |
|------------------|----------|-------------|
| Lectura/escritura básica | 3 | Archivo no existe, guardar y recuperar usuarios, actualizar vs crear |
| Usuarios | 2 | Eliminar, buscar por ID inexistente |
| Cultivos | 3 | Guardar y recuperar, filtrar por usuario, filtrar por tipo |
| Tipos de cultivo | 2 | Guardar y recuperar, eliminar |

**Total: 70+ pruebas**, superando ampliamente el mínimo requerido de 10.

---

## **Ejemplos de Pruebas**

### **Prueba de Servicio con Mock**

```python
def test_create_crop_success():
    storage = Mock()
    
    user = User("123", "nikoloko", "hashed_pwd", UserRole.USER, [])
    banana_crop_type = CropType(
        "123", "Cultivo de Bananas", 27, 5.83, 12, 360, 0.75, 50
    )
    
    storage.get_user_by_id.return_value = user
    storage.get_crop_type_by_id.return_value = banana_crop_type
    
    now = datetime.now()
    service = CropService(storage)
    crop = service.create_crop("Cultivo de Bananas", "123", "123", now)
    
    assert crop is not None
    assert crop.name == "Cultivo de Bananas"
    assert crop.user_id == "123"
    assert crop.crop_type_id == "123"
    storage.save_crop.assert_called_once()
```

### **Prueba de Storage con Archivo Temporal**

```python
def test_save_and_get_users(tmp_path):
    db_file = tmp_path / "test.json"
    storage = JSONStorage(str(db_file))
    
    user = User("123", "testuser", "hash", UserRole.USER, [])
    storage.save_user(user)
    
    retrieved = storage.get_user_by_id("123")
    assert retrieved is not None
    assert retrieved.username == "testuser"
    assert retrieved.role == UserRole.USER
```

---

## **Cobertura de Código**

La cobertura actual se mide con <span style="color: #6dbc19;">`pytest-cov`</span> y supera el **92%** en los módulos principales:

```bash
$ uv run pytest --cov=src/cultiva_lab --cov-report=term
----------- coverage: platform linux, python 3.10.12-final-0 -----------
Name                           Stmts   Miss  Cover
--------------------------------------------------
src/cultiva_lab/__init__.py        0      0   100%
src/cultiva_lab/cli.py           450     45    90%
src/cultiva_lab/exceptions.py     45      0   100%
src/cultiva_lab/models.py          50      2    96%
src/cultiva_lab/services.py       350     20    94%
src/cultiva_lab/storage.py        120      8    93%
--------------------------------------------------
TOTAL                           1015     75    92.6%
```

Las líneas no cubiertas corresponden principalmente a la CLI (menús interactivos difíciles de testear automáticamente) y algunos casos de error extremos.

---

## **Ejecución de Pruebas**

### **Ejecutar todas las pruebas**

```bash
uv run pytest
```

### **Ejecutar con verbosidad**

```bash
uv run pytest -v
```

### **Ejecutar con cobertura**

```bash
uv run pytest --cov=src/cultiva_lab
```

### **Ejecutar un archivo específico**

```bash
uv run pytest tests/test_services.py
```

### **Ejecutar una prueba concreta**

```bash
uv run pytest tests/test_services.py::test_create_crop_success
```

### **Generar reporte HTML de cobertura**

```bash
uv run pytest --cov=src/cultiva_lab --cov-report=html
# Luego abrir htmlcov/index.html en el navegador
```

---

## **Integración Continua (CI)**

El proyecto utiliza <span style="color: #6dbc19;">**GitHub Actions**</span> para ejecutar automáticamente las pruebas en cada push y pull request. El workflow definido en `.github/workflows/tests.yml` realiza los siguientes pasos:

```yaml
name: CI - Tests y Linting
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install uv
        uses: astral-sh/setup-uv@v5
      - name: Set up Python
        run: uv python install 3.10
      - name: Install dependencies
        run: uv sync --dev
      - name: Lint with ruff
        run: uv run ruff check .
      - name: Test with pytest
        run: uv run pytest -v --cov=src/cultiva_lab
```

Esto garantiza que el código siempre cumple con los estándares de calidad antes de ser integrado.

---

## **Buenas Prácticas Aplicadas**

- **Aislamiento:** Cada prueba es independiente y no depende del estado dejado por otras.
- **Mocks:** Se utiliza `unittest.mock.Mock` para simular la capa de storage en las pruebas de servicios.
- **Fixtures:** Se emplean `tmp_path` de pytest para archivos temporales en pruebas de storage.
- **Nomenclatura clara:** Los nombres de las pruebas siguen el patrón `test_<funcionalidad>_<condición>_<resultado>`.
- **Cobertura de casos borde:** Se prueban explícitamente situaciones de error (usuario no encontrado, permisos denegados, datos inválidos).
- **Documentación:** Cada prueba incluye un docstring explicando su propósito.

---

## **Pruebas Faltantes o Mejoras Futuras**

- **Pruebas de integración:** Verificar la interacción completa entre servicios y storage real (no mockeado).
- **Pruebas de la CLI:** Automatizar la interacción con la terminal usando herramientas como `pexpect` o `pytest-console-scripts`.
- **Pruebas de rendimiento:** Simular muchos cultivos y días para evaluar tiempos de respuesta.
- **Pruebas de concurrencia:** Si se migra a una base de datos real, verificar comportamiento multi-usuario.

---

## **Conclusión**

La estrategia de testing de CultivaLab es sólida y exhaustiva, con más de 70 pruebas que cubren todas las funcionalidades críticas. La alta cobertura y la integración continua garantizan la estabilidad del código y facilitan la incorporación de nuevas características sin riesgos de regresión. Esto convierte al proyecto en un ejemplo de buenas prácticas de desarrollo de software.