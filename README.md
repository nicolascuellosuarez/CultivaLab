# CultivaLab

Laboratorio Virtual para Simulación y Análisis de Cultivos

---

## Descripción General

CultivaLab es una aplicación de línea de comandos (CLI) diseñada para agricultura de precisión. Permite a investigadores y agricultores modelar el crecimiento de cultivos bajo diferentes condiciones ambientales, simulando el desarrollo día a día y generando estadísticas predictivas. El sistema implementa un modelo mecanicista basado en factores ambientales como temperatura, agua y luz, los cuales afectan directamente el desarrollo de la planta. La arquitectura del software es modular y escalable, permitiendo futuras expansiones como la integración con bases de datos externas o interfaces web.

---

## Propósito de la Aplicación

El propósito fundamental de CultivaLab es proporcionar una herramienta accesible desde la terminal para simular el crecimiento de cultivos en base a condiciones climáticas ingresadas por el usuario. Los usuarios pueden registrarse y autenticarse en el sistema, existiendo dos roles claramente diferenciados: usuario normal y administrador. Los usuarios normales pueden crear y gestionar sus propios cultivos, mientras que el administrador tiene la capacidad de gestionar los tipos de cultivo disponibles y visualizar información global de todos los usuarios. Adicionalmente, el sistema permite generar estadísticas detalladas sobre el crecimiento y rendimiento de cada cultivo, facilitando así la toma de decisiones agrícolas informadas.

---

## Estructura del Proyecto

El proyecto está organizado siguiendo una arquitectura limpia con separación de responsabilidades. En el directorio src/cultiva_lab se encuentran los módulos principales: cli.py que contiene la interfaz de usuario, models.py donde se definen las dataclasses del dominio, storage.py que maneja la persistencia en archivos JSON, services.py que implementa toda la lógica de negocio, y exceptions.py que define la jerarquía de excepciones personalizadas. El directorio tests alberga las pruebas unitarias que garantizan el correcto funcionamiento del sistema. Los datos persistentes se almacenan en data/database.json, mientras que la configuración del proyecto y sus dependencias se especifican en pyproject.toml. Adicionalmente, el directorio .github/workflows contiene la configuración para integración continua mediante GitHub Actions. Vea pues, la estructura del proyecto:

cultivalab/
├── src/
│   └── cultiva_lab/
│       ├── cli.py                 # Interfaz de usuario
│       ├── models.py               # Dataclasses del dominio
│       ├── storage.py               # Persistencia JSON
│       ├── services.py               # Lógica de negocio
│       ├── __init__.py               # Inicializador
│       └── exceptions.py             # Excepciones personalizadas
├── tests/                           # Pruebas unitarias
│    ├── __init__.py                     # Inicializador de tests
│    ├── test_services.py               # Tests a Servicios
│    └── test_storage.py                 # Tests al Storage
├── data/                             # Base de datos local
├── assets/                             # Elementos gráficos para la CLI 
│    ├── CultivaLab.png
│    └── Logo.png 
├── .github/workflows/                 # CI/CD con GitHub Actions
│    └── tests.yml
├── pyproject.toml                     # Configuración del proyecto
├── gitignore                     
└── README.md

---

## Requisitos del Sistema

Para ejecutar CultivaLab se necesita Python en su versión 3.10 o superior, así como el gestor de proyectos uv para manejar las dependencias. Todas las librerías necesarias están especificadas en el archivo pyproject.toml y se instalan automáticamente al ejecutar uv sync.

---

## Instalación y Configuración

El primer paso consiste en clonar el repositorio desde la URL correspondiente y acceder al directorio del proyecto. Una vez dentro, se debe ejecutar el comando 'uv sync' para instalar todas las dependencias necesarias. No se requiere configuración adicional, ya que la aplicación crea automáticamente los archivos de datos la primera vez que se ejecuta.

---

## Comandos de Uso

