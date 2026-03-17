# **CultivaLab**

<p align="center">
  <img src="assets/CultivaLab.png" alt="CultivaLab Logo" width="650"/>
</p>
  
<div align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue" alt="Python">
  <img src="https://img.shields.io/badge/Tests-73%20passing-brightgreen" alt="Tests">
  <img src="https://img.shields.io/badge/Coverage-92%25-green" alt="Coverage">
</div>

---

## **¿Qué es CultivaLab?**

**CultivaLab** es una aplicación de <span style="color: #6dbc19;">*línea de comandos*</span> diseñada para agricultura de precisión. Permite a investigadores y agricultores modelar el crecimiento de cultivos bajo diferentes condiciones ambientales, simulando el desarrollo día a día y generando estadísticas sobre el rendimiento. 

El sistema implementa un <span style="color: #6dbc19;">*modelo mecanicista*</span> basado en factores ambientales como <span style="color: #6dbc19;">**temperatura**</span>, <span style="color: #6dbc19;">**agua**</span> y <span style="color: #6dbc19;">**luz**</span>, los cuales afectan directamente el desarrollo de la planta. La arquitectura del software es modular y escalable, permitiendo futuras expansiones como la integración con bases de datos externas o interfaces web.

---

## **Objetivo de la App.**

El propósito fundamental de CultivaLab es proporcionar una herramienta accesible desde la terminal para simular el crecimiento de cultivos en base a condiciones climáticas ingresadas por el usuario. 
Los usuarios pueden registrarse y autenticarse en el sistema, existiendo dos roles claramente diferenciados: <span style="color: #6dbc19;">**usuario normal**</span> y <span style="color: #6dbc19;">**administrador**</span>. 

Los usuarios normales pueden crear y gestionar sus propios cultivos, mientras que el administrador tiene la capacidad de <span style="color: #6dbc19;">**gestionar los tipos de cultivo disponibles**</span> y visualizar información global de todos los usuarios. Adicionalmente, el sistema permite generar estadísticas detalladas sobre el crecimiento y rendimiento de cada cultivo, **facilitando así la toma de decisiones agrícolas informadas**.

---

## **Características Principales.**

El sistema implementa una arquitectura de usuarios con **roles diferenciados**, permitiendo separar claramente las responsabilidades entre <span style="color: #6dbc19;">**usuarios estándar**</span> y <span style="color: #6dbc19;">**administradores**</span>. Los usuarios normales pueden crear y gestionar sus propios cultivos dentro de la plataforma, mientras que el administrador mantiene el control del catálogo global de <span style="color: #6dbc19;">*tipos de cultivo*</span>, garantizando la consistencia de la información base del sistema.

<div style="display:flex; gap:20px;">
<div style="flex:1;">
<h3>Menú de Administrador</h3>
<script 
src="https://asciinema.org/a/ttnizKgi8QRBjeod.js"
id="asciicast-ttnizKgi8QRBjeod"
data-rows="25"
data-cols="90"
data-font-size="16"
async>
</script>
</div>
<div style="flex:1;">
<h3>Menú de Usuario</h3>
<script 
src="https://asciinema.org/a/z2rxAUVoVt88H1tN.js"
id="asciicast-z2rxAUVoVt88H1tN"
data-rows="25"
data-cols="90"
data-font-size="16"
async>
</script>
</div>
</div>

La plataforma también incorpora un <span style="color: #6dbc19;">**sistema de simulación diaria**</span> que permite registrar condiciones ambientales relevantes para el crecimiento de los cultivos. Entre estas variables se encuentran:

- <span style="color: #6dbc19;">**Temperatura**</span>
- <span style="color: #6dbc19;">**Precipitación (lluvia)**</span>
- <span style="color: #6dbc19;">**Horas de exposición solar**</span>

A partir de estos datos, el sistema calcula automáticamente la nueva <span style="color: #6dbc19;">*biomasa*</span> del cultivo utilizando un modelo matemático que tiene en cuenta múltiples factores agronómicos y ambientales, en específico, la <span style="color: #6dbc19;">*fase fenológica*</span> actual del cultivo, su <span style="color: #6dbc19;">*capacidad máxima de carga*</span>, la <span style="color: #6dbc19;">*desviación*</span> frente a las <span style="color: #6dbc19;">*condiciones ambientales óptimas*</span> y los factores de <span style="color: #6dbc19;">*estrés ambiental*</span> que afectan el desarrollo.

Como resultado de estas simulaciones, el sistema genera <span style="color: #6dbc19;">**estadísticas detalladas**</span> que permiten evaluar el comportamiento del cultivo a lo largo del tiempo. Por ejemplo, los respectivos promedios de las <span style="color: #6dbc19;">**condiciones ambientales**</span> registradas, el <span style="color: #6dbc19;">**crecimiento total**</span> acumulado de una planta, el número de días con <span style="color: #6dbc19;">**estrés térmico**</span> y la comparación del rendimiento real frente al potencial teórico esperado.

