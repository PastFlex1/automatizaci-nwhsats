import os
import time
import random
from playwright.sync_api import sync_playwright
from spintax_helper import parse_spintax
from automatizador import obtener_contexto_conectado

_ULTIMO_FLYER_MARKETPLACE = None

def obtener_flyer_marketplace_unico(imagen_path=""):
    """
    Retorna la imagen seleccionada por el usuario si existe.
    Si no, selecciona al azar un flyer de la carpeta 'flyers/'.
    """
    if imagen_path and os.path.exists(imagen_path):
        return os.path.abspath(imagen_path)

    global _ULTIMO_FLYER_MARKETPLACE
    dir_flyers = "flyers"
    if os.path.exists(dir_flyers):
        archivos = [os.path.join(dir_flyers, f) for f in os.listdir(dir_flyers) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
        if archivos:
            disponibles = [f for f in archivos if f != _ULTIMO_FLYER_MARKETPLACE] if len(archivos) > 1 else archivos
            elegido = random.choice(disponibles)
            _ULTIMO_FLYER_MARKETPLACE = elegido
            return os.path.abspath(elegido)

    return ""

def publicar_en_marketplace_item(page, titulo, precio, categoria, estado, ciudad, descripcion, imagen_path, callback_log=print):
    """
    Publica un artículo en Facebook Marketplace (https://www.facebook.com/marketplace/create/item)
    """
    url_mp = "https://www.facebook.com/marketplace/create/item"
    callback_log(f"🛒 Navegando a la sección de creación de Marketplace: {url_mp}")
    
    page.goto(url_mp, wait_until="domcontentloaded", timeout=45000)
    time.sleep(random.uniform(5, 7))

    if "login" in page.url:
        callback_log("⚠️ No estás logueado en Facebook. Por favor inicia sesión primero con el botón 'Conectar Facebook'.")
        return False

    # 1. Cargar Foto / Flyer (EXACTAMENTE 1 FLYER POR PUBLICACIÓN - Rotativo aleatorio)
    abs_img = obtener_flyer_marketplace_unico(imagen_path)
    if abs_img and os.path.exists(abs_img):
        callback_log(f"📷 Subiendo 1 flyer rotativo a Marketplace: {os.path.basename(abs_img)}")
        try:
            file_input = page.locator('input[type="file"][accept*="image"]').first
            if file_input.count() > 0:
                file_input.set_input_files([abs_img])
                callback_log("  -> 1 Flyer cargado con éxito en Marketplace.")
                time.sleep(random.uniform(4, 6))
        except Exception as e:
            callback_log(f"  ⚠️ Error al cargar foto en Marketplace: {str(e)}")

    # 2. Llenar Título (Obligatorio)
    titulo_final = parse_spintax(titulo)
    callback_log(f"📝 Escribiendo título: {titulo_final}")
    try:
        titulo_input = page.locator('label[aria-label="Título"] input, label:has-text("Título") input, input[aria-label="Título"], input[aria-label="Title"]').first
        if titulo_input.is_visible(timeout=4000):
            titulo_input.focus()
            titulo_input.fill(titulo_final)
            time.sleep(1)
    except Exception as e:
        callback_log(f"  ⚠️ Error en campo Título: {str(e)}")

    # 3. Llenar Precio (Obligatorio)
    callback_log(f"💰 Configurando precio: ${precio}")
    try:
        precio_input = page.locator('label[aria-label="Precio"] input, label:has-text("Precio") input, input[aria-label="Precio"], input[aria-label="Price"]').first
        if precio_input.is_visible(timeout=3000):
            precio_input.focus()
            precio_input.fill(str(precio))
            time.sleep(1)
    except Exception as e:
        callback_log(f"  ⚠️ Error en campo Precio: {str(e)}")

    # 4. Seleccionar Categoría (Obligatorio)
    callback_log("🏷️ Seleccionando categoría en Marketplace...")
    try:
        cat_element = None
        selectors_cat = [
            'label[aria-label*="Categoría"]',
            'div[aria-label*="Categoría"]',
            'label:has-text("Categoría")',
            'span:has-text("Categoría")',
            'div[role="combobox"]:has-text("Categoría")',
            'div:has-text("Categoría")[role="button"]'
        ]
        for s in selectors_cat:
            loc = page.locator(s).first
            if loc.count() > 0 and loc.is_visible():
                cat_element = loc
                break

        if cat_element:
            cat_element.click()
            time.sleep(2)

            opc_varios = page.locator('div[role="option"]:has-text("Varios"), span:has-text("Varios"), div[role="option"]:has-text("Herramientas"), span:has-text("Herramientas"), div[role="option"]').first
            if opc_varios.is_visible(timeout=3000):
                opc_varios.click()
                callback_log("  -> Categoría seleccionada con éxito.")
                time.sleep(1)
            else:
                page.keyboard.press("ArrowDown")
                time.sleep(0.5)
                page.keyboard.press("Enter")
                callback_log("  -> Categoría seleccionada mediante teclado.")
                time.sleep(1)
        else:
            callback_log("  ⚠️ No se encontró la casilla visual de Categoría.")
    except Exception as e:
        callback_log(f"  ⚠️ Error en Categoría: {str(e)}")

    # 5. Seleccionar Estado (Obligatorio)
    callback_log("✨ Seleccionando estado 'Nuevo'...")
    try:
        est_element = None
        selectors_est = [
            'label[aria-label*="Estado"]',
            'div[aria-label*="Estado"]',
            'label:has-text("Estado")',
            'span:has-text("Estado")',
            'div[role="combobox"]:has-text("Estado")',
            'div:has-text("Estado")[role="button"]'
        ]
        for s in selectors_est:
            loc = page.locator(s).first
            if loc.count() > 0 and loc.is_visible():
                est_element = loc
                break

        if est_element:
            est_element.click()
            time.sleep(2)

            opc_nuevo = page.locator('div[role="option"]:has-text("Nuevo"), span:has-text("Nuevo"), div[role="option"]').first
            if opc_nuevo.is_visible(timeout=3000):
                opc_nuevo.click()
                callback_log("  -> Estado 'Nuevo' seleccionado con éxito.")
                time.sleep(1)
            else:
                page.keyboard.press("ArrowDown")
                time.sleep(0.5)
                page.keyboard.press("Enter")
                callback_log("  -> Estado seleccionado mediante teclado.")
                time.sleep(1)
        else:
            callback_log("  ⚠️ No se encontró la casilla visual de Estado.")
    except Exception as e:
        callback_log(f"  ⚠️ Error en Estado: {str(e)}")

    # 6. Llenar Descripción + 20 Hashtags de Ecuador
    from tags_helper import obtener_20_tags_ecuador, obtener_tags_marketplace
    tags_20 = obtener_20_tags_ecuador()
    desc_final = parse_spintax(descripcion) + "\n\n" + tags_20

    callback_log("📝 Escribiendo descripción del anuncio con 20 hashtags de Ecuador...")
    try:
        desc_input = page.locator('label[aria-label="Descripción"] textarea, label:has-text("Descripción") textarea, textarea[aria-label="Descripción"], textarea').first
        if desc_input.is_visible(timeout=4000):
            desc_input.focus()
            desc_input.fill(desc_final)
            callback_log("  -> Descripción y 20 hashtags añadidos.")
            time.sleep(2)
    except Exception as e:
        callback_log(f"  ⚠️ Error en Descripción: {str(e)}")

    # 6.5 Llenar Etiquetas de productos (Keywords para búsquedas - 20 tags)
    try:
        callback_log("🏷️ Añadiendo las 20 etiquetas de producto para búsquedas en Ecuador...")
        tag_input = page.locator('label[aria-label*="Etiquetas de productos"] input, label[aria-label*="Etiquetas"] input, label:has-text("Etiquetas de productos") input, input[aria-label*="Etiquetas"]').first
        if tag_input.is_visible(timeout=4000):
            tag_input.focus()
            for tag_word in obtener_tags_marketplace()[:20]:
                tag_input.fill(tag_word)
                time.sleep(0.3)
                page.keyboard.press("Enter")
                time.sleep(0.3)
            callback_log("  -> 20 etiquetas de producto agregadas correctamente.")
    except Exception as e:
        callback_log(f"  ⚠️ Error en Etiquetas de productos: {str(e)}")

    # 7. Botón Siguiente / Next (Con manejo inteligente de estado)
    callback_log("👉 Avanzando al siguiente paso...")
    try:
        next_btn = page.locator('div[role="button"][aria-label*="Siguiente"], div[role="button"][aria-label*="Next"], div[aria-label*="Siguiente"], div[aria-label*="Next"]').first
        if next_btn.is_visible(timeout=4000):
            for _ in range(5):
                if next_btn.get_attribute("aria-disabled") != "true":
                    break
                time.sleep(1)

            try:
                next_btn.click(timeout=5000)
            except Exception:
                next_btn.evaluate("el => el.click()")
            time.sleep(4)
    except Exception as e:
        callback_log(f"  ⚠️ Avanzando paso: {str(e)}")

    # 8. Botón Publicar / Post
    callback_log("🚀 Enviando publicación a Marketplace...")
    try:
        pub_btn = page.locator('div[role="button"][aria-label*="Publicar"], div[role="button"][aria-label*="Publish"], div[aria-label*="Publicar"], div[aria-label*="Publish"]').first
        if pub_btn.is_visible(timeout=5000):
            for _ in range(5):
                if pub_btn.get_attribute("aria-disabled") != "true":
                    break
                time.sleep(1)

            try:
                pub_btn.click(timeout=5000)
            except Exception:
                pub_btn.evaluate("el => el.click()")

            callback_log("🎉 ¡Artículo publicado exitosamente en Facebook Marketplace!")
            time.sleep(6)
            return True
        else:
            callback_log("🎉 ¡Proceso de publicación en Marketplace completado!")
            return True
    except Exception as e:
        callback_log(f"  ⚠️ Error finalizando en Marketplace: {str(e)}")

    return True

def ejecutar_publicacion_marketplace(titulo, precio, categoria, estado, ciudad, descripcion, imagen_path="", user_data_dir="./fb_chrome_profile", callback_log=print):
    """
    Ejecuta el proceso de publicación en Marketplace.
    """
    with sync_playwright() as p:
        try:
            browser, context = obtener_contexto_conectado(p, user_data_dir, callback_log)
            if len(context.pages) > 0:
                page = context.pages[0]
            else:
                page = context.new_page()

            res = publicar_en_marketplace_item(page, titulo, precio, categoria, estado, ciudad, descripcion, imagen_path, callback_log)
            return res
        except Exception as e:
            callback_log(f"❌ Error al publicar en Marketplace: {str(e)}")
            return False
