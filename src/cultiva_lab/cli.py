import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
import questionary
from questionary import Style
from datetime import datetime
from .storage import JSONStorage
from .services import CropService, UserService, CropTypeService
from .models import UserRole
from .exceptions import (
    UserNotFoundError,
    UserAlreadyExistsError,
    InvalidInputError,
    AuthorizationError,
    ResourceOwnershipError,
    CropNotFoundError,
    CropTypeNotFoundError,
    AdminAlreadyExistsError,
    UnauthorizedAccessError,
    BusinessRuleViolationError,
    DuplicateDataError,
)

VERDE = "#9bd353"
MARRON = "#704A1E"
BLANCO = "white"

custom_style = Style(
    [
        ("qmark", f"fg:{VERDE} bold"),
        ("question", "fg:white bold"),
        ("answer", f"fg:{MARRON} bold"),
        ("pointer", f"fg:{VERDE} bold"),
        ("highlighted", f"fg:{VERDE} bold"),
        ("selected", f"fg:{MARRON} bold"),
        ("separator", f"fg:{VERDE}"),
        ("instruction", "fg:gray"),
        ("text", "fg:white"),
        ("disabled", "fg:gray italic"),
    ]
)

console = Console()

LOGO = r"""
 ██████╗██╗   ██╗██╗     ████████╗██╗██╗   ██╗ █████╗ ██╗      █████╗ ██████╗ 
██╔════╝██║   ██║██║     ╚══██╔══╝██║██║   ██║██╔══██╗██║     ██╔══██╗██╔══██╗
██║     ██║   ██║██║        ██║   ██║██║   ██║███████║██║     ███████║██████╔╝
██║     ██║   ██║██║        ██║   ██║╚██╗ ██╔╝██╔══██║██║     ██╔══██║██╔══██╗
╚██████╗╚██████╔╝███████╗   ██║   ██║ ╚████╔╝ ██║  ██║███████╗██║  ██║██████╔╝
 ╚═════╝ ╚═════╝ ╚══════╝   ╚═╝   ╚═╝  ╚═══╝  ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═════╝ 

                ╔══════════════════════════════════════╗ ▓▒░
                ║    Laboratorio Virtual de Cultivos   ║ ▓▒░
                ╚══════════════════════════════════════╝ ▓▒░
"""


def print_logo():
    """Imprime el logo con colores."""
    logo_text = Text(LOGO)
    logo_text.stylize(f"bold {VERDE}", 0, len(LOGO))
    console.print(logo_text)


# Inicialización de servicios (usando JSONStorage)
storage = JSONStorage()
user_service = UserService(storage)
crop_service = CropService(storage)
crop_type_service = CropTypeService(storage, user_service)

# Variable global para el usuario logueado
current_user = None

app = typer.Typer(help="CultivaLab - CLI para agricultura de precisión")


def requiere_autenticacion(admin: bool = False):
    """Decorador para verificar autenticación y rol."""

    def decorator(func):
        def wrapper(*args, **kwargs):
            global current_user
            if current_user is None:
                console.print(
                    Panel("Debes iniciar sesión primero.", style=f"bold {MARRON}")
                )
                return
            if admin and current_user.role.value != UserRole.ADMIN.value:
                console.print(
                    Panel("Acceso solo para administradores.", style=f"bold {MARRON}")
                )
                return
            return func(*args, **kwargs)

        return wrapper

    return decorator


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """Punto de entrada principal. Muestra el menú interactivo."""
    if ctx.invoked_subcommand is not None:
        return  # Si se llamó a un subcomando, no mostrar menú
    menu_principal()


def menu_principal():
    """Bucle principal del menú interactivo."""
    global current_user
    print_logo()
    while True:
        if current_user is None:
            opcion = questionary.select(
                "Menú Principal",
                choices=[
                    "Iniciar sesión",
                    "Registrarse",
                    "Registrar administrador (solo una vez)",
                    "Salir",
                ],
                style=custom_style,
            ).ask()

            if opcion == "Iniciar sesión":
                login()
            elif opcion == "Registrarse":
                register()
            elif opcion == "Registrar administrador (solo una vez)":
                register_admin()
            elif opcion == "Salir":
                console.print(Panel("¡Hasta luego! 🌱", style=f"bold {VERDE}"))
                break
        else:
            # Menú según rol
            if current_user.role.value == UserRole.ADMIN.value:
                menu_admin()
            else:
                menu_user()


def login():
    global current_user
    username = questionary.text("Usuario:", style=custom_style).ask()
    password = questionary.password("Contraseña:", style=custom_style).ask()
    try:
        user = user_service.login(username, password)
        current_user = user
        console.print(Panel(f"Bienvenido {user.username}!", style=f"bold {VERDE}"))
    except (UserNotFoundError, AuthorizationError) as e:
        console.print(Panel(f"{str(e)}", style=f"bold {MARRON}"))


def register():
    username = questionary.text("Nombre de usuario:", style=custom_style).ask()
    password = questionary.password(
        "Contraseña (mínimo 8 caracteres):", style=custom_style
    ).ask()
    try:
        user = user_service.register_user(username, password)
        console.print(
            Panel(
                f"Usuario {user.username} registrado. Ahora puedes iniciar sesión.",
                style=f"bold {VERDE}",
            )
        )
    except (InvalidInputError, UserAlreadyExistsError) as e:
        console.print(Panel(f"{str(e)}", style=f"bold {MARRON}"))


