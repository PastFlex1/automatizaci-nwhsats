import os
import time
import random
from playwright.sync_api import sync_playwright
from spintax_helper import parse_spintax
from automatizador import obtener_contexto_conectado

DIRECCION_DEFECTO = "Figueroa Oe 4-14 y 25 de Mayo (a media cuadra del Obelisco de Cotocollao)"
TELEFONOS_DEFECTO = "098 941 1821 / 099 235 0548"

def generar_texto_respuesta(direccion=DIRECCION_DEFECTO, telefonos=TELEFONOS_DEFECTO):
    template = (
        "{¡Hola!|Buenas tardes|Saludos|Gracias por escribirnos} 👋\n\n"
        f"{{Te invitamos a visitarnos en nuestro local físico:|Puedes encontrarnos en nuestra dirección:}}\n"
        f"📍 **{direccion}**\n\n"
        f"{{O comunícate directamente con nosotros a los teléfonos:|También nos puedes llamar o escribir por WhatsApp al:}}\n"
        f"📞 **{telefonos}**\n\n"
        "{{¡Te esperamos con la mejor atención y promociones!|¡Será un gusto atenderte!}} 🚀"
    )
    return parse_spintax(template)

def responder_comentarios_en_notificaciones(direccion=DIRECCION_DEFECTO, telefonos=TELEFONOS_DEFECTO, user_data_dir="./fb_chrome_profile", callback_log=print, stop_event=None):
    """
    Revisa las notificaciones recientes de Facebook y responde a los comentarios con la dirección física y números de teléfono.
    """
    callback_log("🤖 Iniciando Auto-Respondedor de Comentarios en Facebook...")
    callback_log(f"📍 Dirección: {direccion}")
    callback_log(f"📞 Teléfonos: {telefonos}")

    with sync_playwright() as p:
        try:
            browser, context = obtener_contexto_conectado(p, user_data_dir, callback_log)
            if len(context.pages) > 0:
                page = context.pages[0]
            else:
                page = context.new_page()

            # Navegar a notificaciones de Facebook
            callback_log("🔔 Navegando a Notificaciones de Facebook...")
            page.goto("https://www.facebook.com/notifications", wait_until="domcontentloaded", timeout=45000)
            time.sleep(random.uniform(5, 7))

            if "login" in page.url:
                callback_log("⚠️ No estás logueado en Facebook. Inicia sesión primero.")
                return False

            # Buscar notificaciones relacionadas a comentarios ("comentó", "commented")
            notif_items = page.locator('div[role="navigation"] a[href*="comment"], div[role="main"] a[href*="comment"], a[href*="notif_t=feedback"]').all()
            
            if not notif_items:
                callback_log("ℹ️ No se detectaron notificaciones de nuevos comentarios pendientes por el momento.")
                return True

            callback_log(f"📩 Se encontraron {len(notif_items)} notificaciones de interacciones recientes.")

            for idx, item in enumerate(notif_items[:10], start=1):
                if stop_event and stop_event.is_set():
                    callback_log("⏹️ Auto-respondedor detenido por el usuario.")
                    break

                try:
                    href = item.get_attribute("href")
                    if href:
                        url_notif = href if href.startswith("http") else "https://www.facebook.com" + href
                        callback_log(f"\n💬 Revisando comentario [{idx}/{min(10, len(notif_items))}]: {url_notif[:60]}...")
                        
                        page.goto(url_notif, wait_until="domcontentloaded", timeout=35000)
                        time.sleep(random.uniform(4, 6))

                        # Buscar la caja de texto para responder
                        reply_box_selectors = [
                            'div[role="textbox"][aria-label*="Responde"]',
                            'div[role="textbox"][aria-label*="Escribe una respuesta"]',
                            'div[role="textbox"][aria-label*="Escribe un comentario"]',
                            'div[role="textbox"][aria-label*="Write a comment"]',
                            'div[role="textbox"][aria-label*="Reply"]',
                            'div[contenteditable="true"][role="textbox"]'
                        ]

                        box = None
                        for sel in reply_box_selectors:
                            try:
                                loc = page.locator(sel).last
                                if loc.is_visible(timeout=3000):
                                    box = loc
                                    break
                            except Exception:
                                continue

                        if box:
                            # Intentar extraer el texto del comentario
                            texto_cliente = "Info"
                            try:
                                elementos_texto = page.locator('div[dir="auto"]').all_inner_texts()
                                if elementos_texto:
                                    textos_validos = [t for t in elementos_texto if len(t) > 2 and t not in ["Me gusta", "Responder", "Compartir", "Like", "Reply", "Share"]]
                                    if textos_validos:
                                        texto_cliente = textos_validos[-1]
                            except:
                                pass

                            from ai_sales_agent import generar_respuesta_ventas, analizar_intencion_cliente
                            from crm_db import registrar_o_actualizar_cliente, registrar_estadistica

                            respuesta = generar_respuesta_ventas(texto_cliente, direccion=direccion, telefonos=telefonos)
                            estado_lead = analizar_intencion_cliente(texto_cliente)
                            
                            # Registrar en CRM
                            registrar_o_actualizar_cliente(nombre="Cliente FB", perfil_fb=url_notif[:100], estado=estado_lead, interes="Equipo Gastronómico")
                            registrar_estadistica("mensajes_recibidos")
                            if estado_lead in ["Interesado", "Cotizado", "Venta Cerrada"]:
                                registrar_estadistica("clientes_interesados")

                            box.focus()
                            box.fill(respuesta)
                            time.sleep(2)
                            page.keyboard.press("Enter")
                            callback_log("✅ ¡Respuesta enviada con tu dirección y números de teléfono!")
                            time.sleep(random.uniform(5, 8))
                        else:
                            callback_log("ℹ️ Comentario ya respondido o cerrado.")

                except Exception as e:
                    callback_log(f"⚠️ Nota al procesar notificación: {str(e)}")

        except Exception as e:
            callback_log(f"❌ Error en Auto-Respondedor: {str(e)}")
            return False

    callback_log("🏁 Revisión de respuestas automáticas finalizada.")
    return True