Adicionalmente a aplicación ofrece capacidades completas de <span style="color: #6dbc19;">**búsqueda y filtrado**</span>, permitiendo localizar cultivos por <span style="color: #704A1E;">*ID*</span>, <span style="color: #704A1E;">*nombre*</span> o <span style="color: #704A1E;">*tipo*</span>. Los usuarios pueden gestionar su perfil cambiando su nombre de usuario o contraseña, e incluso eliminar su cuenta si así lo desean. El administrador dispone de herramientas adicionales como *la gestión completa* de tipos de cultivo, visualización de todos los usuarios con sus respectivos cultivos, y estadísticas globales del sistema.

La persistencia de datos se realiza mediante archivos <span style="color: #6dbc19;">**JSON**</span>, lo que garantiza que toda la información se mantenga entre sesiones sin necesidad de configurar bases de datos externas. El código está respaldado por más de <span style="color: #6dbc19;">*setenta pruebas unitarias*</span> que garantizan su correcto funcionamiento, y se incluye un flujo de <span style="color: #6dbc19;">*integración continua*</span> mediante GitHub Actions que ejecuta automáticamente las pruebas y verifica el estilo del código en cada cambio.

---

## **Tecnologías Utilizadas.**

El proyecto está desarrollado en Python utilizando ``uv`` como gestor de dependencias. La interfaz de línea de comandos se construyó con la librería ``typer``, mientras que la presentación visual mejorada se logra mediante ``rich`` para tablas, paneles y colores. La navegación interactiva por menús se implementó con la librería ``questionary``, permitiendo selección mediante teclas de dirección. Para el **hashing** de contraseñas se emplea ``bcrypt``, garantizando la seguridad de las credenciales almacenadas.

En el aspecto de calidad de código, se utiliza ``ruff`` como linter y formateador, y ``myp`` para verificación estática de tipos. Las pruebas unitarias se ejecutan con ``pytest`` y finalmente, la integración continua está configurada con GitHub Actions, que ejecuta automáticamente las verificaciones en cada <span style="color: #6dbc19;">**push**</span> o <span style="color: #6dbc19;">**pull request**</span>.

---

## **Estructura del proyecto.**

El código fuente se organiza en el directorio ``src/cultiva_lab``, donde se encuentran los módulos principales. El archivo ``cli.py`` contiene la <span style="color: #6dbc19;">*interfaz de usuario*</span> con todos los menús interactivos. En ``models.py`` se definen las <span style="color: #6dbc19;">*dataclasses*</span> que representan las entidades del dominio como ``Usuario``, ``Cultivo``, ``Tipo de Cultivo`` y ``Condición Diaria``. La <span style="color: #6dbc19;">*lógica de negocio*</span> reside en ``services.py``, que implementa las operaciones y validaciones para cada entidad. El módulo ``storage.py`` maneja la **persistencia** mediante un patrón de repositorio con una implementación concreta en <span style="color: #6dbc19;">*JSON*</span>, mientras que ``exceptions.py`` define la jerarquía completa de <span style="color: #6dbc19;">*excepciones personalizadas*</span> utilizadas en toda la aplicación.

El directorio ``tests`` contiene las <span style="color: #6dbc19;">*pruebas unitarias*</span> organizadas por módulo, y la carpeta ``data`` almacena el archivo ``database.json`` que funciona como <span style="color: #6dbc19;">*base de datos local*</span>. La documentación se encuentra en el directorio ``docs``, construida con MkDocs y el tema Material para una presentación profesional.

    ´´
    cultivalab/
    ├── src/
    │   └── cultiva_lab/
    │       ├── cli.py
    │       ├── models.py
    │       ├── services.py
    │       ├── storage.py
    │       └── exceptions.py
    ├── tests/
    │   ├── __init__.py 
    │   ├── test_services.py
    │   └── test_storage.py
    ├── data/
    ├── docs/
    │   └── assets/
    │       ├── CultivaLab.png
    │       ├── CultivaLabLogo.png
    │       ├── CultivaLabLogo2.png
    │       ├── CultivaLabLogo3.png
    │       └── Logo.png
    │   └── stylesheets/
    │       └── extra.css
    │   └── index.md
    ├── .github/workflows/
    │   └── tests.yml
    ├── pyproject.toml
    ├── mkdocs.yml
    └── README.md
    ´´

---

## **Estado Actual del Proyecto.**
El proyecto se encuentra en su *versión inicial* con todas las funcionalidades principales implementadas y probadas. Los **modelos de dominio** están completos y correctamente definidos como dataclasses. La capa de persistencia funciona con archivos **JSON** y sigue el patrón de repositorio mediante un *protocolo abstracto*. Los servicios implementan toda la lógica de negocio con validaciones exhaustivas y manejo adecuado de excepciones. La interfaz de usuario es completamente funcional y permite realizar todas las *operaciones disponibles*. Se han ejecutado más de setenta pruebas unitarias con una cobertura superior al noventa por ciento, y el flujo de integración continua verifica automáticamente la calidad del código en cada cambio.