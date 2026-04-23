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
    """Menú principal para usuarios normales."""
    acciones = {
        "Mis cultivos": listar_mis_cultivos,
        "Crear nuevo cultivo": crear_cultivo,
        "Buscar cultivos": menu_buscar_cultivos,
        "Ver detalles de un cultivo": ver_detalle_cultivo,
        "Simular día en un cultivo": simular_dia,
        "Estadísticas de un cultivo": ver_estadisticas,
        "Editar nombre de un cultivo": editar_cultivo,
        "Eliminar un cultivo": eliminar_cultivo,
        "Gestionar mi perfil": menu_gestionar_perfil,
        "Cerrar sesión": logout,
    }

    while True:
        opcion = questionary.select(
            f"Menú de Usuario: {current_user.username}",
            choices=list(acciones.keys()),
            style=custom_style,
        ).ask()

        if opcion == "Cerrar sesión":
            logout()
            break

        acciones[opcion]()


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
    irrigation = (
        questionary.text(
            "Riego hecho a la planta (mm, opcional, Enter para 0):", style=custom_style
        ).ask()
        or "0"
    )

    try:
        temp_f = float(temp)
        rain_f = float(rain)
        sun_f = float(sun)
        irrigation_f = float(irrigation)
        updated_crop = crop_service.simulate_day(
            crop.id, current_user.id, temp_f, rain_f, sun_f, irrigation_f
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
    tipo_obj = _seleccionar_tipo_cultivo()
    if not tipo_obj:
        return

    resultados = _obtener_cultivos_por_tipo(tipo_obj.id)
    if not resultados:
        console.print(
            Panel(
                f"No tienes cultivos de tipo {tipo_obj.name}.", style=f"bold {MARRON}"
            )
        )
        return

    _mostrar_resultados_por_tipo(resultados, tipo_obj.name)


def _seleccionar_tipo_cultivo():
    """Muestra lista de tipos y retorna el seleccionado o None."""
    tipos = crop_type_service.get_crop_types()
    if not tipos:
        console.print(
            Panel("No hay tipos de cultivo disponibles.", style=f"bold {MARRON}")
        )
        return None

    opciones = [t.name for t in tipos]
    opciones.append("Volver")

    tipo_elegido = questionary.select(
        "Selecciona tipo de cultivo:", choices=opciones, style=custom_style
    ).ask()

    if tipo_elegido == "Volver":
        return None

    return next((t for t in tipos if t.name == tipo_elegido), None)


def _obtener_cultivos_por_tipo(tipo_id):
    """Obtiene los cultivos del usuario actual filtrados por tipo."""
    crops = crop_service.get_crops_by_user(current_user.id, current_user.id)
    return [c for c in crops if c.crop_type_id == tipo_id]


def _mostrar_resultados_por_tipo(resultados, tipo_nombre):
    """Muestra la tabla con los cultivos encontrados."""
    table = Table(
        title=f"Cultivos de tipo {tipo_nombre}",
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
    target_user = _seleccionar_usuario()
    if not target_user:
        return

    filtro = _seleccionar_filtro(target_user.username)
    if not filtro:
        return

    crops = _obtener_cultivos_con_filtro(target_user.id, filtro)
    if not crops:
        console.print(Panel("No se encontraron cultivos.", style=f"bold {MARRON}"))
        return

    _mostrar_tabla_cultivos(crops, target_user.username)


def _seleccionar_usuario():
    """Selecciona un usuario de la lista."""
    users = user_service.get_all_users(current_user.id)
    if not users:
        console.print(Panel("No hay usuarios.", style=f"bold {MARRON}"))
        return None

    opciones = [f"{u.username} (ID: {u.id})" for u in users]
    opciones.append("Volver")

    elegido = questionary.select(
        "Selecciona un usuario:", choices=opciones, style=custom_style
    ).ask()

    if elegido == "Volver":
        return None

    idx = opciones.index(elegido)
    return users[idx]


def _seleccionar_filtro(username):
    """Selecciona el tipo de filtro a aplicar."""
    filtro = questionary.select(
        f"Filtrar cultivos de {username}:",
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

    return None if filtro == "Volver" else filtro


def _obtener_cultivos_con_filtro(user_id, filtro):
    """Obtiene los cultivos aplicando el filtro seleccionado."""
    crops = crop_service.get_crops_by_user(user_id, current_user.id)

    if filtro == "Todos":
        return crops

    filtros_map = {
        "Por ID": _filtrar_por_id,
        "Por nombre": _filtrar_por_nombre,
        "Por tipo": _filtrar_por_tipo,
        "Solo activos": lambda c: [cult for cult in c if cult.active],
        "Solo cosechados": lambda c: [cult for cult in c if not cult.active],
    }

    if filtro in filtros_map:
        return filtros_map[filtro](crops)

    return crops


def _filtrar_por_id(crops):
    """Filtra cultivos por ID."""
    crop_id = questionary.text("ID del cultivo:", style=custom_style).ask()
    return [c for c in crops if c.id == crop_id] if crop_id else crops


def _filtrar_por_nombre(crops):
    """Filtra cultivos por nombre (búsqueda parcial)."""
    nombre = questionary.text("Nombre (o parte):", style=custom_style).ask()
    if not nombre:
        return crops
    nombre_lower = nombre.lower()
    return [c for c in crops if nombre_lower in c.name.lower()]


def _filtrar_por_tipo(crops):
    """Filtra cultivos por tipo."""
    tipos = crop_type_service.get_crop_types()
    if not tipos:
        return crops

    opciones_tipo = [t.name for t in tipos]
    tipo_elegido = questionary.select(
        "Tipo:", choices=opciones_tipo, style=custom_style
    ).ask()
    tipo_obj = next(t for t in tipos if t.name == tipo_elegido)
    return [c for c in crops if c.crop_type_id == tipo_obj.id]


def _mostrar_tabla_cultivos(crops, username):
    """Muestra los cultivos en una tabla formateada."""
    table = Table(
        title=f"Cultivos de {username}",
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
    table.add_column("Temp óptima (°C)", style="white")
    table.add_column("Temp max (°C)", style="white")
    table.add_column("Agua nec (mm/día)", style="white")
    table.add_column("Luz nec (horas)", style="white")
    table.add_column("Ciclo (días)", style="white")
    table.add_column("Biomasa ini (g/m²)", style="white")
    table.add_column("Potencial (g/m²)", style="white")
    table.add_column("Activos", style="white")

    for t in tipos:
        # Contar cultivos activos de este tipo
        cultivos = crop_service.storage.get_crops_by_type(t.id)
        activos = sum(1 for c in cultivos if c.active)

        table.add_row(
            t.id,
            t.name,
            str(t.optimal_temp),
            str(t.maximum_temp),
            str(t.needed_water),
            str(t.needed_light),
            str(t.days_cycle),
            str(t.initial_biomass),
            str(t.potential_performance),
            str(activos),
        )
    console.print(table)


def crear_crop_type():
    """Admin crea un nuevo tipo de cultivo con todos los parámetros."""

    # Datos básicos
    name = questionary.text(
        "Nombre del tipo de cultivo (ej. Maíz, Tomate, Banano):", style=custom_style
    ).ask()

    try:
        optimal_temp = float(
            questionary.text(
                "Temperatura óptima para el crecimiento (°C)", style=custom_style
            ).ask()
        )

        minimum_temp = float(
            questionary.text(
                "Temperatura base mínima para crecimiento (°C):\n"
                "  Por debajo de este valor, la fotosíntesis se detiene. Ej: Maíz 8°C, Tomate 10°C",
                style=custom_style,
            ).ask()
        )

        maximum_temp = float(
            questionary.text(
                "Temperatura máxima letal para crecimiento (°C):\n"
                "  Por encima de este valor, la fotosíntesis se detiene. Ej: Maíz 40°C, Tomate 35°C",
                style=custom_style,
            ).ask()
        )

        cold_sensibility = float(
            questionary.text(
                "Sensibilidad al frío (0-1, mayor = más sensible):\n"
                "  Controla cuánto aumenta la respiración cuando la temperatura baja del óptimo.\n"
                "  Ej: Planta tropical (Banano) → 0.7-0.9, Planta templada (Manzana) → 0.3-0.5",
                style=custom_style,
            ).ask()
            or "0.5"
        )

        heat_sensibility = float(
            questionary.text(
                "Sensibilidad al calor (0-1, mayor = más sensible):\n"
                "  Controla cuánto aumenta la respiración cuando la temperatura sube del óptimo.\n"
                "  Ej: Planta de clima fresco (Lechuga) → 0.8-1.0, Planta tropical (Banano) → 0.3-0.5",
                style=custom_style,
            ).ask()
            or "0.5"
        )

        cold_factor = float(
            questionary.text(
                "Factor exponencial de respuesta al frío (mayor = respuesta más abrupta):\n"
                "  Controla qué tan rápido aumenta el estrés cuando la temperatura baja.\n"
                "  Rango típico: 0.05-0.2. Default 0.1",
                style=custom_style,
            ).ask()
            or "0.1"
        )

        heat_factor = float(
            questionary.text(
                "Factor exponencial de respuesta al calor (mayor = respuesta más abrupta):\n"
                "  Controla qué tan rápido aumenta el estrés cuando la temperatura sube.\n"
                "  Rango típico: 0.05-0.2. Default 0.1",
                style=custom_style,
            ).ask()
            or "0.1"
        )

        temperature_curve_length = float(
            questionary.text(
                "Anchura de la curva de temperatura (σ):\n"
                "  Define qué tan amplio es el rango de temperaturas donde la planta crece bien.\n"
                "  Valores altos (8-10) = planta tolerante a variaciones térmicas.\n"
                "  Valores bajos (2-4) = planta muy sensible. Default 5.0",
                style=custom_style,
            ).ask()
            or "5.0"
        )

        water_wilting = float(
            questionary.text(
                "Punto de marchitez permanente (mm):\n"
                "  Cantidad de agua en el suelo por debajo de la cual la planta ya no puede extraer agua y se marchita.\n"
                "  Rango típico: 40-80 mm según tipo de suelo",
                style=custom_style,
            ).ask()
            or "60"
        )

        water_opt_low = float(
            questionary.text(
                "Umbral inferior de agua óptima (mm):\n"
                "  Por debajo de este valor, la planta comienza a sufrir estrés hídrico.\n"
                "  Debe ser mayor que el punto de marchitez. Rango típico: 70-100 mm",
                style=custom_style,
            ).ask()
            or "80"
        )

        needed_water = float(
            questionary.text(
                "Agua necesaria para crecimiento óptimo (mm/día):\n"
                "  Cantidad de agua que la planta transpira en condiciones ideales.\n"
                "  Ej: Maíz 5-6 mm/día, Tomate 4-5 mm/día, Banano 5-7 mm/día",
                style=custom_style,
            ).ask()
        )

        water_opt_high = float(
            questionary.text(
                "Umbral superior de agua óptima (mm):\n"
                "  Por encima de este valor, el exceso de agua comienza a dañar la planta (anoxia radicular).\n"
                "  Debe ser mayor que el agua necesaria. Rango típico: 120-160 mm",
                style=custom_style,
            ).ask()
            or "130"
        )

        water_capacity = float(
            questionary.text(
                "Capacidad de campo del suelo (mm):\n"
                "  Cantidad máxima de agua que el suelo puede retener antes de que se produzca escorrentía o drenaje.\n"
                "  Rango típico: 150-250 mm según tipo de suelo",
                style=custom_style,
            ).ask()
            or "200"
        )

        water_sensibility = float(
            questionary.text(
                "Sensibilidad al estrés hídrico (mayor = más sensible):\n"
                "  Controla cuánto aumenta la respiración cuando hay falta o exceso de agua.\n"
                "  Rango típico: 0.2-1.5. Default 0.3",
                style=custom_style,
            ).ask()
            or "0.3"
        )

        water_stress_constant = float(
            questionary.text(
                "Pendiente de la curva de estrés hídrico (k):\n"
                "  Controla qué tan abrupta es la caída de la eficiencia cuando el agua se aleja del rango óptimo.\n"
                "  Valores altos (0.8-1.0) = respuesta muy abrupta. Default 0.4",
                style=custom_style,
            ).ask()
            or "0.4"
        )

        needed_light = float(
            questionary.text(
                "Horas de luz óptimas por día:\n"
                "  Cantidad de luz solar que maximiza la fotosíntesis.\n"
                "  Ej: Plantas de día corto (fresa) 8-10h, día largo (cebada) 14-16h",
                style=custom_style,
            ).ask()
        )

        needed_light_max = float(
            questionary.text(
                "Horas de luz máximas antes de fotoinhibición:\n"
                "  A partir de este valor, el exceso de luz comienza a dañar los cloroplastos.\n"
                "  Debe ser mayor que las horas óptimas. Default: óptimo + 4 horas",
                style=custom_style,
            ).ask()
            or str(needed_light + 4)
        )

        light_sensibility = float(
            questionary.text(
                "Sensibilidad al exceso de luz (mayor = más sensible):\n"
                "  Controla cuánto aumenta la respiración cuando hay exceso de luz.\n"
                "  Rango típico: 0.5-2.0. Default 1.0",
                style=custom_style,
            ).ask()
            or "1.0"
        )

        light_km = float(
            questionary.text(
                "Constante de Michaelis-Menten para luz (K_m):\n"
                "  Horas de luz necesarias para alcanzar el 50% de la tasa máxima de fotosíntesis.\n"
                "  Rango típico: 2-6 horas. Default: óptimo * 0.5",
                style=custom_style,
            ).ask()
            or str(needed_light * 0.5)
        )

        light_sigma = float(
            questionary.text(
                "Anchura de la curva de fotoinhibición:\n"
                "  Controla qué tan rápido cae la eficiencia cuando la luz supera el óptimo.\n"
                "  Valores bajos (1-2) = caída rápida. Default 2.0",
                style=custom_style,
            ).ask()
            or "2.0"
        )

        phenological_initial_coefficient = float(
            questionary.text(
                "Coeficiente de cultivo - Fase inicial (K_c_ini):\n"
                "  Demanda de agua en la etapa de establecimiento (primer 15-20% del ciclo).\n"
                "  Rango típico: 0.3-0.5 (plantas pequeñas, poca transpiración)",
                style=custom_style,
            ).ask()
            or "0.4"
        )

        phenological_mid_coefficient = float(
            questionary.text(
                "Coeficiente de cultivo - Fase media (K_c_mid):\n"
                "  Demanda de agua en la etapa de máximo crecimiento (40-85% del ciclo).\n"
                "  Rango típico: 1.0-1.2 (planta completamente desarrollada)",
                style=custom_style,
            ).ask()
            or "1.1"
        )

        phenological_end_coefficient = float(
            questionary.text(
                "Coeficiente de cultivo - Fase final (K_c_end):\n"
                "  Demanda de agua en la etapa de maduración (último 15% del ciclo).\n"
                "  Rango típico: 0.5-0.8 (planta senescente)",
                style=custom_style,
            ).ask()
            or "0.6"
        )

        days_cycle = int(
            questionary.text(
                "Duración total del ciclo de cultivo (días):\n"
                "  Desde la siembra hasta la cosecha.\n"
                "  Ej: Lechuga 30-60, Tomate 90-120, Maíz 120-150, Banano 300-400",
                style=custom_style,
            ).ask()
        )

        photosyntesis_max_rate = float(
            questionary.text(
                "Tasa máxima de fotosíntesis (r_max, por día):\n"
                "  Capacidad máxima de la planta para producir biomasa en condiciones ideales.\n"
                "  Rango típico: 0.15-0.35. Default 0.22",
                style=custom_style,
            ).ask()
            or "0.22"
        )

        breathing_base_rate = float(
            questionary.text(
                "Tasa base de respiración de mantenimiento (r_m, por día):\n"
                "  Energía que la planta consume diariamente para mantenerse viva.\n"
                "  Normalmente es 10-30% de la tasa máxima de fotosíntesis. Default 0.05",
                style=custom_style,
            ).ask()
            or "0.05"
        )

        theta = float(
            questionary.text(
                "Parámetro de asimetría logística (θ):\n"
                "  Controla la forma de la curva de crecimiento.\n"
                "  θ = 1 → crecimiento logístico simétrico.\n"
                "  θ > 1 → crecimiento más rápido al inicio y más lento al final.\n"
                "  Rango típico: 1.0-3.0. Default 1.5",
                style=custom_style,
            ).ask()
            or "1.5"
        )

        consecutive_stress_days_limit = int(
            questionary.text(
                "Días consecutivos de estrés severo antes de la muerte:\n"
                "  Si la planta sufre estrés extremo (factor total < 0.1) durante este número de días seguidos, muere.\n"
                "  Rango típico: 3-7 días. Default 5",
                style=custom_style,
            ).ask()
            or "5"
        )

        theta_coefficient = float(
            questionary.text(
                "Coeficiente de evapotranspiración de referencia:\n"
                "  Parámetro del método de Hargreaves para calcular la evaporación potencial.\n"
                "  Valor estándar: 0.0023 (no cambiar a menos que se tenga conocimiento específico)",
                style=custom_style,
            ).ask()
            or "0.0023"
        )

        initial_biomass = float(
            questionary.text(
                "Biomasa inicial al momento de la siembra (g/m²):\n"
                "  Masa de la plántula al inicio. Ej: Semilla pequeña 0.1-0.5, plántula 1-5",
                style=custom_style,
            ).ask()
        )

        potential_performance = float(
            questionary.text(
                "Rendimiento potencial máximo (g/m²):\n"
                "  Biomasa máxima que puede alcanzar el cultivo en condiciones perfectas.\n"
                "  Ej: Lechuga 200-300, Tomate 500-800, Maíz 1000-1500, Banano 2000-3000",
                style=custom_style,
            ).ask()
        )

        nuevo = crop_type_service.create_crop_type(
            admin_id=current_user.id,
            name=name,
            optimal_temp=optimal_temp,
            minimum_temp=minimum_temp,
            maximum_temp=maximum_temp,
            cold_sensibility=cold_sensibility,
            heat_sensibility=heat_sensibility,
            cold_factor=cold_factor,
            heat_factor=heat_factor,
            temperature_curve_length=temperature_curve_length,
            water_wilting=water_wilting,
            water_opt_low=water_opt_low,
            needed_water=needed_water,
            water_opt_high=water_opt_high,
            water_capacity=water_capacity,
            water_sensibility=water_sensibility,
            water_stress_constant=water_stress_constant,
            needed_light=needed_light,
            needed_light_max=needed_light_max,
            light_sensibility=light_sensibility,
            light_km=light_km,
            light_sigma=light_sigma,
            phenological_initial_coefficient=phenological_initial_coefficient,
            phenological_mid_coefficient=phenological_mid_coefficient,
            phenological_end_coefficient=phenological_end_coefficient,
            days_cycle=days_cycle,
            photosyntesis_max_rate=photosyntesis_max_rate,
            breathing_base_rate=breathing_base_rate,
            theta=theta,
            consecutive_stress_days_limit=consecutive_stress_days_limit,
            theta_coefficient=theta_coefficient,
            initial_biomass=initial_biomass,
            potential_performance=potential_performance,
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
    """Edita un tipo de cultivo existente (solo admin)."""
    tipo = seleccionar_crop_type("Selecciona el tipo a editar:")
    if not tipo:
        return

    cambios = _recolectar_cambios_crop_type(tipo)

    if not cambios:
        console.print(Panel("No se realizaron cambios.", style=f"bold {MARRON}"))
        return

    _aplicar_cambios_crop_type(tipo.id, cambios)


def _recolectar_cambios_crop_type(tipo):
    """Solicita al usuario los nuevos valores y retorna un diccionario con los cambios."""
    cambios = {}

    _preguntar_campo(cambios, "name", "Nombre del cultivo", tipo.name, str)

    _preguntar_campo(
        cambios,
        "optimal_temp",
        "Temperatura óptima para crecimiento (°C)",
        tipo.optimal_temp,
        float,
    )
    _preguntar_campo(
        cambios,
        "minimum_temp",
        "Temperatura mínima para crecimiento (°C)",
        tipo.minimum_temp,
        float,
    )
    _preguntar_campo(
        cambios,
        "maximum_temp",
        "Temperatura máxima letal (°C)",
        tipo.maximum_temp,
        float,
    )

    _preguntar_campo(
        cambios,
        "cold_sensibility",
        "Sensibilidad al frío (0-1)",
        tipo.cold_sensibility,
        float,
    )
    _preguntar_campo(
        cambios,
        "heat_sensibility",
        "Sensibilidad al calor (0-1)",
        tipo.heat_sensibility,
        float,
    )
    _preguntar_campo(
        cambios,
        "cold_factor",
        "Factor exponencial de respuesta al frío",
        tipo.cold_factor,
        float,
    )
    _preguntar_campo(
        cambios,
        "heat_factor",
        "Factor exponencial de respuesta al calor",
        tipo.heat_factor,
        float,
    )
    _preguntar_campo(
        cambios,
        "temperature_curve_length",
        "Anchura de la curva de temperatura (σ)",
        tipo.temperature_curve_length,
        float,
    )

    _preguntar_campo(
        cambios,
        "water_wilting",
        "Punto de marchitez permanente (mm)",
        tipo.water_wilting,
        float,
    )
    _preguntar_campo(
        cambios,
        "water_opt_low",
        "Umbral inferior de agua óptima (mm)",
        tipo.water_opt_low,
        float,
    )
    _preguntar_campo(
        cambios,
        "needed_water",
        "Agua necesaria para crecimiento óptimo (mm/día)",
        tipo.needed_water,
        float,
    )
    _preguntar_campo(
        cambios,
        "water_opt_high",
        "Umbral superior de agua óptima (mm)",
        tipo.water_opt_high,
        float,
    )
    _preguntar_campo(
        cambios,
        "water_capacity",
        "Capacidad de campo del suelo (mm)",
        tipo.water_capacity,
        float,
    )
    _preguntar_campo(
        cambios,
        "water_sensibility",
        "Sensibilidad al estrés hídrico",
        tipo.water_sensibility,
        float,
    )
    _preguntar_campo(
        cambios,
        "water_stress_constant",
        "Pendiente de curva de estrés hídrico (k)",
        tipo.water_stress_constant,
        float,
    )

    _preguntar_campo(
        cambios,
        "needed_light",
        "Horas de luz óptimas por día",
        tipo.needed_light,
        float,
    )
    _preguntar_campo(
        cambios,
        "needed_light_max",
        "Horas de luz máximas antes de fotoinhibición",
        tipo.needed_light_max,
        float,
    )
    _preguntar_campo(
        cambios,
        "light_sensibility",
        "Sensibilidad al exceso de luz",
        tipo.light_sensibility,
        float,
    )
    _preguntar_campo(
        cambios,
        "light_km",
        "Constante de Michaelis-Menten (K_m) para luz",
        tipo.light_km,
        float,
    )
    _preguntar_campo(
        cambios,
        "light_sigma",
        "Anchura de curva de fotoinhibición (σ)",
        tipo.light_sigma,
        float,
    )

    _preguntar_campo(
        cambios,
        "phenological_initial_coefficient",
        "Coeficiente de cultivo - Fase inicial (K_c_ini)",
        tipo.phenological_initial_coefficient,
        float,
    )
    _preguntar_campo(
        cambios,
        "phenological_mid_coefficient",
        "Coeficiente de cultivo - Fase media (K_c_mid)",
        tipo.phenological_mid_coefficient,
        float,
    )
    _preguntar_campo(
        cambios,
        "phenological_end_coefficient",
        "Coeficiente de cultivo - Fase final (K_c_end)",
        tipo.phenological_end_coefficient,
        float,
    )

    _preguntar_campo(
        cambios,
        "days_cycle",
        "Duración total del ciclo de cultivo (días)",
        tipo.days_cycle,
        int,
    )
    _preguntar_campo(
        cambios,
        "photosyntesis_max_rate",
        "Tasa máxima de fotosíntesis (r_max, por día)",
        tipo.photosyntesis_max_rate,
        float,
    )
    _preguntar_campo(
        cambios,
        "breathing_base_rate",
        "Tasa base de respiración (r_m, por día)",
        tipo.breathing_base_rate,
        float,
    )
    _preguntar_campo(
        cambios, "theta", "Parámetro de asimetría logística (θ)", tipo.theta, float
    )
    _preguntar_campo(
        cambios,
        "consecutive_stress_days_limit",
        "Días consecutivos de estrés severo antes de la muerte",
        tipo.consecutive_stress_days_limit,
        int,
    )
    _preguntar_campo(
        cambios,
        "theta_coefficient",
        "Coeficiente de evapotranspiración (Hargreaves)",
        tipo.theta_coefficient,
        float,
    )

    _preguntar_campo(
        cambios,
        "initial_biomass",
        "Biomasa inicial al sembrar (g/m²)",
        tipo.initial_biomass,
        float,
    )
    _preguntar_campo(
        cambios,
        "potential_performance",
        "Rendimiento potencial máximo (g/m²)",
        tipo.potential_performance,
        float,
    )

    return cambios


def _preguntar_campo(cambios, campo, nombre_mostrar, valor_actual, tipo_conversion):
    """Pregunta un campo y lo agrega a cambios si el usuario ingresó un valor."""
    valor_str = questionary.text(
        f"Nuevo {nombre_mostrar} (dejar vacío para '{valor_actual}'):",
        style=custom_style,
    ).ask()

    if valor_str and valor_str.strip():
        try:
            cambios[campo] = tipo_conversion(valor_str)
        except ValueError:
            console.print(
                Panel(
                    f"Valor inválido para {nombre_mostrar}. Se ignora.",
                    style=f"bold {MARRON}",
                )
            )


def _aplicar_cambios_crop_type(tipo_id, cambios):
    """Aplica los cambios al tipo de cultivo."""
    try:
        crop_type_service.update_crop_type(current_user.id, tipo_id, **cambios)
        console.print(Panel("Tipo actualizado.", style=f"bold {VERDE}"))
    except (
        BusinessRuleViolationError,
        ResourceOwnershipError,
        InvalidInputError,
    ) as e:
        console.print(Panel(f"{str(e)}", style=f"bold {MARRON}"))


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
        usuario_a_eliminar = _seleccionar_usuario_para_eliminar()
        if not usuario_a_eliminar:
            return

        if not _confirmar_eliminacion(usuario_a_eliminar):
            return

        _eliminar_cultivos_del_usuario(usuario_a_eliminar)
        _eliminar_usuario(usuario_a_eliminar)
        _verificar_eliminacion(usuario_a_eliminar)

    except ResourceOwnershipError:
        console.print(
            Panel("No tienes permisos para esta acción.", style=f"bold {MARRON}")
        )
    except Exception as e:
        console.print(Panel(f"Error: {str(e)}", style=f"bold {MARRON}"))


def _obtener_usuarios_no_admin():
    """Retorna lista de usuarios excluyendo al admin actual."""
    users = user_service.get_all_users(current_user.id)
    if not users:
        console.print(Panel("No hay usuarios registrados.", style=f"bold {MARRON}"))
        return []

    otros_usuarios = [u for u in users if u.id != current_user.id]
    if not otros_usuarios:
        console.print(
            Panel("No hay otros usuarios para eliminar.", style=f"bold {MARRON}")
        )
        return []

    return otros_usuarios


def _seleccionar_usuario_para_eliminar():
    """Muestra lista de usuarios y retorna el seleccionado o None."""
    otros_usuarios = _obtener_usuarios_no_admin()
    if not otros_usuarios:
        return None

    opciones = [
        f"{u.username} (ID: {u.id}) - {len(u.crop_ids)} cultivos"
        for u in otros_usuarios
    ]
    opciones.append("Cancelar")

    elegido = questionary.select(
        "Selecciona el usuario a eliminar:", choices=opciones, style=custom_style
    ).ask()

    if elegido == "Cancelar":
        return None

    idx = opciones.index(elegido)
    return otros_usuarios[idx]


def _confirmar_eliminacion(usuario):
    """Muestra advertencia y pide confirmación."""
    console.print(
        Panel(
            f"[bold]ADVERTENCIA:[/bold] Se eliminará:\n"
            f"• Usuario: {usuario.username}\n"
            f"• Cultivos asociados: {len(usuario.crop_ids)}\n"
            f"• Esta acción NO se puede deshacer.",
            style=f"bold {MARRON}",
        )
    )

    return questionary.confirm(
        f"¿Estás SEGURO de eliminar a '{usuario.username}'?",
        default=False,
    ).ask()


def _eliminar_cultivos_del_usuario(usuario):
    """Elimina todos los cultivos asociados al usuario."""
    crops = crop_service.get_crops_by_user(usuario.id, current_user.id)
    for crop in crops:
        try:
            crop_service.delete_crop(crop.id, current_user.id)
            console.print(f"Cultivo '{crop.name}' eliminado.")
        except Exception as e:
            console.print(f"Error al eliminar cultivo {crop.name}: {str(e)}")


def _eliminar_usuario(usuario):
    """Elimina el usuario del sistema."""
    user_service.delete_user(usuario.id, current_user.id)


def _verificar_eliminacion(usuario):
    """Verifica que el usuario fue eliminado correctamente."""
    usuario_verificacion = user_service.storage.get_user_by_id(usuario.id)
    if usuario_verificacion is None:
        console.print(
            Panel(
                f"Usuario '{usuario.username}' eliminado correctamente.",
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


if __name__ == "__main__":
    app()
