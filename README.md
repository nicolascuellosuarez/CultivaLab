# CultivaLab

CultivaLab es una plataforma completa para la simulación y análisis de crecimiento de cultivos. Integra una interfaz de línea de comandos interactiva, una API REST robusta y un panel de control web moderno para que investigadores y agricultores puedan modelar el desarrollo de plantas bajo diferentes condiciones ambientales.

El sistema implementa un modelo mecanicista basado en factores ambientales como temperatura, agua y luz, utilizando ecuaciones diferenciales para simular el crecimiento día a día. La arquitectura es modular y escalable, diseñada para entornos de producción real.

---

## Características Principales

### Modelo Científico de Crecimiento

El modelo matemático implementado incluye fotosíntesis dependiente de temperatura mediante una función gaussiana, factor hídrico mediante una sigmoide doble que penaliza tanto la falta como el exceso de agua, y factor lumínico mediante Michaelis-Menten para baja luminosidad y una gaussiana decreciente para el exceso. La respiración de mantenimiento sigue la ecuación de Arrhenius para modelar el efecto de la temperatura. La respiración de crecimiento es proporcional a la fotosíntesis. El balance hídrico considera evapotranspiración mediante el método de Hargreaves y drenaje cuando se supera la capacidad de campo. La logística generalizada controla la capacidad de carga, y existe un mecanismo de muerte por estrés prolongado.

### Sistema de Usuarios

Existen dos roles: usuario normal y administrador. El administrador es único en todo el sistema. La autenticación se realiza mediante JWT con cookies seguras. Los usuarios pueden registrarse, actualizar su perfil y eliminar su cuenta.

### Gestión de Cultivos

El administrador puede gestionar un catálogo de tipos de cultivo con parámetros científicos configurables. Los usuarios pueden realizar operaciones CRUD completas sobre sus cultivos, simular días ingresando condiciones ambientales, consultar el historial de condiciones, obtener estadísticas detalladas y buscar cultivos por ID, nombre o tipo.

### Panel de Control Web

El panel web incluye gráficas interactivas de evolución de biomasa utilizando Recharts, métricas de rendimiento y estrés, un modelo 3D simplificado con Three.js que muestra un cilindro que crece según la biomasa, y tablas dinámicas con filtros y paginación.

### API REST

La API cuenta con documentación automática disponible en la ruta /docs. Incluye endpoints para autenticación, usuarios, cultivos y tipos de cultivo. La persistencia se realiza en Supabase con PostgreSQL. El manejo de errores se realiza mediante excepciones personalizadas.

### Interfaz de Línea de Comandos

La CLI ofrece menús navegables con teclas de dirección utilizando Questionary, colores personalizados y tablas formateadas con Rich. Incluye las mismas funcionalidades que la versión web, ideal para automatización y uso en servidores.

---

## Tecnologías Utilizadas

### Backend

- Python 3.10+
- FastAPI para la API REST
- Typer para la CLI
- Rich para formato visual en terminal
- Questionary para menús interactivos
- bcrypt para hashing de contraseñas
- PyJWT para manejo de tokens
- Supabase (PostgreSQL) para persistencia
- Ruff como linter y formateador
- mypy para verificación estática de tipos
- pytest para pruebas unitarias

### Frontend Web

- Next.js 15 con App Router
- TypeScript
- Tailwind CSS
- Recharts para gráficas
- React Three Fiber para modelo 3D
- Lucide React para iconos

---

## Estructura del Proyecto

```
CultivaLab/
├── api/                          # API REST con FastAPI
│   ├── main.py                   # Punto de entrada de la API
│   ├── dependencies.py           # Dependencias y autenticación
│   ├── routers/                  # Endpoints por recurso
│   │   ├── auth.py               # Login, registro, registro admin
│   │   ├── users.py              # CRUD de usuarios
│   │   ├── crop_types.py         # CRUD de tipos de cultivo
│   │   └── crops.py              # CRUD de cultivos, simulación
│   └── schemas/                  # Modelos Pydantic
│       ├── auth.py
│       ├── user.py
│       ├── crop.py
│       └── crop_type.py
│
├── src/cultiva_lab/              # Lógica de negocio y dominio
│   ├── cli.py                    # CLI interactiva
│   ├── models.py                 # Dataclasses del dominio
│   ├── services.py               # Servicios (lógica de negocio)
│   ├── storage.py                # Protocolo Database + JSONStorage
│   ├── storage_for_supabase.py   # Implementación con Supabase
│   └── exceptions.py             # Excepciones personalizadas
│
├── frontend/                     # Aplicación web Next.js
│   ├── src/
│   │   ├── app/                  # Rutas y páginas
│   │   ├── components/           # Componentes reutilizables
│   │   ├── lib/                  # Utilidades y API client
│   │   └── config/               # Configuración de navegación
│   └── public/                   # Archivos estáticos
│
├── tests/                        # Pruebas unitarias
├── data/                         # Base de datos local (JSON)
├── docs/                         # Documentación MkDocs
├── .github/workflows/            # CI/CD con GitHub Actions
├── pyproject.toml                # Configuración del proyecto
├── mkdocs.yml                    # Configuración de documentación
└── README.md
```

---

## Instalación y Configuración

### Requisitos Previos

- Python 3.10 o superior
- Node.js 18.18 o superior
- uv (gestor de proyectos Python)
- Git

### Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/cultivalab.git
cd cultivalab
```

### Configurar el Backend

```bash
# Instalar dependencias
uv sync