def register_admin():
    admin_key = questionary.password(
        "Clave maestra de administrador:", style=custom_style
    ).ask()
    username = questionary.text("Nombre de usuario admin:", style=custom_style).ask()
    password = questionary.password(
        "Contraseña (mínimo 8 caracteres):", style=custom_style
    ).ask()
    try:
        admin = user_service.register_admin(admin_key, username, password)
        console.print(
            Panel(
                f"Administrador {admin.username} registrado. Ahora puedes iniciar sesión.",
                style=f"bold {VERDE}",
            )
        )
    except (AdminAlreadyExistsError, UnauthorizedAccessError, InvalidInputError) as e:
        console.print(Panel(f"{str(e)}", style=f"bold {MARRON}"))


def logout():
    global current_user
    current_user = None
    console.print(Panel("Sesión cerrada.", style=f"bold {VERDE}"))


def menu_user():
    while True:
        opcion = questionary.select(
            f"Menú de Usuario: {current_user.username}",
            choices=[
                "Mis cultivos",
                "Crear nuevo cultivo",
                "Buscar cultivos",
                "Ver detalles de un cultivo",
                "Simular día en un cultivo",
                "Estadísticas de un cultivo",
                "Editar nombre de un cultivo",
                "Eliminar un cultivo",
                "Gestionar mi perfil",
                "Cerrar sesión",
            ],
            style=custom_style,
        ).ask()

        if opcion == "Mis cultivos":
            listar_mis_cultivos()
        elif opcion == "Crear nuevo cultivo":
            crear_cultivo()
        elif opcion == "Buscar cultivos":
            menu_buscar_cultivos()
        elif opcion == "Ver detalles de un cultivo":
            ver_detalle_cultivo()
        elif opcion == "Simular día en un cultivo":
            simular_dia()
        elif opcion == "Estadísticas de un cultivo":
            ver_estadisticas()
        elif opcion == "Editar nombre de un cultivo":
            editar_cultivo()
        elif opcion == "Eliminar un cultivo":
            eliminar_cultivo()
        elif opcion == "Gestionar mi perfil":
            menu_gestionar_perfil()
        elif opcion == "Cerrar sesión":
            logout()
            break


def listar_mis_cultivos():
    try:
        crops = crop_service.get_crops_by_user(current_user.id, current_user.id)
        if not crops:
            console.print(Panel("No tienes cultivos aún.", style=f"bold {MARRON}"))
            return
        table = Table(
            title="Mis Cultivos", title_style=f"bold {VERDE}", border_style=VERDE
        )
        table.add_column("ID", style="cyan")
        table.add_column("Nombre", style="white")
        table.add_column("Tipo", style="white")
        table.add_column("Días", style="white")
        table.add_column("Activo", style="white")
        for c in crops:
            crop_type = crop_type_service.get_crop_type_by_id(c.crop_type_id)
            tipo_nombre = crop_type.name if crop_type else "Desconocido"
            dias = len(c.conditions)
            activo = "✓" if c.active else "x"
            table.add_row(c.id, c.name, tipo_nombre, str(dias), activo)
        console.print(table)
    except Exception as e:
        console.print(Panel(f"Error: {str(e)}", style=f"bold {MARRON}"))


def crear_cultivo():
    # Listar tipos de cultivo disponibles
    tipos = crop_type_service.get_crop_types()
    if not tipos:
        console.print(
            Panel(
                "No hay tipos de cultivo disponibles. Contacta al administrador.",
                style=f"bold {MARRON}",
            )
        )
        return
    opciones_tipo = [
        f"{t.name} (temp {t.optimal_temp}°C, agua {t.needed_water}mm, luz {t.needed_light}h)"
        for t in tipos
    ]
    tipo_elegido = questionary.select(
        "Selecciona el tipo de cultivo:", choices=opciones_tipo, style=custom_style
    ).ask()
    idx = opciones_tipo.index(tipo_elegido)
    crop_type = tipos[idx]

    nombre = questionary.text("Nombre de tu cultivo:", style=custom_style).ask()
    fecha_str = questionary.text(
        "Fecha de inicio (YYYY-MM-DD) o Enter para hoy:", style=custom_style
    ).ask()
    if fecha_str:
        try:
            start_date = datetime.strptime(fecha_str, "%Y-%m-%d")
        except ValueError:
            console.print(
                Panel(
                    "Formato de fecha inválido. Usando fecha actual.",
                    style=f"bold {MARRON}",
                )
            )
            start_date = datetime.now()
    else:
        start_date = datetime.now()

    try:
        crop = crop_service.create_crop(
            nombre, crop_type.id, current_user.id, start_date
        )
        console.print(
            Panel(
                f"Cultivo '{crop.name}' creado con ID {crop.id}",
                style=f"bold {VERDE}",
            )
        )
    except (InvalidInputError, UserNotFoundError, CropTypeNotFoundError) as e:
        console.print(Panel(f"{str(e)}", style=f"bold {MARRON}"))


