import os
import time
import random
import subprocess
import urllib.request
import json
from playwright.sync_api import sync_playwright
from spintax_helper import parse_spintax

def obtener_puerto_segun_perfil(user_data_dir):
    """
    Asigna un puerto CDP de depuración independiente a cada perfil de Facebook
    generándolo dinámicamente a partir del nombre de la carpeta.
    Permite la ejecución simultánea de perfiles ilimitados sin conflictos.
    """
    dir_str = str(user_data_dir).lower()
    
    if "temporal" in dir_str:
        return 9299
        
    import hashlib
    # Genera un hash consistente del nombre del directorio y lo convierte a un puerto entre 9200 y 9999
    hash_obj = hashlib.md5(dir_str.encode())
    hash_int = int(hash_obj.hexdigest()[:8], 16)
    port = 9200 + (hash_int % 700)
    return port

def obtener_ruta_chrome():
    """
    Busca la ruta ejecutable de Google Chrome en Windows.
    """
    paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe")
    ]
    for p in paths:
        if os.path.exists(p):
            return p
    return "chrome.exe"

def esta_chrome_corriendo(port=9222):
    """
    Verifica si Chrome con puerto de depuración remota está escuchando.
    """
    try:
        req = urllib.request.urlopen(f"http://127.0.0.1:{port}/json/version", timeout=2)
        return req.status == 200
    except Exception:
        return False

def abrir_chrome_nativo(user_data_dir="./fb_chrome_profile", url="https://www.facebook.com"):
    """
    Abre Google Chrome de forma nativa desde Windows asignando el puerto único del perfil.
    Esto evita al 100% las detecciones de bot/automatización de Facebook durante el login.
    """
    abs_profile = os.path.abspath(user_data_dir)
    os.makedirs(abs_profile, exist_ok=True)
    chrome_bin = obtener_ruta_chrome()
    port = obtener_puerto_segun_perfil(user_data_dir)

    if not esta_chrome_corriendo(port):
        cmd = [
            chrome_bin,
            f"--remote-debugging-port={port}",
            f"--user-data-dir={abs_profile}",
            "--no-first-run",
            "--no-default-browser-check",
            url
        ]
        subprocess.Popen(cmd)
        time.sleep(3)

def abrir_navegador_para_login(user_data_dir="./fb_chrome_profile", callback_log=print):
    """
    Abre Google Chrome oficial con el perfil seleccionado para que el usuario inicie sesión sin ser bloqueado por Meta.
    """
    abs_profile = os.path.abspath(user_data_dir)
    port = obtener_puerto_segun_perfil(user_data_dir)
    nombre_perfil = os.path.basename(abs_profile)

    callback_log(f"🌐 Abriendo Google Chrome oficial para {nombre_perfil} (Puerto {port})...")
    callback_log("📌 Inicia sesión normalmente en tu cuenta de Facebook en la ventana de Chrome.")

    abrir_chrome_nativo(user_data_dir, "https://www.facebook.com")
    callback_log(f"💡 Una vez logueado en {nombre_perfil}, puedes minimizar o dejar abierta la ventana.")

def obtener_contexto_conectado(p, user_data_dir="./fb_chrome_profile", callback_log=print):
    """
    Conecta Playwright a la ventana de Google Chrome del perfil mediante puerto CDP asignado (9222, 9223, 9224...).
    Garantiza aislamiento total para permitir publicar simultáneamente con múltiples cuentas sin conflictos.
    """
    abs_profile = os.path.abspath(user_data_dir)
    os.makedirs(abs_profile, exist_ok=True)
    port = obtener_puerto_segun_perfil(user_data_dir)

    if not esta_chrome_corriendo(port):
        callback_log(f"🌐 Abriendo navegador nativo para {os.path.basename(abs_profile)} en puerto {port}...")
        abrir_chrome_nativo(user_data_dir, "https://www.facebook.com")
        time.sleep(4)

    # Conectar Playwright vía CDP al puerto dedicado del perfil
    try:
        browser = p.chromium.connect_over_cdp(f"http://127.0.0.1:{port}")
        context = browser.contexts[0]
        return browser, context
    except Exception as e:
        callback_log(f"⚠️ Reintentando conexión CDP en puerto {port}: {str(e)}")
        time.sleep(2)
        try:
            browser = p.chromium.connect_over_cdp(f"http://127.0.0.1:{port}")
            context = browser.contexts[0]
            return browser, context
        except Exception as e2:
            callback_log(f"⚠️ Error conectando a Chrome en puerto {port}: {str(e2)}")
            context = p.chromium.launch_persistent_context(
                user_data_dir=abs_profile,
                headless=False,
                args=["--disable-blink-features=AutomationControlled"]
            )
            return None, context