Para iniciar la aplicación, se utiliza el comando 'uv run python -m src.cultiva_lab.cli'. Este comando despliega el menú principal donde el usuario puede elegir entre iniciar sesión, registrarse como usuario normal, registrar un administrador (lo cual solo es posible una vez y requiere una clave maestra), o salir de la aplicación. La navegación por los menús se realiza mediante las teclas de dirección, y todas las opciones están claramente etiquetadas.

Para mantener la calidad del código, se dispone de comandos específicos. 'uv run ruff check .' permite verificar que el código cumple con los estándares de estilo definidos, mientras que 'uv run ruff format .' aplica automáticamente las correcciones de formato necesarias.

La ejecución de las pruebas unitarias se realiza con 'uv run pytest'. Para obtener información más detallada sobre cada prueba, se puede añadir el flag '-v'. Si se desea conocer el porcentaje de cobertura del código, se utiliza 'uv run pytest --cov=src/cultiva_lab'.

---

## Funcionalidades para Usuario Normal

Una vez que un usuario normal ha iniciado sesión, accede a un menú específico con múltiples opciones. Puede listar todos sus cultivos existentes, lo que muestra una tabla con el ID, nombre, tipo, días simulados y estado activo o cosechado. La creación de un nuevo cultivo requiere seleccionar un tipo de cultivo de entre los disponibles, asignar un nombre personalizado y opcionalmente especificar una fecha de inicio. El sistema valida que todos los datos ingresados sean correctos.

Para la simulación diaria, el usuario selecciona un cultivo activo e ingresa la temperatura, cantidad de lluvia y horas de sol del día. El sistema calcula automáticamente la nueva biomasa basándose en el modelo de crecimiento implementado, registra la condición diaria y actualiza la fecha de última simulación. Si el cultivo alcanza el final de su ciclo, se marca automáticamente como cosechado.

Las estadísticas de un cultivo muestran información valiosa como la temperatura promedio durante su ciclo, la lluvia promedio recibida, las horas de sol promedio, el crecimiento total en biomasa, la cantidad de días que el cultivo experimentó estrés térmico, y el porcentaje de rendimiento alcanzado respecto al potencial teórico del tipo de cultivo.

El sistema también permite buscar cultivos aplicando filtros. Se puede buscar por ID específico, por nombre utilizando coincidencias parciales, o por tipo de cultivo seleccionando de una lista. Los resultados se muestran en formato tabular para fácil lectura.

En cuanto a la gestión del perfil, el usuario puede cambiar su nombre de usuario siempre que el nuevo no esté ya registrado, actualizar su contraseña verificando primero la contraseña actual, o eliminar permanentemente su cuenta, lo cual requiere confirmación mediante la contraseña y elimina también todos sus cultivos asociados.

---

## Funcionalidades para Administrador

El administrador, después de iniciar sesión, tiene acceso a un conjunto ampliado de opciones. Puede listar todos los usuarios registrados en el sistema, visualizando para cada uno su ID, nombre de usuario, rol y cantidad de cultivos asociados. También tiene la capacidad de eliminar cualquier usuario, para lo cual se presenta una lista seleccionable de usuarios (excluyendo al propio administrador) mostrando además la cantidad de cultivos que serían eliminados. La operación requiere doble confirmación dada su naturaleza irreversible.

La gestión de tipos de cultivo es una responsabilidad exclusiva del administrador. Puede listar todos los tipos existentes con sus parámetros completos, crear nuevos tipos especificando nombre, temperatura óptima, agua necesaria por día, luz necesaria por día, duración del ciclo en días, biomasa inicial y rendimiento potencial. También puede editar tipos existentes, aunque el sistema impide la modificación si existen cultivos activos utilizando ese tipo. La eliminación de tipos de cultivo solo es posible cuando no hay ningún cultivo, activo o cosechado, que haga referencia a ellos.

Para la visualización de cultivos, el administrador puede seleccionar cualquier usuario y luego aplicar filtros como buscar por ID específico, por nombre, por tipo de cultivo, o filtrar para ver solo cultivos activos o solo cosechados. Esto facilita el monitoreo y la auditoría del sistema.