def seleccionar_cultivo_propio(mensaje="Selecciona un cultivo:"):
    crops = crop_service.get_crops_by_user(current_user.id, current_user.id)
    if not crops:
        console.print(Panel("No tienes cultivos.", style=f"bold {MARRON}"))
        return None
    opciones = [f"{c.name} (ID: {c.id})" for c in crops]
    elegido = questionary.select(mensaje, choices=opciones, style=custom_style).ask()
    idx = opciones.index(elegido)
    return crops[idx]


def ver_detalle_cultivo():
    crop = seleccionar_cultivo_propio()
    if not crop:
        return
    # Mostrar información en panel
    info = f"""
    [bold]Nombre:[/bold] {crop.name}
    [bold]ID:[/bold] {crop.id}
    [bold]Tipo:[/bold] {crop_type_service.get_crop_type_by_id(crop.crop_type_id).name}
    [bold]Fecha inicio:[/bold] {crop.start_date.strftime("%Y-%m-%d")}
    [bold]Última simulación:[/bold] {crop.last_sim_date.strftime("%Y-%m-%d")}
    [bold]Días simulados:[/bold] {len(crop.conditions)}
    [bold]Activo:[/bold] {"Sí" if crop.active else "No"}
    """
    panel = Panel(
        Text.from_markup(info), title="Detalle del Cultivo", border_style=VERDE
    )
    console.print(panel)

    # Mostrar últimas condiciones si existen
    if crop.conditions:
        table = Table(
            title="Historial de condiciones",
            title_style=f"bold {VERDE}",
            border_style=VERDE,
        )
        table.add_column("Día", style="cyan")
        table.add_column("Temp (°C)", style="white")
        table.add_column("Lluvia (mm)", style="white")
        table.add_column("Sol (h)", style="white")
        table.add_column("Biomasa (g/m²)", style="white")
        for cond in crop.conditions[-10:]:  # últimas 10
            table.add_row(
                str(cond.day),
                str(cond.temperature),
                str(cond.rain),
                str(cond.sun_hours),
                f"{cond.estimated_biomass:.2f}",
            )
        console.print(table)


def simular_dia():
    crop = seleccionar_cultivo_propio("Selecciona el cultivo a simular:")
    if not crop:
        return
    if not crop.active:
        console.print(Panel("Este cultivo ya está cosechado.", style=f"bold {MARRON}"))
        return

    # Ingresar datos del día
    temp = questionary.text("Temperatura del día (°C):", style=custom_style).ask()
    rain = questionary.text("Lluvia (mm):", style=custom_style).ask()
    sun = questionary.text("Horas de sol:", style=custom_style).ask()

    try:
        temp_f = float(temp)
        rain_f = float(rain)
        sun_f = float(sun)
        updated_crop = crop_service.simulate_day(
            crop.id, current_user.id, temp_f, rain_f, sun_f
        )
        console.print(
            Panel(
                f"Día {len(updated_crop.conditions)} simulado. Nueva biomasa: {updated_crop.conditions[-1].estimated_biomass:.2f} g/m²",
                style=f"bold {VERDE}",
            )
        )
    except (InvalidInputError, ResourceOwnershipError, CropNotFoundError) as e:
        console.print(Panel(f"{str(e)}", style=f"bold {MARRON}"))
    except ValueError:
        console.print(Panel("Valores numéricos inválidos.", style=f"bold {MARRON}"))


def ver_estadisticas():
    crop = seleccionar_cultivo_propio()
    if not crop:
        return
    try:
        stats = crop_service.get_crop_statistics(crop.id, current_user.id)
        panel = Panel(
            f"""
    [bold]Temperatura promedio:[/bold] {stats["average_temperature"]:.2f} °C
    [bold]Lluvia promedio:[/bold] {stats["average_rain"]:.2f} mm
    [bold]Horas sol promedio:[/bold] {stats["average_sun_hours"]:.2f} h
    [bold]Crecimiento total:[/bold] {stats["total_growth"]:.2f} g/m²
    [bold]Días de estrés:[/bold] {stats["stress_days"]}
    [bold]Rendimiento vs potencial:[/bold] {stats["performance_ratio"] * 100:.1f}%
            """,
            title=f"Estadísticas de {crop.name}",
            border_style=VERDE,
        )
        console.print(panel)
    except Exception as e:
        console.print(Panel(f"Error: {str(e)}", style=f"bold {MARRON}"))


def editar_cultivo():
    crop = seleccionar_cultivo_propio("Selecciona el cultivo a editar:")
    if not crop:
        return
    nuevo_nombre = questionary.text(
        "Nuevo nombre (dejar vacío para no cambiar):", style=custom_style
    ).ask()
    if nuevo_nombre and nuevo_nombre.strip():
        try:
            updated = crop_service.update_crops(
                crop.id, current_user.id, name=nuevo_nombre.strip()
            )
            console.print(
                Panel(f"Nombre cambiado a '{updated.name}'", style=f"bold {VERDE}")
            )
        except (InvalidInputError, ResourceOwnershipError) as e:
            console.print(Panel(f"{str(e)}", style=f"bold {MARRON}"))


