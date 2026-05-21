```markdown
# CultivaLab

Laboratorio Virtual para Simulación y Análisis de Cultivos

---

## Descripción General

CultivaLab es una aplicación de línea de comandos (CLI) diseñada para agricultura de precisión. Permite a investigadores y agricultores modelar el crecimiento de cultivos bajo diferentes condiciones ambientales, simulando el desarrollo día a día y generando estadísticas predictivas sobre el rendimiento esperado.

El sistema implementa un modelo mecanicista basado en factores ambientales como temperatura, agua y luz, los cuales afectan directamente el desarrollo de la planta. La arquitectura del software es modular y escalable, permitiendo futuras expansiones como la integración con bases de datos externas o interfaces web.

---

## Características Principales

- Sistema de usuarios con roles (USER y ADMIN)
- Catálogo de tipos de cultivo gestionado por administrador
- Creación y simulación de cultivos
- Modelo matemático de crecimiento basado en factores ambientales
- Estadísticas de rendimiento y estrés
- Persistencia en JSON o Supabase (PostgreSQL)
- CLI interactiva con navegación por teclado
- API REST con FastAPI
- 73+ pruebas unitarias con pytest

---

## Tecnologías Utilizadas

- Python 3.10+
- uv como gestor de dependencias
- Typer para la CLI
- Rich para formato visual en terminal
- Questionary para menús interactivos
- bcrypt para hashing de contraseñas
- Ruff como linter y formateador
- mypy para verificación estática de tipos
- pytest para pruebas unitarias
- FastAPI para la API REST
- Supabase (PostgreSQL) para persistencia en la nube

---

## Estructura del Proyecto

```text
CultivaLab/
├── api/
│   ├── __init__.py
│   ├── dependencies.py      # Dependencias de FastAPI (auth, servicios)
│   ├── main.py              # Aplicación FastAPI
│   ├── routers/             # Endpoints por recurso
│   │   ├── auth.py          # Login, registro, registro admin
│   │   ├── users.py         # CRUD de usuarios
│   │   ├── crop_types.py    # CRUD de tipos de cultivo
│   │   └── crops.py         # CRUD de cultivos, simulación, estadísticas
│   └── schemas/             # Modelos Pydantic (request/response)
│       ├── auth.py
│       ├── user.py
│       ├── crop.py
│       └── crop_type.py
├── data/
│   └── database.json        # Base de datos local (JSON)
├── src/
│   └── cultiva_lab/
│       ├── cli.py           # Interfaz de línea de comandos
│       ├── models.py        # Dataclasses del dominio
│       ├── services.py      # Lógica de negocio
│       ├── storage.py       # Protocolo Database + JSONStorage
│       ├── storage_for_supabase.py  # Implementación con Supabase
│       └── exceptions.py    # Excepciones personalizadas
├── tests/                   # Pruebas unitarias
├── docs/                    # Documentación MkDocs
├── pyproject.toml
├── mkdocs.yml
└── README.md
```

---

## Instalación

Clonar el repositorio e instalar dependencias:

```bash
git clone https://github.com/tu-usuario/cultivalab.git
cd cultivalab
uv sync
```

Configurar variables de entorno (crear archivo `.env`):

```text
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu_anon_key
JWT_SECRET_KEY=tu_clave_secreta_para_jwt
```

---

## Uso de la CLI

Iniciar la aplicación:

```bash
uv run python -m src.cultiva_lab.cli
```

Comandos disponibles dentro de la CLI (navegación con teclas de dirección):

- **Iniciar sesión**: Accede con usuario y contraseña
- **Registrarse**: Crea una nueva cuenta de usuario
- **Registrar administrador**: Crea el único administrador (requiere clave maestra `admin12345`)

Menú de Usuario Normal:

- **Mis cultivos**: Lista todos tus cultivos
- **Crear nuevo cultivo**: Selecciona un tipo de cultivo y asígnale un nombre
- **Buscar cultivos**: Por ID, nombre o tipo
- **Ver detalles de un cultivo**: Muestra información completa del historial
- **Simular día en un cultivo**: Ingresa temperatura, lluvia, horas de sol y riego opcional
- **Estadísticas de un cultivo**: Promedios, crecimiento total, días de estrés, rendimiento
- **Editar nombre de un cultivo**: Cambia el nombre asignado
- **Eliminar un cultivo**: Elimina el cultivo y todo su historial
- **Gestionar mi perfil**: Cambiar username, contraseña o eliminar cuenta

Menú de Administrador:

- **Listar todos los usuarios**: Muestra todos los usuarios registrados
- **Eliminar un usuario**: Selecciona un usuario de la lista para eliminarlo
- **Gestionar tipos de cultivo**: CRUD completo de tipos de cultivo
- **Ver cultivos de un usuario**: Visualiza los cultivos de cualquier usuario
- **Estadísticas globales**: Total de usuarios, cultivos, cultivos activos, tipos disponibles

---

## API REST con FastAPI

Iniciar el servidor:

```bash
uv run uvicorn api.main:app --reload --port 8000
```

Documentación interactiva: http://localhost:8000/docs

### Endpoints de Autenticación

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/auth/register` | Registrar usuario normal |
| POST | `/auth/register-admin` | Registrar administrador |
| POST | `/auth/login` | Iniciar sesión |
| GET | `/auth/me` | Obtener usuario actual |