def ejecutar_modo_continuo_24_7(lista_grupos, mensaje, imagen_path="", direccion=DIRECCION_DEFECTO, telefonos=TELEFONOS_DEFECTO, min_delay=45, max_delay=90, user_data_dir="./fb_chrome_profile", callback_log=print, stop_event=None):
    """
    Bucle continuo 24/7 que alterna entre publicar en grupos y revisar/responder comentarios de forma ininterrumpida.
    """
    from automatizador import publicar_en_grupo_individual, obtener_lista_flyers, obtener_grupos_mezclados_por_perfil

    nombre_perfil = os.path.basename(os.path.abspath(user_data_dir))
    grupos_procesar = obtener_grupos_mezclados_por_perfil(lista_grupos, user_data_dir)

    callback_log(f"⚡ MODO CONTINUO 24/7 ACTIVADO para {nombre_perfil}: Publicación + Responder Comentarios.")
    callback_log(f"🔀 Orden de {len(grupos_procesar)} grupos mezclado exclusivamente para {nombre_perfil}.")

    ronda = 1
    with sync_playwright() as p:
        try:
            browser, context = obtener_contexto_conectado(p, user_data_dir, callback_log)
            if len(context.pages) > 0:
                page = context.pages[0]
            else:
                page = context.new_page()

            flyers_disponibles = obtener_lista_flyers(imagen_path)

            while not (stop_event and stop_event.is_set()):
                callback_log(f"\n🔄 --- INICIANDO CICLO 24/7 #{ronda} ---")

                # 1. PASO A: Revisar notificaciones y responder comentarios pendientes primero
                callback_log("🔔 [24/7] Paso 1: Revisando comentarios nuevos de clientes...")
                try:
                    page.goto("https://www.facebook.com/notifications", wait_until="domcontentloaded", timeout=45000)
                    time.sleep(random.uniform(4, 6))

                    notif_items = page.locator('div[role="navigation"] a[href*="comment"], div[role="main"] a[href*="comment"], a[href*="notif_t=feedback"]').all()
                    if notif_items:
                        callback_log(f"📩 [24/7] Se encontraron {len(notif_items)} notificaciones de comentarios. Respondiendo...")
                        for idx, item in enumerate(notif_items[:5], start=1):
                            if stop_event and stop_event.is_set():
                                break
                            try:
                                href = item.get_attribute("href")
                                if href:
                                    url_notif = href if href.startswith("http") else "https://www.facebook.com" + href
                                    page.goto(url_notif, wait_until="domcontentloaded", timeout=35000)
                                    time.sleep(random.uniform(3, 5))

                                    reply_box_selectors = [
                                        'div[role="textbox"][aria-label*="Responde"]',
                                        'div[role="textbox"][aria-label*="Escribe una respuesta"]',
                                        'div[role="textbox"][aria-label*="Escribe un comentario"]',
                                        'div[role="textbox"][aria-label*="Write a comment"]',
                                        'div[role="textbox"][aria-label*="Reply"]',
                                        'div[contenteditable="true"][role="textbox"]'
                                    ]
                                    box = None
                                    for sel in reply_box_selectors:
                                        try:
                                            loc = page.locator(sel).last
                                            if loc.is_visible(timeout=2000):
                                                box = loc
                                                break
                                        except Exception:
                                            continue

                                    if box:
                                        # Intentar extraer texto
                                        texto_cliente = "Info"
                                        try:
                                            elementos_texto = page.locator('div[dir="auto"]').all_inner_texts()
                                            if elementos_texto:
                                                textos_validos = [t for t in elementos_texto if len(t) > 2 and t not in ["Me gusta", "Responder", "Compartir", "Like", "Reply", "Share"]]
                                                if textos_validos:
                                                    texto_cliente = textos_validos[-1]
                                        except:
                                            pass

                                        from ai_sales_agent import generar_respuesta_ventas, analizar_intencion_cliente
                                        from crm_db import registrar_o_actualizar_cliente, registrar_estadistica

                                        resp = generar_respuesta_ventas(texto_cliente, direccion=direccion, telefonos=telefonos)
                                        estado_lead = analizar_intencion_cliente(texto_cliente)
                                        
                                        registrar_o_actualizar_cliente(nombre="Cliente FB", perfil_fb=url_notif[:100], estado=estado_lead, interes="Equipo Gastronómico")
                                        registrar_estadistica("mensajes_recibidos")
                                        if estado_lead in ["Interesado", "Cotizado", "Venta Cerrada"]:
                                            registrar_estadistica("clientes_interesados")

                                        box.focus()
                                        box.fill(resp)
                                        time.sleep(2)
                                        page.keyboard.press("Enter")
                                        callback_log("  ✅ ¡Respuesta enviada con dirección y números de contacto!")
                                        time.sleep(random.uniform(4, 6))
                            except Exception as e:
                                callback_log(f"  ⚠️ Nota en notificaciones: {str(e)}")
                    else:
                        callback_log("  ℹ️ No hay comentarios nuevos pendientes por ahora.")
                except Exception as e:
                    callback_log(f"  ⚠️ Error revisando notificaciones: {str(e)}")

                if stop_event and stop_event.is_set():
                    break

                # 2. PASO B: Publicar en un grupo de la lista
                if grupos_procesar:
                    grupo_idx = (ronda - 1) % len(grupos_procesar)
                    grupo_clean = grupos_procesar[grupo_idx].strip()
                    if grupo_clean and not grupo_clean.startswith("#"):
                        callback_log(f"\n📢 [24/7] Paso 2: Publicando oferta en Grupo [{grupo_idx + 1}/{len(grupos_procesar)}]: {grupo_clean}")
                        
                        flyer_grupo = ""
                        if flyers_disponibles:
                            f_idx = (ronda - 1) % len(flyers_disponibles)
                            flyer_grupo = flyers_disponibles[f_idx]
                            callback_log(f"🎨 Flyer asignado: {os.path.basename(flyer_grupo)}")

                        try:
                            publicar_en_grupo_individual(page, grupo_clean, mensaje, flyer_grupo, callback_log)
                        except Exception as e:
                            callback_log(f"❌ Error al publicar en grupo: {str(e)}")

                if stop_event and stop_event.is_set():
                    break

                # 3. PASO C: Espera de ciclo 24/7
                espera_ciclo = random.randint(min_delay, max_delay)
                callback_log(f"\n⏳ [24/7] En espera por {espera_ciclo} segundos antes del siguiente ciclo...")
                for _ in range(espera_ciclo):
                    if stop_event and stop_event.is_set():
                        break
                    time.sleep(1)

                ronda += 1

        except Exception as e:
            callback_log(f"❌ Error crítico en Modo 24/7: {str(e)}")

    callback_log("🏁 Modo 24/7 detenido por el usuario.")