def eliminar_cultivo():
    crop = seleccionar_cultivo_propio("Selecciona el cultivo a eliminar:")
    if not crop:
        return
    confirm = questionary.confirm(f"¿Estás seguro de eliminar '{crop.name}'?").ask()
    if confirm:
        try:
            crop_service.delete_crop(crop.id, current_user.id)
            console.print(Panel("Cultivo eliminado.", style=f"bold {VERDE}"))
        except (ResourceOwnershipError, CropNotFoundError) as e:
            console.print(Panel(f"{str(e)}", style=f"bold {MARRON}"))


def menu_buscar_cultivos():
    """Menú para buscar cultivos por diferentes criterios."""
    opcion = questionary.select(
        "Buscar cultivos por:",
        choices=["Por ID", "Por nombre", "Por tipo de cultivo", "Ver todos", "Volver"],
        style=custom_style,
    ).ask()

    if opcion == "Por ID":
        buscar_cultivo_por_id()
    elif opcion == "Por nombre":
        buscar_cultivo_por_nombre()
    elif opcion == "Por tipo de cultivo":
        buscar_cultivo_por_tipo()
    elif opcion == "Ver todos":
        listar_mis_cultivos()


def buscar_cultivo_por_id():
    """Buscar un cultivo específico por su ID."""
    crop_id = questionary.text("ID del cultivo:", style=custom_style).ask()
    if not crop_id:
        return

    try:
        crop = crop_service.get_crop_by_id(crop_id, current_user.id)
        mostrar_detalle_cultivo_completo(crop)
    except (CropNotFoundError, ResourceOwnershipError) as e:
        console.print(Panel(f"{str(e)}", style=f"bold {MARRON}"))


def buscar_cultivo_por_nombre():
    """Buscar cultivos por nombre (búsqueda parcial)."""
    nombre = questionary.text("Nombre (o parte del nombre):", style=custom_style).ask()
    if not nombre:
        return

    nombre_busqueda = nombre.lower()
    crops = crop_service.get_crops_by_user(current_user.id, current_user.id)
    resultados = [c for c in crops if nombre_busqueda in c.name.lower()]

    if not resultados:
        console.print(
            Panel(f"No se encontraron cultivos con '{nombre}'.", style=f"bold {MARRON}")
        )
        return

    table = Table(
        title=f"Resultados para '{nombre}'",
        title_style=f"bold {VERDE}",
        border_style=VERDE,
    )
    table.add_column("ID", style="cyan")
    table.add_column("Nombre", style="white")
    table.add_column("Tipo", style="white")
    table.add_column("Días", style="white")
    table.add_column("Activo", style="white")

    for c in resultados:
        tipo = crop_type_service.get_crop_type_by_id(c.crop_type_id)
        tipo_nombre = tipo.name if tipo else "Desconocido"
        table.add_row(
            c.id, c.name, tipo_nombre, str(len(c.conditions)), "✓" if c.active else "x"
        )
    console.print(table)


def buscar_cultivo_por_tipo():
    """Buscar cultivos por tipo de cultivo."""
    tipos = crop_type_service.get_crop_types()
    if not tipos:
        console.print(
            Panel("No hay tipos de cultivo disponibles.", style=f"bold {MARRON}")
        )
        return

    opciones = [t.name for t in tipos]
    opciones.append("Volver")

    tipo_elegido = questionary.select(
        "Selecciona tipo de cultivo:", choices=opciones, style=custom_style
    ).ask()

    if tipo_elegido == "Volver":
        return

    tipo_obj = next((t for t in tipos if t.name == tipo_elegido), None)
    if not tipo_obj:
        return

    crops = crop_service.get_crops_by_user(current_user.id, current_user.id)
    resultados = [c for c in crops if c.crop_type_id == tipo_obj.id]

    if not resultados:
        console.print(
            Panel(f"No tienes cultivos de tipo {tipo_elegido}.", style=f"bold {MARRON}")
        )
        return

    table = Table(
        title=f"Cultivos de tipo {tipo_elegido}",
        title_style=f"bold {VERDE}",
        border_style=VERDE,
    )
    table.add_column("ID", style="cyan")
    table.add_column("Nombre", style="white")
    table.add_column("Días", style="white")
    table.add_column("Biomasa actual", style="white")
    table.add_column("Activo", style="white")

    for c in resultados:
        biomasa = c.conditions[-1].estimated_biomass if c.conditions else 0
        table.add_row(
            c.id,
            c.name,
            str(len(c.conditions)),
            f"{biomasa:.2f}",
            "✓" if c.active else "x",
        )
    console.print(table)


def mostrar_detalle_cultivo_completo(crop):
    """Muestra información detallada de un cultivo."""
    info = f"""
    [bold]Nombre:[/bold] {crop.name}
    [bold]ID:[/bold] {crop.id}
    [bold]Tipo:[/bold] {crop_type_service.get_crop_type_by_id(crop.crop_type_id).name}
    [bold]Fecha inicio:[/bold] {crop.start_date.strftime("%Y-%m-%d")}
    [bold]Última simulación:[/bold] {crop.last_sim_date.strftime("%Y-%m-%d")}
    [bold]Días simulados:[/bold] {len(crop.conditions)}
    [bold]Activo:[/bold] {"Sí" if crop.active else "No"}
    """
    panel = Panel(
        Text.from_markup(info), title="Detalle del Cultivo", border_style=VERDE
    )
    console.print(panel)

    if crop.conditions:
        ultima = crop.conditions[-1]
        console.print(
            Panel(
                f"Última biomasa: [bold]{ultima.estimated_biomass:.2f}[/bold] g/m² (día {ultima.day})",
                style=VERDE,
            )
        )