Las estadísticas globales presentan un resumen del estado general de la aplicación, incluyendo el número total de usuarios registrados, la cantidad total de cultivos creados, cuántos de ellos están actualmente activos, y el número de tipos de cultivo disponibles en el catálogo.

---

## Modelo de Crecimiento Implementado

El cálculo de la biomasa diaria se basa en la combinación de varios factores. El factor ambiental considera la temperatura real del día comparada con la temperatura óptima del cultivo, penalizando las desviaciones significativas. También evalúa si la lluvia recibida satisface el requerimiento hídrico del cultivo, y si las horas de sol alcanzan el mínimo necesario. El factor fenológico depende de la etapa del cultivo, con un crecimiento más lento al inicio y al final del ciclo, y más rápido durante la etapa vegetativa. Finalmente, el factor de capacidad de carga considera la biomasa actual respecto al rendimiento potencial, reduciendo el crecimiento a medida que el cultivo se acerca a su máximo teórico. La combinación de estos factores produce una estimación realista del crecimiento diario.

---

## Estructura de Datos y Persistencia

Los datos en CultivaLab se organizan en cuatro entidades principales. La entidad Usuario incluye un identificador único, nombre de usuario, contraseña hasheada mediante bcrypt, rol que puede ser USER o ADMIN, y una lista de IDs de los cultivos que posee. La entidad Tipo de Cultivo contiene nombre, temperatura óptima en grados Celsius, agua necesaria en milímetros por día, luz necesaria en horas por día, duración del ciclo en días, biomasa inicial al momento de la siembra, y rendimiento potencial en gramos por metro cuadrado. La entidad Cultivo registra un identificador único, nombre asignado por el usuario, ID del usuario propietario, ID del tipo de cultivo asociado, fechas de inicio y última simulación, lista de condiciones diarias, y un indicador de si está activo. La entidad Condición Diaria almacena el número de día, temperatura, lluvia, horas de sol, y la biomasa estimada para ese día específico.

Toda esta información se persiste en un único archivo JSON ubicado en data/database.json. El archivo contiene tres secciones principales: users para la lista de usuarios, crops para la lista de cultivos, y crop_types para los tipos de cultivo. La primera vez que se ejecuta la aplicación, si el archivo no existe, se crea automáticamente con las estructuras vacías correspondientes.

---

## Integración Continua y Calidad de Código

El proyecto incorpora GitHub Actions para garantizar la calidad del código en cada cambio. El workflow definido se ejecuta automáticamente ante cada push o pull request a la rama principal. Durante la ejecución, se instala el entorno necesario, se verifican los estándares de estilo mediante Ruff, y se ejecutan todas las pruebas unitarias con Pytest. Si alguna de estas etapas falla, el workflow lo indica claramente, permitiendo corregir los problemas antes de que el código sea integrado.

---

## Manejo de Errores y Excepciones

CultivaLab implementa una jerarquía completa de excepciones personalizadas para manejar de manera elegante las diferentes situaciones de error. Las excepciones relacionadas con usuarios incluyen UserNotFoundError cuando se busca un identificador inexistente, UserAlreadyExistsError al intentar registrar un nombre duplicado, y otras similares. Para autorización existen AuthorizationError, ResourceOwnershipError cuando se intenta acceder a recursos de otro usuario, y AdminAlreadyExistsError al intentar crear un segundo administrador. En el dominio de cultivos se tienen CropNotFoundError y CropTypeNotFoundError. Errores de validación se agrupan en InvalidInputError, mientras que violaciones de reglas de negocio como intentar editar un tipo con cultivos activos lanzan BusinessRuleViolationError. Esta estructura permite capturar errores específicos y mostrar mensajes claros al usuario.

---

## Contribución al Proyecto

Quienes deseen contribuir al desarrollo de CultivaLab pueden hacerlo mediante el flujo estándar de GitHub. Se recomienda realizar un fork del repositorio, crear una rama para la nueva funcionalidad, asegurarse de que todas las pruebas pasen y que el código cumpla con los estándares de formato antes de enviar un pull request. La documentación de las nuevas funcionalidades debe incluirse junto con el código.

---