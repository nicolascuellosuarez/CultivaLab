# **Guía de Instalación**

Esta guía te llevará paso a paso desde la obtención del código fuente de <span style="color: #6dbc19;">**CultivaLab**</span>, hasta su primera ejecución.

---

## **Requisitos Previos**

Antes de comenzar, asegúrate de tener instalado lo siguiente en tu sistema:

- ``Python 3.10`` o superior
- ``uv`` (gestor de proyectos Python)
- ``git``  (para clonar el repositorio)

Para verificar tu versión de Python, ejecuta en tu terminal:

```bash
python --version
```

### **Instalación de uv**

Si no tienes uv instalado, puedes instalarlo con el siguiente comando:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

O en Windows (dentro de WSL), usa:

```bash
wget -qO- https://astral.sh/uv/install.sh | bash
```

Después de la instalación, reinicia tu terminal o ejecuta:

```bash
source ~/.bashrc
```

Y finalmente, verifica la instalación:

```bash
uv --version
```

---

## **Clonar el Repositorio**

Para clonar el repositorio, utiliza el comando:

```bash
git clone https://github.com/tu-usuario/cultivalab.git
```

Y luego:

```bash
cd cultivalab
```

---

## **Instalar Dependencias**

Una vez dentro del directorio del proyecto, ejecuta:

```bash
uv sync
```

Este comando creará un entorno virtual e instalará todas las dependencias necesarias definidas en `pyproject.toml`, incluyendo:

- <span style="color: #6dbc19;">**typer**</span> para la interfaz de línea de comandos
- <span style="color: #6dbc19;">**rich**</span> para el formato visual en terminal
- <span style="color: #6dbc19;">**questionary**</span> para los menús interactivos
- <span style="color: #6dbc19;">**bcrypt**</span> para el hashing de contraseñas

---

## **Verificar la Instalación**

Para asegurarte de que todo está correcto, ejecuta las pruebas unitarias:

```bash
uv run pytest
```

Deberías ver una salida similar a esta:

<div style="display:flex; gap:20px;">
<div style="flex:1;">
<script 
src="https://asciinema.org/a/Qvcl1kjc37W8geam.js"
id="asciicast-Qvcl1kjc37W8geam"
data-rows="25"
data-cols="90"
data-font-size="16"
async>
</script>
</div>
</div>

---

## **Primera Ejecución**

Inicia la aplicación con el siguiente comando:

```bash
uv run python -m src.cultiva_lab.cli
```

y aparecerá el menú principal de <span style="color: #6dbc19;">**CultivaLab**</span>:

<div style="display:flex; gap:20px;">
<div style="flex:1;">
<script 
src="https://asciinema.org/a/LnXQYx5VLRLFJmXO.js"
id="asciicast-LnXQYx5VLRLFJmXO"
data-rows="25"
data-cols="90"
data-font-size="16"
async>
</script>
</div>
</div>

---

## **Registrar un Usuario**

1. Selecciona <span style="color: #6dbc19;">**Registrarse**</span> con las teclas de dirección.
2. Ingresa un <span style="color: #6dbc19;">**nombre de usuario**</span>.
3. Ingresa una <span style="color: #6dbc19;">**contraseña**</span> de al menos 8 caracteres.

<div style="display:flex; gap:20px;">
<div style="flex:1;">
<script 
src="https://asciinema.org/a/2rSXUMKGjkJnCWXc.js?t=0:03"
id="asciicast-2rSXUMKGjkJnCWXc"
data-rows="25"
data-cols="90"
data-font-size="16"
async>
</script>
</div>
</div>

---

## **Iniciar Sesión**

1. Selecciona <span style="color: #6dbc19;">**Iniciar sesión**</span>.
2. Ingresa tus credenciales.

Una vez dentro, accederás al menú de usuario con todas las opciones disponibles.

<div style="display:flex; gap:20px;">
<div style="flex:1;">
<script 
src="https://asciinema.org/a/8LsYEn5eRabriNb8.js?t=0:03"
id="asciicast-8LsYEn5eRabriNb8"
data-rows="25"
data-cols="90"
data-font-size="16"
async>
</script>
</div>
</div>

---

## **Registrar Administrador (Opcional)**

Si deseas tener un perfil de administrador (solo puede existir uno en todo el sistema):

1. En el menú principal, selecciona <span style="color: #6dbc19;">**Registrar administrador**</span>.
2. Ingresa la <span style="color: #6dbc19;">**clave maestra**</span> (por defecto es `admin12345`).
3. Define un nombre de usuario y contraseña.

<div style="display:flex; gap:20px;">
<div style="flex:1;">
<script 
src="https://asciinema.org/a/M7EIsDxxPKyUBWqE.js?t=0:03"
id="asciicast-M7EIsDxxPKyUBWqE"
data-rows="25"
data-cols="90"
data-font-size="16"
async>
</script>
</div>
</div>

---

## **Primeros Pasos con Cultivos**

### *1. Crear un cultivo*

Desde el menú de usuario, selecciona <span style="color: #6dbc19;">**Crear nuevo cultivo**</span>:

<div style="display:flex; gap:20px;">
<div style="flex:1;">
<script 
src="https://asciinema.org/a/ueWXOJkBz9Y6aF8W.js?t=0:10"
id="asciicast-ueWXOJkBz9Y6aF8W"
data-rows="25"
data-cols="90"
data-font-size="16"
async>
</script>
</div>
</div>

### *2. Simular un día*

Selecciona <span style="color: #6dbc19;">**Simular día en un cultivo**</span>:

<div style="display:flex; gap:20px;">
<div style="flex:1;">
<script 
src="https://asciinema.org/a/B9VewmUDtWaA4AGr.js?t=0:10"
id="asciicast-B9VewmUDtWaA4AGr"
data-rows="25"
data-cols="90"
data-font-size="16"
async>
</script>
</div>
</div>

---

## **Comandos Útiles para Desarrollo**

### *Formatear código*

```bash
uv run ruff format .
```

### *Verificar estilo*

```bash
uv run ruff check .
```

### *Ejecutar pruebas con cobertura*

```bash
uv run pytest --cov=src/cultiva_lab --cov-report=term
```

### Ver cobertura detallada

```bash
uv run pytest --cov=src/cultiva_lab --cov-report=html
# Luego abre htmlcov/index.html en tu navegador
```

---

## **Solución de Problemas**

### *Error: "No module named src.cultiva_lab"*

Asegúrate de estar en el directorio raíz del proyecto y haber ejecutado `uv sync`.

### *Error: "database.json not found"*

No te preocupes, el archivo se creará automáticamente al ejecutar la aplicación por primera vez.

### *Las pruebas fallan*

Verifica que tienes instaladas todas las dependencias de desarrollo:

```bash
uv sync --dev
```