def menu_gestionar_perfil():
    """Menú para que el usuario gestione su perfil."""
    while True:
        opcion = questionary.select(
            f"Perfil de {current_user.username}",
            choices=[
                "Cambiar nombre de usuario",
                "Cambiar contraseña",
                "Eliminar mi cuenta",
                "Volver",
            ],
            style=custom_style,
        ).ask()

        if opcion == "Cambiar nombre de usuario":
            cambiar_username()
        elif opcion == "Cambiar contraseña":
            cambiar_password()
        elif opcion == "Eliminar mi cuenta":
            eliminar_mi_cuenta()
        elif opcion == "Volver":
            break


def cambiar_username():
    """Cambiar el nombre de usuario."""
    nuevo = questionary.text("Nuevo nombre de usuario:", style=custom_style).ask()
    if not nuevo or not nuevo.strip():
        console.print(Panel("El nombre no puede estar vacío.", style=f"bold {MARRON}"))
        return

    try:
        user_service.update_username(current_user.id, nuevo.strip(), current_user.id)
        current_user.username = nuevo.strip()
        console.print(Panel(f"Username actualizado a '{nuevo}'", style=f"bold {VERDE}"))
    except (UserAlreadyExistsError, ResourceOwnershipError, InvalidInputError) as e:
        console.print(Panel(f"{str(e)}", style=f"bold {MARRON}"))


def cambiar_password():
    """Cambiar la contraseña del usuario."""
    old = questionary.password("Contraseña actual:", style=custom_style).ask()
    new = questionary.password(
        "Nueva contraseña (mínimo 8 caracteres):", style=custom_style
    ).ask()
    confirm = questionary.password(
        "Confirmar nueva contraseña:", style=custom_style
    ).ask()

    if not old or not new:
        console.print(
            Panel("Las contraseñas no pueden estar vacías.", style=f"bold {MARRON}")
        )
        return

    if new != confirm:
        console.print(Panel("Las contraseñas no coinciden.", style=f"bold {MARRON}"))
        return

    try:
        user_service.update_password(current_user.id, old, new)
        console.print(Panel("Contraseña actualizada.", style=f"bold {VERDE}"))
    except (AuthorizationError, InvalidInputError, UserNotFoundError) as e:
        console.print(Panel(f"{str(e)}", style=f"bold {MARRON}"))


def eliminar_mi_cuenta():
    global current_user  # ← DEBE IR AL PRINCIPIO DE LA FUNCIÓN
    """Eliminar la propia cuenta del usuario."""
    console.print(
        Panel(
            "[bold]ADVERTENCIA:[/bold] Esta acción eliminará permanentemente tu cuenta y todos tus cultivos.",
            style=f"bold {MARRON}",
        )
    )

    confirm = questionary.confirm(
        f"¿Estás SEGURO de eliminar tu cuenta '{current_user.username}'?", default=False
    ).ask()

    if not confirm:
        return

    password = questionary.password(
        "Ingresa tu contraseña para confirmar:", style=custom_style
    ).ask()

    try:
        # Verificar contraseña
        user_service.login(current_user.username, password)
        # Eliminar cuenta
        user_service.delete_user(current_user.id, current_user.id)
        console.print(Panel("Tu cuenta ha sido eliminada.", style=f"bold {VERDE}"))

        current_user = None
    except (AuthorizationError, UserNotFoundError) as e:
        console.print(Panel(f"{str(e)}", style=f"bold {MARRON}"))