### Endpoints de Usuarios

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/users/me` | Perfil propio |
| PUT | `/users/me` | Actualizar username |
| PUT | `/users/me/password` | Cambiar contraseña |
| DELETE | `/users/me` | Eliminar cuenta propia |
| GET | `/users/` | Listar todos los usuarios (admin) |
| GET | `/users/{user_id}` | Obtener usuario por ID |

### Endpoints de Tipos de Cultivo

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/crop-types/` | Listar todos los tipos |
| GET | `/crop-types/{crop_type_id}` | Obtener tipo por ID |
| POST | `/crop-types/` | Crear nuevo tipo (admin) |
| PUT | `/crop-types/{crop_type_id}` | Actualizar tipo (admin) |
| DELETE | `/crop-types/{crop_type_id}` | Eliminar tipo (admin) |

### Endpoints de Cultivos

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/crops/` | Listar cultivos del usuario |
| GET | `/crops/{crop_id}` | Obtener cultivo por ID |
| POST | `/crops/` | Crear nuevo cultivo |
| PUT | `/crops/{crop_id}` | Actualizar cultivo |
| DELETE | `/crops/{crop_id}` | Eliminar cultivo |
| POST | `/crops/{crop_id}/simulate` | Simular un día |
| GET | `/crops/{crop_id}/history` | Historial de condiciones |
| GET | `/crops/{crop_id}/stats` | Estadísticas del cultivo |

### Ejemplos de Uso

Registrar usuario:

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "agricultor1", "password": "password123"}'
```

Iniciar sesión:

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "agricultor1", "password": "password123"}'
```

Crear un cultivo (requiere token):

```bash
curl -X POST http://localhost:8000/crops/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <tu_token>" \
  -d '{"name": "Mi primer maíz", "crop_type_id": "uuid-del-tipo", "water_stored": 85.0}'
```

Simular un día:

```bash
curl -X POST "http://localhost:8000/crops/{crop_id}/simulate?temperature=25&rain=5&sun_hours=8&irrigation=0" \
  -H "Authorization: Bearer <tu_token>"
```

Obtener estadísticas:

```bash
curl -X GET http://localhost:8000/crops/{crop_id}/stats \
  -H "Authorization: Bearer <tu_token>"
```

---

## Persistencia de Datos

CultivaLab soporta dos modos de persistencia:

### JSONStorage (por defecto)

Los datos se guardan en `data/database.json`. No requiere configuración adicional.

### SupabaseStorage (recomendado para producción)

Para usar Supabase, configura las variables de entorno `SUPABASE_URL` y `SUPABASE_KEY` en el archivo `.env`. Luego, en `dependencies.py` se debe cambiar la instancia de `JSONStorage` por `SupabaseStorage`.

---

## Pruebas

Ejecutar todas las pruebas:

```bash
uv run pytest -v
```

Ejecutar pruebas con cobertura:

```bash
uv run pytest --cov=src/cultiva_lab
```

---

## Calidad del Código

Verificar estilo con Ruff:

```bash
uv run ruff check .
```

Aplicar formato automático:

```bash
uv run ruff format .
```

Verificar tipos con mypy:

```bash
uv run mypy src/
```

---

## Licencia

MIT
```