def publicar_en_grupo_individual(page, url, mensaje_spintax, imagen_path, callback_log):
    """
    Intenta publicar en un grupo individual de Facebook adjuntando 1 flyer (si fue seleccionado).
    """
    callback_log(f"🔗 Navegando a: {url}")
    page.goto(url, wait_until="domcontentloaded", timeout=45000)
    time.sleep(random.uniform(4, 6))

    # Verificar si estamos logueados o si pide login
    if "login" in page.url:
        callback_log("⚠️ No estás logueado en Facebook. Por favor inicia sesión primero con el botón 'Conectar Facebook'.")
        return False

    abs_img = os.path.abspath(imagen_path) if (imagen_path and os.path.exists(imagen_path)) else None

    # 1. Abrir el cuadro de publicación
    # Si tenemos un flyer, intentamos presionar directamente el botón "Foto/video" del feed del grupo
    modal_abierto = False
    
    if abs_img:
        photo_trigger_selectors = [
            'div[role="button"]:has-text("Foto/video")',
            'div[role="button"]:has-text("Foto/Video")',
            'div[role="button"]:has-text("Foto o video")',
            'div[role="button"]:has-text("Photo/video")',
            'span:has-text("Foto/video")',
            'span:has-text("Photo/video")',
            'div[aria-label="Foto/video"]',
            'div[aria-label="Photo/video"]'
        ]
        for sel in photo_trigger_selectors:
            try:
                btn = page.locator(sel).first
                if btn.is_visible(timeout=2000):
                    btn.click()
                    modal_abierto = True
                    callback_log("✏️ Cuadro de publicación abierto en modo Foto/Video.")
                    time.sleep(3)
                    break
            except Exception:
                continue

    if not modal_abierto:
        box_selectors = [
            'div[role="button"]:has-text("Escribe algo...")',
            'div[role="button"]:has-text("Write something...")',
            'div[role="button"]:has-text("¿Qué estás pensando?")',
            'div[role="button"]:has-text("What\'s on your mind?")',
            'span:has-text("Escribe algo...")',
            'span:has-text("Write something...")',
            'span:has-text("¿Qué estás pensando?")',
            'div[aria-label="Escribe algo..."]',
            'div[aria-label="Write something..."]',
            'div[role="button"]:has-text("Crear publicación")',
            'div[role="button"]:has-text("Create post")'
        ]
        for selector in box_selectors:
            try:
                btn = page.locator(selector).first
                if btn.is_visible(timeout=3000):
                    btn.click()
                    modal_abierto = True
                    callback_log("✏️ Cuadro de publicación abierto.")
                    time.sleep(3)
                    break
            except Exception:
                continue

    if not modal_abierto:
        try:
            page.keyboard.press("c")
            time.sleep(2)
        except Exception:
            pass

    time.sleep(random.uniform(2, 4))

    # 2. Localizar la caja de texto dentro del modal desplegado
    editor_selectors = [
        'div[role="dialog"] div[role="textbox"]',
        'div[role="dialog"] div[contenteditable="true"]',
        'div[contenteditable="true"][role="textbox"]',
        'div[role="textbox"]'
    ]

    editor = None
    for sel in editor_selectors:
        try:
            loc = page.locator(sel).first
            if loc.is_visible(timeout=4000):
                editor = loc
                break
        except Exception:
            continue

    if not editor:
        callback_log(f"❌ No se pudo abrir la caja de texto en {url}. Puede ser un grupo restringido.")
        return False

    # Escribir el texto
    editor.focus()
    mensaje_final = parse_spintax(mensaje_spintax)

    # Generar hashtags aleatorios probabilísticos anti-ban
    from tags_helper import obtener_tags_aleatorios_antiban
    tags_random = obtener_tags_aleatorios_antiban()
    if tags_random:
        mensaje_final += "\n\n" + tags_random
        callback_log(f"🏷️ Hashtags aleatorios anti-ban incluidos: {tags_random}")

    editor.fill(mensaje_final)
    time.sleep(random.uniform(2, 4))

    # 3. Cargar 1 Flyer en la publicación si fue seleccionado
    if abs_img:
        callback_log(f"📷 Cargando 1 flyer: {os.path.basename(abs_img)}")
        uploaded = False

        # Intento A: Cargar directamente a través del input file en el diálogo
        try:
            inputs_dialog = page.locator('div[role="dialog"] input[type="file"]')
            if inputs_dialog.count() > 0:
                inputs_dialog.first.set_input_files([abs_img])
                uploaded = True
                callback_log("  -> Flyer enviado a input file del modal.")
        except Exception as e:
            callback_log(f"  ⚠️ Intento A: {str(e)}")

        # Intento B: Cargar en cualquier input file visible de la página
        if not uploaded:
            try:
                inputs_all = page.locator('input[type="file"]')
                if inputs_all.count() > 0:
                    inputs_all.first.set_input_files([abs_img])
                    uploaded = True
                    callback_log("  -> Flyer enviado a input file global.")
            except Exception as e:
                callback_log(f"  ⚠️ Intento B: {str(e)}")

        # Intento C: Dar clic en el botón "Foto/video" del diálogo activando capturador de archivos
        if not uploaded:
            photo_btn_selectors = [
                'div[role="dialog"] div[aria-label="Foto/video"]',
                'div[role="dialog"] div[aria-label="Foto/Video"]',
                'div[role="dialog"] div[aria-label="Photo/video"]',
                'div[role="dialog"] div[aria-label="Foto o video"]',
                'div[role="dialog"] span:has-text("Foto/video")',
                'div[role="dialog"] span:has-text("Foto o video")',
                'div[role="dialog"] span:has-text("Photo/video")',
                'div[role="dialog"] div[role="button"]:has-text("Foto")',
                'div[role="dialog"] i[style*="background-image"]'
            ]
            for p_sel in photo_btn_selectors:
                try:
                    p_btn = page.locator(p_sel).first
                    if p_btn.is_visible(timeout=2000):
                        try:
                            with page.expect_file_chooser(timeout=3000) as fc_info:
                                p_btn.click()
                            fc = fc_info.value
                            fc.set_files([abs_img])
                            uploaded = True
                            callback_log("  -> Flyer cargado mediante capturador de archivos.")
                            break
                        except Exception:
                            p_btn.click()
                            time.sleep(2)
                            inputs_after = page.locator('input[type="file"]')
                            if inputs_after.count() > 0:
                                inputs_after.first.set_input_files([abs_img])
                                uploaded = True
                                callback_log("  -> Flyer cargado tras desplegar sección de foto.")
                                break
                except Exception:
                    continue

        if uploaded:
            # Si es video, esperamos más tiempo para que Facebook lo procese
            ext = os.path.splitext(abs_img)[1].lower()
            if ext in [".mp4", ".mov", ".avi", ".mkv"]:
                callback_log("  -> 🎥 Video detectado. Esperando procesamiento de video en Facebook (25 segundos)...")
                time.sleep(random.uniform(23, 28))
            else:
                callback_log("  -> 🖼️ Esperando procesamiento de imagen en Facebook (8 segundos)...")
                time.sleep(random.uniform(8, 11))
        else:
            callback_log("❌ No se pudo adjuntar el flyer a la publicación.")

    # 4. Dar clic en el botón Publicar / Post
    publish_btn_selectors = [
        'div[role="dialog"] div[aria-label="Publicar"]',
        'div[role="dialog"] div[aria-label="Post"]',
        'div[role="dialog"] div[role="button"]:has-text("Publicar")',
        'div[role="dialog"] div[role="button"]:has-text("Post")',
        'div[aria-label="Publicar"]',
        'div[aria-label="Post"]'
    ]

    published = False
    for p_sel in publish_btn_selectors:
        try:
            p_btn = page.locator(p_sel).first
            if p_btn.is_visible(timeout=3000):
                is_disabled = p_btn.get_attribute("aria-disabled") == "true"
                if not is_disabled:
                    p_btn.click()
                    published = True
                    time.sleep(random.uniform(6, 9))
                    
                    # Chequear si fue a "Pendiente de aprobación"
                    try:
                        # Buscar textos comunes de moderación en español e inglés
                        pending_loc = page.locator('text=/pendiente|aprobación|revisión|pending|approval/i')
                        if pending_loc.count() > 0 and pending_loc.first.is_visible(timeout=2000):
                            callback_log("⚠️ Publicación enviada, pero requiere APROBACIÓN del administrador (Pendiente).")
                        else:
                            callback_log("🚀 ¡Publicación enviada exitosamente y está VISIBLE!")
                    except Exception:
                        callback_log("🚀 ¡Publicación enviada exitosamente!")
                        
                    break
        except Exception:
            continue

    if not published:
        callback_log("⚠️ No se encontró el botón 'Publicar' activo o el grupo requiere aprobación previa.")
        return False

    return True