def ver_cultivos_usuario_con_filtros():
    """Admin puede ver cultivos de usuarios con filtros."""
    users = user_service.get_all_users(current_user.id)
    if not users:
        console.print(Panel("No hay usuarios.", style=f"bold {MARRON}"))
        return

    opciones = [f"{u.username} (ID: {u.id})" for u in users]
    opciones.append("Volver")

    elegido = questionary.select(
        "Selecciona un usuario:", choices=opciones, style=custom_style
    ).ask()

    if elegido == "Volver":
        return

    idx = opciones.index(elegido)
    target_user = users[idx]

    filtro = questionary.select(
        f"Filtrar cultivos de {target_user.username}:",
        choices=[
            "Todos",
            "Por ID",
            "Por nombre",
            "Por tipo",
            "Solo activos",
            "Solo cosechados",
            "Volver",
        ],
        style=custom_style,
    ).ask()

    if filtro == "Volver":
        return

    crops = crop_service.get_crops_by_user(target_user.id, current_user.id)

    if filtro == "Por ID":
        crop_id = questionary.text("ID del cultivo:", style=custom_style).ask()
        if crop_id:
            crops = [c for c in crops if c.id == crop_id]
    elif filtro == "Por nombre":
        nombre = questionary.text("Nombre (o parte):", style=custom_style).ask()
        if nombre:
            nombre_lower = nombre.lower()
            crops = [c for c in crops if nombre_lower in c.name.lower()]
    elif filtro == "Por tipo":
        tipos = crop_type_service.get_crop_types()
        if tipos:
            opciones_tipo = [t.name for t in tipos]
            tipo_elegido = questionary.select(
                "Tipo:", choices=opciones_tipo, style=custom_style
            ).ask()
            tipo_obj = next(t for t in tipos if t.name == tipo_elegido)
            crops = [c for c in crops if c.crop_type_id == tipo_obj.id]
    elif filtro == "Solo activos":
        crops = [c for c in crops if c.active]
    elif filtro == "Solo cosechados":
        crops = [c for c in crops if not c.active]

    if not crops:
        console.print(Panel("No se encontraron cultivos.", style=f"bold {MARRON}"))
        return

    table = Table(
        title=f"Cultivos de {target_user.username}",
        title_style=f"bold {VERDE}",
        border_style=VERDE,
    )
    table.add_column("ID", style="cyan")
    table.add_column("Nombre", style="white")
    table.add_column("Tipo", style="white")
    table.add_column("Días", style="white")
    table.add_column("Biomasa", style="white")
    table.add_column("Activo", style="white")

    for c in crops:
        tipo = crop_type_service.get_crop_type_by_id(c.crop_type_id)
        tipo_nombre = tipo.name if tipo else "?"
        biomasa = c.conditions[-1].estimated_biomass if c.conditions else 0
        table.add_row(
            c.id,
            c.name,
            tipo_nombre,
            str(len(c.conditions)),
            f"{biomasa:.2f}",
            "✓" if c.active else "x",
        )
    console.print(table)


def menu_admin():
    while True:
        opcion = questionary.select(
            f"Menú de Administrador: {current_user.username}",
            choices=[
                "Listar todos los usuarios",
                "Eliminar un usuario",
                "Gestionar tipos de cultivo",
                "Ver cultivos de un usuario (con filtros)",
                "Estadísticas globales",
                "Cerrar sesión",
            ],
            style=custom_style,
        ).ask()

        if opcion == "Listar todos los usuarios":
            listar_usuarios()
        elif opcion == "Eliminar un usuario":
            eliminar_usuario_admin()
        elif opcion == "Gestionar tipos de cultivo":
            menu_gestion_crop_types()
        elif opcion == "Ver cultivos de un usuario (con filtros)":
            ver_cultivos_usuario_con_filtros()
        elif opcion == "Estadísticas globales":
            ver_estadisticas_globales()
        elif opcion == "Cerrar sesión":
            logout()
            break


def listar_usuarios():
    try:
        users = user_service.get_all_users(current_user.id)
        table = Table(
            title="Usuarios registrados",
            title_style=f"bold {VERDE}",
            border_style=VERDE,
        )
        table.add_column("ID", style="cyan")
        table.add_column("Username", style="white")
        table.add_column("Rol", style="white")
        table.add_column("# Cultivos", style="white")
        for u in users:
            crops = crop_service.get_crops_by_user(u.id, current_user.id)
            table.add_row(u.id, u.username, u.role.value, str(len(crops)))
        console.print(table)
    except ResourceOwnershipError:
        console.print(Panel("No tienes permisos.", style=f"bold {MARRON}"))


def menu_gestion_crop_types():
    while True:
        opcion = questionary.select(
            "Gestión de Tipos de Cultivo",
            choices=[
                "Listar tipos",
                "Crear nuevo tipo",
                "Editar tipo",
                "Eliminar tipo",
                "Estadísticas por tipo",
                "Volver",
            ],
            style=custom_style,
        ).ask()

        if opcion == "Listar tipos":
            listar_crop_types()
        elif opcion == "Crear nuevo tipo":
            crear_crop_type()
        elif opcion == "Editar tipo":
            editar_crop_type()
        elif opcion == "Eliminar tipo":
            eliminar_crop_type()
        elif opcion == "Estadísticas por tipo":
            ver_estadisticas_tipos()
        elif opcion == "Volver":
            break


def listar_crop_types():
    tipos = crop_type_service.get_crop_types()
    if not tipos:
        console.print(Panel("No hay tipos de cultivo.", style=f"bold {MARRON}"))
        return
    table = Table(
        title="Tipos de Cultivo", title_style=f"bold {VERDE}", border_style=VERDE
    )
    table.add_column("ID", style="cyan")
    table.add_column("Nombre", style="white")
    table.add_column("Temp ópt", style="white")
    table.add_column("Agua nec", style="white")
    table.add_column("Luz nec", style="white")
    table.add_column("Ciclo (días)", style="white")
    table.add_column("Biomasa ini", style="white")
    table.add_column("Potencial", style="white")
    for t in tipos:
        table.add_row(
            t.id,
            t.name,
            str(t.optimal_temp),
            str(t.needed_water),
            str(t.needed_light),
            str(t.days_cycle),
            str(t.initial_biomass),
            str(t.potential_performance),
        )
    console.print(table)