# Configurar variables de entorno (crear archivo .env)
cp .env.example .env
# Editar .env con tus credenciales de Supabase y JWT_SECRET_KEY
```

### Configurar el Frontend

```bash
cd frontend
npm install
cp .env.local.example .env.local
# Editar .env.local con NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Configurar Supabase

1. Crear un proyecto en Supabase
2. Ejecutar las migraciones SQL (ver sección Base de Datos)
3. Configurar las variables de entorno en el archivo .env

---

## Ejecución

### Iniciar el Backend (API y CLI)

```bash
# Iniciar la API REST
uv run uvicorn api.main:app --reload --port 8000

# En otra terminal, iniciar la CLI
uv run python -m src.cultiva_lab.cli
```

### Iniciar el Frontend

```bash
cd frontend
npm run dev
```

La aplicación web estará disponible en http://localhost:3000

### Documentación de la API

Una vez que el backend esté corriendo, acceder a http://localhost:8000/docs para ver la documentación interactiva.

---

## Base de Datos

CultivaLab utiliza Supabase (PostgreSQL) como base de datos. Las tablas principales son:

### Tabla users

Almacena los usuarios del sistema con id (UUID), username único, password_hash, role (USER o ADMIN), y created_at.

### Tabla crop_types

Contiene los parámetros científicos de cada especie de cultivo. Incluye campos como optimal_temp, minimum_temp, maximum_temp, needed_water, needed_light, days_cycle, photosyntesis_max_rate, breathing_base_rate, activation_energy, y muchos otros parámetros del modelo de crecimiento.

### Tabla crops

Representa los cultivos concretos de cada usuario. Incluye id, name, user_id (clave foránea a users), crop_type_id (clave foránea a crop_types), start_date, last_sim_date, active, water_stored, consecutive_stress_days, y current_phase.

### Tabla daily_conditions

Registra las condiciones diarias de cada cultivo. Incluye id, crop_id (clave foránea a crops), day, temperature, rain, sun_hours, estimated_biomass, y created_at.

Las relaciones están definidas con claves foráneas y eliminación en cascada para mantener la integridad referencial.

---

## Modelo de Crecimiento

El modelo matemático implementado es un sistema de ecuaciones diferenciales que se resuelve numéricamente con el método de Euler usando paso diario.

### Fotosíntesis Bruta

La fotosíntesis bruta se calcula como el producto de la tasa máxima de fotosíntesis, la biomasa actual, los factores de estrés ambiental y el término logístico.

### Respiración de Crecimiento

Es una fracción de la fotosíntesis bruta que se pierde al construir nuevo tejido.

### Respiración de Mantenimiento

Sigue la ecuación de Arrhenius, dependiente de la biomasa y la temperatura.

### Crecimiento Neto

Es la diferencia entre la fotosíntesis bruta y la suma de ambas respiraciones.

### Balance Hídrico

El agua almacenada en el suelo se actualiza diariamente considerando lluvia, riego, evapotranspiración y drenaje.

### Factores de Estrés

Los factores de estrés térmico, hídrico y lumínico se calculan mediante funciones asintóticas que penalizan las desviaciones de las condiciones óptimas.

---

## Endpoints Principales de la API

### Autenticación

- POST /auth/register - Registrar usuario normal
- POST /auth/register-admin - Registrar administrador (requiere clave maestra)
- POST /auth/login - Iniciar sesión (devuelve token JWT)
- GET /auth/me - Obtener usuario actual

### Usuarios

- GET /users/me - Perfil propio
- PUT /users/me - Actualizar nombre de usuario
- PUT /users/me/password - Cambiar contraseña
- DELETE /users/me - Eliminar cuenta propia
- GET /users/ - Listar todos los usuarios (solo admin)
- GET /users/{user_id} - Obtener usuario por ID

### Tipos de Cultivo

- GET /crop-types/ - Listar todos los tipos
- GET /crop-types/{crop_type_id} - Obtener tipo por ID
- POST /crop-types/ - Crear nuevo tipo (solo admin)
- PUT /crop-types/{crop_type_id} - Actualizar tipo (solo admin)
- DELETE /crop-types/{crop_type_id} - Eliminar tipo (solo admin)

### Cultivos

- GET /crops/ - Listar cultivos del usuario
- GET /crops/{crop_id} - Obtener cultivo por ID
- POST /crops/ - Crear nuevo cultivo
- PUT /crops/{crop_id} - Actualizar cultivo
- DELETE /crops/{crop_id} - Eliminar cultivo
- POST /crops/{crop_id}/simulate - Simular un día
- GET /crops/{crop_id}/history - Historial de condiciones diarias
- GET /crops/{crop_id}/stats - Estadísticas del cultivo
- GET /crops/admin/all - Listar todos los cultivos (solo admin)

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

Verificar complejidad ciclomática:

```bash
uv run radon cc src -a
```

---

## CI/CD

El proyecto incluye GitHub Actions que ejecutan automáticamente:

- Ruff (linting y formato)
- mypy (verificación de tipos)
- pytest (pruebas unitarias)
- radon (complejidad ciclomática)
- Despliegue de documentación a GitHub Pages

En cada push o pull request a la rama main.

---

## Documentación

La documentación completa está disponible en https://tu-usuario.github.io/cultivalab/

Para generarla localmente:

```bash
mkdocs serve
```

---

## Contribución

1. Hacer fork del repositorio
2. Crear una rama para la nueva funcionalidad
3. Ejecutar las pruebas y el linter antes de hacer commit
4. Enviar un pull request