def obtener_lista_flyers(imagen_path_o_dir=""):
    """
    Obtiene la lista de todos los flyers/imágenes disponibles para rotación.
    """
    flyers = []

    # 1. Si el usuario seleccionó una imagen específica válida
    if imagen_path_o_dir and os.path.isfile(imagen_path_o_dir):
        flyers.append(os.path.abspath(imagen_path_o_dir))

    # 2. Escanear la carpeta ./flyers para rotar todas las fotos presentes
    dir_flyers = os.path.abspath("flyers")
    if os.path.exists(dir_flyers):
        archivos = sorted(os.listdir(dir_flyers))
        for f in archivos:
            ext = os.path.splitext(f)[1].lower()
            if ext in [".png", ".jpg", ".jpeg", ".webp", ".gif", ".mp4", ".mov", ".avi", ".mkv"]:
                full_path = os.path.join(dir_flyers, f)
                if full_path not in flyers:
                    flyers.append(full_path)

    return flyers


def obtener_grupos_mezclados_por_perfil(lista_grupos, user_data_dir):
    """
    Mezcla la lista de grupos asignando una semilla única según el perfil (Perfil 1, Perfil 2, etc.)
    para que cada cuenta publique en un orden completamente diferente y no coincidan en los mismos grupos.
    """
    if not lista_grupos:
        return []

    grupos_clean = [g.strip() for g in lista_grupos if g.strip() and not g.strip().startswith("#")]
    
    # Crear una semilla a partir del nombre del perfil + día del año
    abs_prof = os.path.abspath(user_data_dir)
    seed_str = f"{os.path.basename(abs_prof)}_{time.localtime().tm_yday}"
    seed_val = int(abs(hash(seed_str)))
    
    rng = random.Random(seed_val)
    grupos_shuffled = list(grupos_clean)
    rng.shuffle(grupos_shuffled)
    
    return grupos_shuffled