def crear_crop_type():
    name = questionary.text("Nombre del tipo:", style=custom_style).ask()
    try:
        optimal_temp = float(
            questionary.text("Temperatura óptima (°C):", style=custom_style).ask()
        )
        needed_water = float(
            questionary.text("Agua necesaria (mm/día):", style=custom_style).ask()
        )
        needed_light = float(
            questionary.text("Luz necesaria (horas/día):", style=custom_style).ask()
        )
        days_cycle = int(questionary.text("Días de ciclo:", style=custom_style).ask())
        initial_biomass = float(
            questionary.text("Biomasa inicial (g/m²):", style=custom_style).ask()
        )
        potential = float(
            questionary.text("Rendimiento potencial (g/m²):", style=custom_style).ask()
        )

        nuevo = crop_type_service.create_crop_type(
            current_user.id,
            name,
            optimal_temp,
            needed_water,
            needed_light,
            days_cycle,
            initial_biomass,
            potential,
        )
        console.print(
            Panel(
                f"Tipo '{nuevo.name}' creado con ID {nuevo.id}",
                style=f"bold {VERDE}",
            )
        )
    except (InvalidInputError, DuplicateDataError, ResourceOwnershipError) as e:
        console.print(Panel(f"{str(e)}", style=f"bold {MARRON}"))
    except ValueError:
        console.print(Panel("Valores numéricos inválidos.", style=f"bold {MARRON}"))


def seleccionar_crop_type(mensaje="Selecciona un tipo:"):
    tipos = crop_type_service.get_crop_types()
    if not tipos:
        console.print(Panel("No hay tipos.", style=f"bold {MARRON}"))
        return None
    opciones = [f"{t.name} (ID: {t.id})" for t in tipos]
    elegido = questionary.select(mensaje, choices=opciones, style=custom_style).ask()
    idx = opciones.index(elegido)
    return tipos[idx]


def editar_crop_type():
    tipo = seleccionar_crop_type("Selecciona el tipo a editar:")
    if not tipo:
        return
    # Permitir cambiar algunos campos
    cambios = {}
    name = questionary.text(
        f"Nuevo nombre (dejar vacío para '{tipo.name}'):", style=custom_style
    ).ask()
    if name and name.strip():
        cambios["name"] = name.strip()

    temp = questionary.text(
        f"Nueva temperatura óptima (dejar vacío para {tipo.optimal_temp}):",
        style=custom_style,
    ).ask()
    if temp:
        cambios["optimal_temp"] = float(temp)

    water = questionary.text(
        f"Nueva agua necesaria (dejar vacío para {tipo.needed_water}):",
        style=custom_style,
    ).ask()
    if water:
        cambios["needed_water"] = float(water)

    light = questionary.text(
        f"Nueva luz necesaria (dejar vacío para {tipo.needed_light}):",
        style=custom_style,
    ).ask()
    if light:
        cambios["needed_light"] = float(light)

    cycle = questionary.text(
        f"Nuevo ciclo en días (dejar vacío para {tipo.days_cycle}):", style=custom_style
    ).ask()
    if cycle:
        cambios["days_cycle"] = int(cycle)

    init = questionary.text(
        f"Nueva biomasa inicial (dejar vacío para {tipo.initial_biomass}):",
        style=custom_style,
    ).ask()
    if init:
        cambios["initial_biomass"] = float(init)

    pot = questionary.text(
        f"Nuevo potencial (dejar vacío para {tipo.potential_performance}):",
        style=custom_style,
    ).ask()
    if pot:
        cambios["potential_performance"] = float(pot)

    if cambios:
        try:
            crop_type_service.update_crop_type(current_user.id, tipo.id, **cambios)
            console.print(Panel("Tipo actualizado.", style=f"bold {VERDE}"))
        except (
            BusinessRuleViolationError,
            ResourceOwnershipError,
            InvalidInputError,
        ) as e:
            console.print(Panel(f"{str(e)}", style=f"bold {MARRON}"))
    else:
        console.print(Panel("No se realizaron cambios.", style=f"bold {MARRON}"))


def eliminar_crop_type():
    tipo = seleccionar_crop_type(
        "Selecciona el tipo a eliminar (solo si no tiene cultivos activos):"
    )
    if not tipo:
        return
    confirm = questionary.confirm(f"¿Eliminar el tipo '{tipo.name}'?").ask()
    if confirm:
        try:
            crop_type_service.delete_crop_type(current_user.id, tipo.id)
            console.print(Panel("Tipo eliminado.", style=f"bold {VERDE}"))
        except (BusinessRuleViolationError, ResourceOwnershipError) as e:
            console.print(Panel(f"{str(e)}", style=f"bold {MARRON}"))


def ver_estadisticas_tipos():
    try:
        stats = crop_type_service.get_crop_types_with_stats(current_user.id)
        table = Table(
            title="Estadísticas por Tipo de Cultivo",
            title_style=f"bold {VERDE}",
            border_style=VERDE,
        )
        table.add_column("Tipo", style="white")
        table.add_column("Cultivos activos", style="white")
        for s in stats:
            table.add_row(s["name"], str(s["active_crops"]))
        console.print(table)
    except ResourceOwnershipError:
        console.print(Panel("No tienes permisos.", style=f"bold {MARRON}"))