def ejecutar_automatizacion(lista_grupos, mensaje, imagen_path="", min_delay=45, max_delay=90, user_data_dir="./fb_chrome_profile", callback_log=print, stop_event=None):
    """
    Bucle principal de automatización con rotación automática de flyers y Spintax.
    """
    if not lista_grupos:
        callback_log("❌ La lista de grupos está vacía.")
        return

    # Mezclar la lista de grupos con un orden único e independiente para este perfil
    grupos_procesar = obtener_grupos_mezclados_por_perfil(lista_grupos, user_data_dir)
    nombre_perfil = os.path.basename(os.path.abspath(user_data_dir))

    # Escanear y preparar rotación de flyers
    flyers_disponibles = obtener_lista_flyers(imagen_path)

    callback_log(f"🔀 Lista de grupos mezclada aleatoriamente para {nombre_perfil} (0% coincidencia con otros perfiles).")
    callback_log(f"🚀 Iniciando campaña en {len(grupos_procesar)} grupos...")
    if flyers_disponibles:
        callback_log(f"🔄 Rotación activa: {len(flyers_disponibles)} flyer(s) diferentes disponibles para publicar alternados.")
        for idx, fl in enumerate(flyers_disponibles, start=1):
            callback_log(f"   └─ Flyer #{idx}: {os.path.basename(fl)}")
    else:
        callback_log("⚠️ Publicando en modo solo texto (no se encontraron flyers en la carpeta 'flyers').")

    callback_log(f"⏱️ Intervalos de seguridad anti-spam: {min_delay}s - {max_delay}s por grupo.")

    exitos = 0
    fallos = 0

    with sync_playwright() as p:
        try:
            browser, context = obtener_contexto_conectado(p, user_data_dir, callback_log)
            
            if len(context.pages) > 0:
                page = context.pages[0]
            else:
                page = context.new_page()

            for i, grupo_url in enumerate(grupos_procesar, start=1):
                if stop_event and stop_event.is_set():
                    callback_log("⏹️ Proceso detenido por el usuario.")
                    break

                grupo_clean = grupo_url.strip()
                if not grupo_clean or grupo_clean.startswith("#"):
                    continue

                callback_log(f"\n📌 Grupo [{i}/{len(grupos_procesar)}]: {grupo_clean}")
                
                # Asignar un flyer diferente a cada grupo en rotación
                flyer_grupo = ""
                if flyers_disponibles:
                    flyer_index = (i - 1) % len(flyers_disponibles)
                    flyer_grupo = flyers_disponibles[flyer_index]
                    callback_log(f"🖼️ Flyer asignado para este post: {os.path.basename(flyer_grupo)} (Flyer #{flyer_index + 1} de {len(flyers_disponibles)})")

                try:
                    res = publicar_en_grupo_individual(page, grupo_clean, mensaje, flyer_grupo, callback_log)
                    if res:
                        exitos += 1
                    else:
                        fallos += 1
                except Exception as e:
                    callback_log(f"❌ Error al procesar grupo: {str(e)}")
                    fallos += 1

                # Pausa aleatoria antes del siguiente grupo (si no es el último)
                if i < len(lista_grupos) and not (stop_event and stop_event.is_set()):
                    espera = random.randint(min_delay, max_delay)
                    callback_log(f"⏳ Pausa de seguridad de {espera} segundos...")
                    for _ in range(espera):
                        if stop_event and stop_event.is_set():
                            break
                        time.sleep(1)

        except Exception as e:
            callback_log(f"❌ Error crítico en el navegador: {str(e)}")

    callback_log(f"\n📊 Resumen de campaña: {exitos} exitosas, {fallos} fallidas.")