def ver_cultivos_usuario():
    # Primero listar usuarios
    users = user_service.get_all_users(current_user.id)
    if not users:
        console.print(Panel("No hay usuarios.", style=f"bold {MARRON}"))
        return
    opciones = [f"{u.username} (ID: {u.id})" for u in users]
    elegido = questionary.select(
        "Selecciona un usuario:", choices=opciones, style=custom_style
    ).ask()
    idx = opciones.index(elegido)
    target_user = users[idx]

    crops = crop_service.get_crops_by_user(target_user.id, current_user.id)
    if not crops:
        console.print(
            Panel(
                f"El usuario {target_user.username} no tiene cultivos.",
                style=f"bold {MARRON}",
            )
        )
        return
    table = Table(
        title=f"Cultivos de {target_user.username}",
        title_style=f"bold {VERDE}",
        border_style=VERDE,
    )
    table.add_column("ID", style="cyan")
    table.add_column("Nombre", style="white")
    table.add_column("Tipo", style="white")
    table.add_column("Días", style="white")
    table.add_column("Activo", style="white")
    for c in crops:
        tipo = crop_type_service.get_crop_type_by_id(c.crop_type_id)
        tipo_nombre = tipo.name if tipo else "?"
        table.add_row(
            c.id,
            c.name,
            tipo_nombre,
            str(len(c.conditions)),
            "✓" if c.active else "x",
        )
    console.print(table)


def ver_estadisticas_globales():
    # Por ejemplo: total de usuarios, cultivos activos, etc.
    users = user_service.get_all_users(current_user.id)
    # Podemos obtener del storage directamente
    all_crops = storage.get_crops()
    active_crops = [c for c in all_crops if c.active]
    total_crop_types = len(crop_type_service.get_crop_types())

    panel = Panel(
        f"""
    [bold]Total usuarios:[/bold] {len(users)}
    [bold]Total cultivos:[/bold] {len(all_crops)}
    [bold]Cultivos activos:[/bold] {len(active_crops)}
    [bold]Tipos de cultivo:[/bold] {total_crop_types}
        """,
        title="Estadísticas Globales",
        border_style=VERDE,
    )
    console.print(panel)


def eliminar_usuario_admin():
    """Admin puede eliminar cualquier usuario (seleccionando de una lista)."""
    try:
        users = user_service.get_all_users(current_user.id)
        if not users:
            console.print(Panel("No hay usuarios registrados.", style=f"bold {MARRON}"))
            return

        # Filtrar para que no pueda eliminarse a sí mismo
        otros_usuarios = [u for u in users if u.id != current_user.id]

        if not otros_usuarios:
            console.print(
                Panel("No hay otros usuarios para eliminar.", style=f"bold {MARRON}")
            )
            return

        opciones = [
            f"{u.username} (ID: {u.id}) - {len(u.crop_ids)} cultivos"
            for u in otros_usuarios
        ]
        opciones.append("Cancelar")

        elegido = questionary.select(
            "Selecciona el usuario a eliminar:", choices=opciones, style=custom_style
        ).ask()

        if elegido == "Cancelar":
            return

        idx = opciones.index(elegido)
        usuario_a_eliminar = otros_usuarios[idx]

        # Confirmación
        console.print(
            Panel(
                f"[bold]ADVERTENCIA:[/bold] Se eliminará:\n"
                f"• Usuario: {usuario_a_eliminar.username}\n"
                f"• Cultivos asociados: {len(usuario_a_eliminar.crop_ids)}\n"
                f"• Esta acción NO se puede deshacer.",
                style=f"bold {MARRON}",
            )
        )

        confirm = questionary.confirm(
            f"¿Estás SEGURO de eliminar a '{usuario_a_eliminar.username}'?",
            default=False,
        ).ask()

        if not confirm:
            return

        # PRIMERO: Eliminar todos los cultivos del usuario
        crops = crop_service.get_crops_by_user(usuario_a_eliminar.id, current_user.id)
        for crop in crops:
            try:
                crop_service.delete_crop(crop.id, current_user.id)
                console.print(f"Cultivo '{crop.name}' eliminado.")
            except Exception as e:
                console.print(f"Error al eliminar cultivo {crop.name}: {str(e)}")

        # LUEGO: Eliminar el usuario
        user_service.delete_user(usuario_a_eliminar.id, current_user.id)

        # Verificar que se eliminó
        usuario_verificacion = user_service.storage.get_user_by_id(
            usuario_a_eliminar.id
        )
        if usuario_verificacion is None:
            console.print(
                Panel(
                    f"Usuario '{usuario_a_eliminar.username}' eliminado correctamente.",
                    style=f"bold {VERDE}",
                )
            )
        else:
            console.print(
                Panel(
                    "El usuario parece no haberse eliminado. Intenta manualmente.",
                    style=f"bold {MARRON}",
                )
            )

    except ResourceOwnershipError:
        console.print(
            Panel("No tienes permisos para esta acción.", style=f"bold {MARRON}")
        )
    except Exception as e:
        console.print(Panel(f"Error: {str(e)}", style=f"bold {MARRON}"))


if __name__ == "__main__":
    app()
