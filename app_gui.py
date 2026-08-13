import os
import json
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import customtkinter as ctk

from spintax_helper import parse_spintax
from generador_copy import obtener_plantillas, generar_copy_personalizado
from automatizador import abrir_navegador_para_login, ejecutar_automatizacion
from automatizador_marketplace import ejecutar_publicacion_marketplace
from auto_responder import responder_comentarios_en_notificaciones, ejecutar_modo_continuo_24_7, DIRECCION_DEFECTO, TELEFONOS_DEFECTO

# Configuración de tema
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

CONFIG_FILE = "config.json"
GRUPOS_FILE = "grupos.txt"
FLYERS_DIR = "flyers"

class FBAutomatorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        os.makedirs(FLYERS_DIR, exist_ok=True)

        self.title("FB AutoPost Pro - Automatizador de Ventas en Facebook")
        self.geometry("980x740")
        self.minsize(900, 680)

        self.stop_event = threading.Event()
        self.is_running = False

        # Cargar configuración inicial
        self.config_data = self.cargar_configuracion()

        # Layout Principal (Tabs + Status/Controls)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Tabview
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=0, column=0, padx=15, pady=10, sticky="nsew")

        self.tab_campana = self.tabview.add("📢 Configurar Campaña")
        self.tab_grupos = self.tabview.add("📋 Lista de Grupos")
        self.tab_marketplace = self.tabview.add("🛒 Publicar en Marketplace")
        self.tab_responder = self.tabview.add("💬 Auto-Respondedor")
        self.tab_copy = self.tabview.add("✨ Generador de Anuncios IA")

        # Construir UI en cada pestaña
        self.crear_tab_campana()
        self.crear_tab_grupos()
        self.crear_tab_marketplace()
        self.crear_tab_responder()
        self.crear_tab_copy()

        # Panel Inferior: Botones de Acción y Logs
        self.crear_panel_inferior()

        # Cargar datos guardados
        self.cargar_grupos_desde_archivo()

    def cargar_configuracion(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "min_delay": 45,
            "max_delay": 90,
            "image_path": "",
            "message_template": "{🔥 ¡TODO EN ACERO INOXIDABLE DIRECTO DE FÁBRICA! 🔥|🛠️ ¡FABRICANTES DIRECTOS EN ACERO INOXIDABLE! 🛠️|⚡ ¡EQUIPA TU NEGOCIO CON APM INOX! ⚡}\n\n{¿Empiezas un negocio o quieres renovar tus equipos?|¿Buscas máxima calidad al mejor precio de fábrica?|En APM Inox diseñamos y fabricamos exactamente lo que necesitas:}\n\n✨ **{Lo que fabricamos para ti|Nuestros productos principales}:**\n🔥 {Hornos y cocinas industriales de alta eficiencia|Cocinas industriales y hornos a medida}\n🏪 {Góndolas, estanterías y exhibidores|Estanterías y góndolas reforzadas}\n💨 {Campanas de extracción|Campanas y sistemas de extracción}\n🛠️ {Equipos, mesas y accesorios en acero inox|Muebles y artículos 100% acero inoxidable}\n📐 {Fabricación 100% a medida para tu espacio|Diseños personalizados según tu requerimiento}\n\n🚚 **{📦 Envíos a domicilio a todo el Ecuador 🇪🇨|📦 Hacemos envíos seguros a todas las provincias de Ecuador 🇪🇨|📦 Envíos garantizados a nivel nacional 🇪🇨}**\n\n📍 **{Visítanos en nuestro local:|Ubicación exacta:}**\n**Figueroa Oe 4-14 y 25 de Mayo** (a media cuadra del Obelisco de Cotocollao).\n\n📲 **{Cotiza gratis hoy mismo:|Contactos e informes inmediatos:}**\n📞 **098 941 1821** / **099 235 0548**\n\n💬 {¡Escríbenos por WhatsApp o Inbox y te respondemos de inmediato!|¡Te enviamos fotos, catálogo y presupuestos al instante!}\n\n🚀 **APM Inox** — *Tú lo imaginas, nosotros lo fabricamos.*"
        }

    def guardar_configuracion(self):
        self.config_data["min_delay"] = int(self.entry_min_delay.get())
        self.config_data["max_delay"] = int(self.entry_max_delay.get())
        self.config_data["message_template"] = self.txt_mensaje.get("1.0", "end-1c")
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(self.config_data, f, indent=2, ensure_ascii=False)

    # ---------------- TAB CAMPAÑA ----------------
    def crear_tab_campana(self):
        self.tab_campana.grid_columnconfigure(0, weight=1)
        self.tab_campana.grid_rowconfigure(1, weight=1)

        # Frame Superior: Opciones de Mensaje
        lbl_msg = ctk.CTkLabel(self.tab_campana, text="Mensaje de la Publicación (Soporta Spintax entre {opcion1|opcion2}):", font=ctk.CTkFont(size=14, weight="bold"))
        lbl_msg.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")

        self.txt_mensaje = ctk.CTkTextbox(self.tab_campana, font=ctk.CTkFont(size=13))
        self.txt_mensaje.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        self.txt_mensaje.insert("1.0", self.config_data.get("message_template", ""))

        # Frame de botones de utilidad para el mensaje
        frame_msg_tools = ctk.CTkFrame(self.tab_campana, fg_color="transparent")
        frame_msg_tools.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

        btn_spintax_preview = ctk.CTkButton(frame_msg_tools, text="🎲 Probar Spintax (Vista Previa)", command=self.probar_spintax, fg_color="#2b5c8f")
        btn_spintax_preview.pack(side="left", padx=5)

        btn_limpiar = ctk.CTkButton(frame_msg_tools, text="🧹 Limpiar Texto", command=lambda: self.txt_mensaje.delete("1.0", "end"), fg_color="#555555")
        btn_limpiar.pack(side="left", padx=5)

        # Frame de Imagen y Tiempos
        frame_settings = ctk.CTkFrame(self.tab_campana)
        frame_settings.grid(row=3, column=0, padx=10, pady=10, sticky="ew")
        frame_settings.grid_columnconfigure(1, weight=1)

        # Imagen
        ctk.CTkLabel(frame_settings, text="Imagen / Flyer Publicitario:", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        saved_img = self.config_data.get("image_path") or ""
        display_txt = os.path.basename(saved_img) if (saved_img and os.path.exists(saved_img)) else ("Ninguna imagen seleccionada" if not saved_img else f"{os.path.basename(saved_img)} (no encontrada)")
        display_color = "#00ffcc" if (saved_img and os.path.exists(saved_img)) else "#aaaaaa"

        self.lbl_img_path = ctk.CTkLabel(frame_settings, text=display_txt, anchor="w", text_color=display_color)
        self.lbl_img_path.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        frame_img_btns = ctk.CTkFrame(frame_settings, fg_color="transparent")
        frame_img_btns.grid(row=0, column=2, padx=10, pady=10)

        btn_open_folder = ctk.CTkButton(frame_img_btns, text="📂 Abrir Carpeta 'flyers'", command=self.abrir_carpeta_flyers, width=150, fg_color="#2b5c8f", hover_color="#1e4066")
        btn_open_folder.pack(side="left", padx=2)

        btn_select_img = ctk.CTkButton(frame_img_btns, text="🖼️ Buscar Flyer...", command=self.seleccionar_imagen, width=140)
        btn_select_img.pack(side="left", padx=2)

        btn_clear_img = ctk.CTkButton(frame_img_btns, text="❌ Quitar", command=self.quitar_imagen, width=65, fg_color="#777777")
        btn_clear_img.pack(side="left", padx=2)

        # Delays
        frame_delays = ctk.CTkFrame(frame_settings, fg_color="transparent")
        frame_delays.grid(row=1, column=0, columnspan=3, padx=10, pady=(0, 10), sticky="w")

        ctk.CTkLabel(frame_delays, text="Pausa Mínima (seg):").pack(side="left", padx=(0, 5))
        self.entry_min_delay = ctk.CTkEntry(frame_delays, width=60)
        self.entry_min_delay.pack(side="left", padx=(0, 15))
        self.entry_min_delay.insert(0, str(self.config_data.get("min_delay", 45)))

        ctk.CTkLabel(frame_delays, text="Pausa Máxima (seg):").pack(side="left", padx=(0, 5))
        self.entry_max_delay = ctk.CTkEntry(frame_delays, width=60)
        self.entry_max_delay.pack(side="left", padx=(0, 15))
        self.entry_max_delay.insert(0, str(self.config_data.get("max_delay", 90)))

        ctk.CTkLabel(frame_delays, text="*(Tiempos recomendados para evitar bloqueos por spam)", text_color="#888888", font=ctk.CTkFont(size=11)).pack(side="left")

    def probar_spintax(self):
        original = self.txt_mensaje.get("1.0", "end-1c")
        if not original.strip():
            messagebox.showwarning("Atención", "Escribe primero un texto con formato Spintax.")
            return
        muestra = parse_spintax(original)
        messagebox.showinfo("🎲 Vista Previa de Spintax Generada", f"Esta es una variación aleatoria generada:\n\n{muestra}")

    def abrir_carpeta_flyers(self):
        abs_flyers = os.path.abspath(FLYERS_DIR)
        os.makedirs(abs_flyers, exist_ok=True)
        try:
            os.startfile(abs_flyers)
        except Exception:
            messagebox.showinfo("Carpeta Flyers", f"La carpeta de flyers está en:\n{abs_flyers}")

    def seleccionar_imagen(self):
        initial_dir = os.path.abspath(FLYERS_DIR)
        filepath = filedialog.askopenfilename(
            title="Selecciona tu flyer o imagen publicitaria",
            initialdir=initial_dir,
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.webp *.gif")]
        )
        if filepath:
            self.config_data["image_path"] = filepath
            self.lbl_img_path.configure(text=os.path.basename(filepath), text_color="#00ffcc")
            self.guardar_configuracion()

    def quitar_imagen(self):
        self.config_data["image_path"] = ""
        self.lbl_img_path.configure(text="Ninguna imagen seleccionada", text_color="#aaaaaa")
        self.guardar_configuracion()

    # ---------------- TAB GRUPOS ----------------
    def crear_tab_grupos(self):
        self.tab_grupos.grid_columnconfigure(0, weight=1)
        self.tab_grupos.grid_rowconfigure(1, weight=1)

        lbl_info = ctk.CTkLabel(self.tab_grupos, text="Pega las URLs de los Grupos de Facebook (una por línea):", font=ctk.CTkFont(size=14, weight="bold"))
        lbl_info.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")

        self.txt_grupos = ctk.CTkTextbox(self.tab_grupos, font=ctk.CTkFont(size=13))
        self.txt_grupos.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")

        frame_grupo_tools = ctk.CTkFrame(self.tab_grupos, fg_color="transparent")
        frame_grupo_tools.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

        btn_guardar_g = ctk.CTkButton(frame_grupo_tools, text="💾 Guardar en grupos.txt", command=self.guardar_grupos_a_archivo)
        btn_guardar_g.pack(side="left", padx=5)

        btn_cargar_g = ctk.CTkButton(frame_grupo_tools, text="📂 Recargar desde grupos.txt", command=self.cargar_grupos_desde_archivo, fg_color="#555555")
        btn_cargar_g.pack(side="left", padx=5)

        self.lbl_grupo_count = ctk.CTkLabel(frame_grupo_tools, text="Total Grupos: 0", font=ctk.CTkFont(weight="bold"))
        self.lbl_grupo_count.pack(side="right", padx=10)

        self.txt_grupos.bind("<KeyRelease>", self.actualizar_conteo_grupos)

    def cargar_grupos_desde_archivo(self):
        if os.path.exists(GRUPOS_FILE):
            with open(GRUPOS_FILE, "r", encoding="utf-8") as f:
                contenido = f.read()
                self.txt_grupos.delete("1.0", "end")
                self.txt_grupos.insert("1.0", contenido)
        self.actualizar_conteo_grupos()

    def guardar_grupos_a_archivo(self):
        contenido = self.txt_grupos.get("1.0", "end-1c")
        with open(GRUPOS_FILE, "w", encoding="utf-8") as f:
            f.write(contenido)
        messagebox.showinfo("Éxito", "La lista de grupos ha sido guardada en grupos.txt")
        self.actualizar_conteo_grupos()

    def extraer_urls_validas(self, texto):
        urls = []
        for line in texto.split("\n"):
            clean = line.strip()
            if "facebook.com" in clean:
                clean = clean.lstrip("#").strip()
                if not clean.startswith("http"):
                    clean = "https://" + clean
                urls.append(clean)
        return urls

    def actualizar_conteo_grupos(self, event=None):
        texto = self.txt_grupos.get("1.0", "end-1c")
        validas = self.extraer_urls_validas(texto)
        self.lbl_grupo_count.configure(text=f"Total Grupos Válidos: {len(validas)}")

    # ---------------- TAB MARKETPLACE ----------------
    def crear_tab_marketplace(self):
        self.tab_marketplace.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self.tab_marketplace, text="Publicar Artículo en Facebook Marketplace:", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, columnspan=2, padx=15, pady=(15, 10), sticky="w")

        # Título
        ctk.CTkLabel(self.tab_marketplace, text="Título del Anuncio:").grid(row=1, column=0, padx=15, pady=5, sticky="w")
        self.entry_mp_titulo = ctk.CTkEntry(self.tab_marketplace, placeholder_text="{Muebles en Acero Inoxidable|Trabajos A Medida}")
        self.entry_mp_titulo.grid(row=1, column=1, padx=15, pady=5, sticky="ew")
        self.entry_mp_titulo.insert(0, "{Trabajos en Acero Inoxidable|Muebles en Inox A Medida}")

        # Precio
        ctk.CTkLabel(self.tab_marketplace, text="Precio ($):").grid(row=2, column=0, padx=15, pady=5, sticky="w")
        self.entry_mp_precio = ctk.CTkEntry(self.tab_marketplace, width=120)
        self.entry_mp_precio.grid(row=2, column=1, padx=15, pady=5, sticky="w")
        self.entry_mp_precio.insert(0, "1")

        # Categoría
        ctk.CTkLabel(self.tab_marketplace, text="Categoría:").grid(row=3, column=0, padx=15, pady=5, sticky="w")
        self.entry_mp_cat = ctk.CTkEntry(self.tab_marketplace, placeholder_text="Herramientas / Varios")
        self.entry_mp_cat.grid(row=3, column=1, padx=15, pady=5, sticky="ew")
        self.entry_mp_cat.insert(0, "Varios")

        # Estado
        ctk.CTkLabel(self.tab_marketplace, text="Estado del Producto:").grid(row=4, column=0, padx=15, pady=5, sticky="w")
        self.entry_mp_estado = ctk.CTkEntry(self.tab_marketplace, placeholder_text="Nuevo")
        self.entry_mp_estado.grid(row=4, column=1, padx=15, pady=5, sticky="w")
        self.entry_mp_estado.insert(0, "Nuevo")

        # Información de Selección de Imagen en Marketplace
        lbl_img_info = ctk.CTkLabel(
            self.tab_marketplace,
            text="📷 Imagen del Anuncio: Se seleccionará EXACTAMENTE 1 flyer rotativo al azar de tu carpeta 'flyers/' (40 imágenes disponibles) para cada publicación de Marketplace sin repetir el anterior.",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#27ae60",
            justify="left",
            wraplength=750
        )
        lbl_img_info.grid(row=5, column=0, columnspan=2, padx=15, pady=(10, 5), sticky="w")

        # Botón de Publicación directa en Marketplace
        btn_pub_mp = ctk.CTkButton(
            self.tab_marketplace,
            text="🛒 Publicar Ahora en Facebook Marketplace",
            command=self.iniciar_publicacion_marketplace,
            fg_color="#e67e22",
            hover_color="#d35400",
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        btn_pub_mp.grid(row=6, column=0, columnspan=2, padx=15, pady=20)

    def iniciar_publicacion_marketplace(self):
        if self.is_running:
            return

        self.guardar_configuracion()

        titulo = self.entry_mp_titulo.get().strip()
        precio = self.entry_mp_precio.get().strip()
        cat = self.entry_mp_cat.get().strip()
        estado = self.entry_mp_estado.get().strip()
        
        # Usar el mensaje del editor principal o el de la configuración guardada
        mensaje = self.txt_mensaje.get("1.0", "end-1c").strip()
        if not mensaje:
            mensaje = self.config_data.get("message_template", "")

        if not titulo:
            messagebox.showwarning("Atención", "Por favor ingresa un título para el anuncio de Marketplace.")
            return

        if not mensaje:
            messagebox.showwarning("Atención", "Por favor ingresa la descripción del anuncio en la pestaña '📢 Configurar Campaña'.")
            return

        self.stop_event.clear()
        self.is_running = True

        self.btn_start.configure(state="disabled")
        self.btn_login.configure(state="disabled")
        self.btn_mode_247.configure(state="disabled")
        self.btn_stop.configure(state="normal")

        perfil_nom = self.combo_perfiles.get() if hasattr(self, "combo_perfiles") else "Perfil 1"
        self.log(f"\n🛒 Iniciando publicación en Facebook Marketplace con {perfil_nom}...")

        img_path = self.config_data.get("image_path", "")

        def run_mp_thread():
            try:
                ejecutar_publicacion_marketplace(
                    titulo=titulo,
                    precio=precio,
                    categoria=cat,
                    estado=estado,
                    ciudad="Quito",
                    descripcion=mensaje,
                    imagen_path="",
                    user_data_dir=self.obtener_directorio_perfil(),
                    callback_log=self.log
                )
            finally:
                self.is_running = False
                self.after(0, self.finalizar_campana)

        threading.Thread(target=run_mp_thread, daemon=True).start()

    # ---------------- TAB AUTO-RESPONDER ----------------
    def crear_tab_responder(self):
        self.tab_responder.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self.tab_responder, text="Auto-Respondedor Inteligente de Comentarios:", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, columnspan=2, padx=15, pady=(15, 10), sticky="w")

        # Dirección física
        ctk.CTkLabel(self.tab_responder, text="Dirección Física del Local:").grid(row=1, column=0, padx=15, pady=8, sticky="w")
        self.entry_resp_dir = ctk.CTkEntry(self.tab_responder, placeholder_text="Dirección completa...")
        self.entry_resp_dir.grid(row=1, column=1, padx=15, pady=8, sticky="ew")
        self.entry_resp_dir.insert(0, DIRECCION_DEFECTO)

        # Teléfonos de contacto
        ctk.CTkLabel(self.tab_responder, text="Teléfonos de Contacto:").grid(row=2, column=0, padx=15, pady=8, sticky="w")
        self.entry_resp_tel = ctk.CTkEntry(self.tab_responder, placeholder_text="Teléfonos de WhatsApp/Llamadas...")
        self.entry_resp_tel.grid(row=2, column=1, padx=15, pady=8, sticky="ew")
        self.entry_resp_tel.insert(0, TELEFONOS_DEFECTO)

        # Explicación
        lbl_info = ctk.CTkLabel(
            self.tab_responder,
            text="📌 Esta función revisa tus notificaciones y responde automáticamente a las personas que pregunten en tus publicaciones,\nenviándoles la dirección exacta de tu local físico y tus números telefónicos para cerrar la venta.",
            font=ctk.CTkFont(size=11),
            text_color="#bbbbbb",
            justify="left"
        )
        lbl_info.grid(row=3, column=0, columnspan=2, padx=15, pady=15, sticky="w")

        # Botón Activar Auto-Respondedor
        btn_start_resp = ctk.CTkButton(
            self.tab_responder,
            text="🤖 Activar Auto-Respondedor de Comentarios",
            command=self.iniciar_auto_responder,
            fg_color="#8e44ad",
            hover_color="#732d91",
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        btn_start_resp.grid(row=4, column=0, columnspan=2, padx=15, pady=20)

    def iniciar_auto_responder(self):
        if self.is_running:
            return

        direccion = self.entry_resp_dir.get().strip()
        telefonos = self.entry_resp_tel.get().strip()

        if not direccion or not telefonos:
            messagebox.showwarning("Atención", "Por favor completa la dirección y los teléfonos.")
            return

        self.stop_event.clear()
        self.is_running = True
        self.log("\n🤖 Iniciando Auto-Respondedor de Comentarios...")

        def run_resp_thread():
            try:
                responder_comentarios_en_notificaciones(
                    direccion=direccion,
                    telefonos=telefonos,
                    user_data_dir=self.obtener_directorio_perfil(),
                    callback_log=self.log,
                    stop_event=self.stop_event
                )
            finally:
                self.is_running = False

        threading.Thread(target=run_resp_thread, daemon=True).start()

    # ---------------- TAB GENERADOR DE COPY ----------------
    def crear_tab_copy(self):
        self.tab_copy.grid_columnconfigure(0, weight=1)

        lbl = ctk.CTkLabel(self.tab_copy, text="Selecciona una Plantilla de Ventas para tu Negocio:", font=ctk.CTkFont(size=14, weight="bold"))
        lbl.pack(anchor="w", padx=15, pady=(15, 5))

        plantillas = obtener_plantillas()

        frame_btns = ctk.CTkFrame(self.tab_copy)
        frame_btns.pack(fill="x", padx=15, pady=5)

        for clave, data in plantillas.items():
            btn = ctk.CTkButton(
                frame_btns,
                text=data["titulo"],
                command=lambda p=data["plantilla"]: self.usar_plantilla(p),
                fg_color="#1f538d",
                height=35
            )
            btn.pack(side="left", padx=5, pady=10, expand=True)

        # Generador por formulario
        frame_form = ctk.CTkFrame(self.tab_copy)
        frame_form.pack(fill="both", expand=True, padx=15, pady=10)
        frame_form.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(frame_form, text="o Crea un Anuncio Personalizado con IA:", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="w")

        ctk.CTkLabel(frame_form, text="Producto / Servicio:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.entry_copy_prod = ctk.CTkEntry(frame_form, placeholder_text="ej. Reparación de Laptops / Calzado Deportivo")
        self.entry_copy_prod.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(frame_form, text="Contacto / WhatsApp:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.entry_copy_contact = ctk.CTkEntry(frame_form, placeholder_text="ej. 55-1234-5678 o Inbox")
        self.entry_copy_contact.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(frame_form, text="Beneficios Clave (uno por línea):").grid(row=3, column=0, padx=10, pady=5, sticky="nw")
        self.txt_copy_ben = ctk.CTkTextbox(frame_form, height=70)
        self.txt_copy_ben.grid(row=3, column=1, padx=10, pady=5, sticky="ew")
        self.txt_copy_ben.insert("1.0", "Atención rápida a domicilio\nDescuento del 15% esta semana\nGarantía de 6 meses")

        btn_gen_form = ctk.CTkButton(frame_form, text="⚡ Generar Anuncio con Spintax y Enviar a Campaña", command=self.generar_copy_formulario, fg_color="#27ae60", hover_color="#219150")
        btn_gen_form.grid(row=4, column=0, columnspan=2, padx=10, pady=15)

    def usar_plantilla(self, plantilla):
        self.txt_mensaje.delete("1.0", "end")
        self.txt_mensaje.insert("1.0", plantilla)
        self.tabview.set("📢 Configurar Campaña")
        messagebox.showinfo("Copiado", "Plantilla cargada en la pestaña '📢 Configurar Campaña'.")

    def generar_copy_formulario(self):
        prod = self.entry_copy_prod.get()
        contact = self.entry_copy_contact.get()
        ben = self.txt_copy_ben.get("1.0", "end-1c")

        if not prod or not contact:
            messagebox.showwarning("Campos vacíos", "Por favor completa el producto y el contacto.")
            return

        copy_resultado = generar_copy_personalizado("general", prod, contact, ben)
        self.txt_mensaje.delete("1.0", "end")
        self.txt_mensaje.insert("1.0", copy_resultado)
        self.tabview.set("📢 Configurar Campaña")
        messagebox.showinfo("¡Listo!", "Anuncio generado con Spintax y cargado en la campaña.")

    # ---------------- PANEL INFERIOR & LOGS ----------------
    def crear_panel_inferior(self):
        # Consola de Logs (se crea primero para recibir logs sin error)
        lbl_log = ctk.CTkLabel(self, text="Consola de Avance en Tiempo Real:", font=ctk.CTkFont(size=12, weight="bold"))
        lbl_log.grid(row=2, column=0, padx=15, pady=(0, 2), sticky="w")

        self.txt_log = ctk.CTkTextbox(self, height=140, font=ctk.CTkFont(family="Consolas", size=12), fg_color="#1e1e1e")
        self.txt_log.grid(row=3, column=0, padx=15, pady=(0, 15), sticky="nsew")

        frame_controls = ctk.CTkFrame(self)
        frame_controls.grid(row=1, column=0, padx=15, pady=(0, 10), sticky="ew")

        # Selector de Perfil Multi-Cuenta
        ctk.CTkLabel(frame_controls, text="👤 Cuenta FB:", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=(10, 2))
        self.combo_perfiles = ctk.CTkComboBox(frame_controls, values=["Perfil 1", "Perfil 2", "Perfil 3", "Perfil 4"], width=110, command=self.al_cambiar_perfil)
        self.combo_perfiles.pack(side="left", padx=(0, 10))
        self.combo_perfiles.set(self.config_data.get("current_profile", "Perfil 1"))

        # Botones Principales
        self.btn_login = ctk.CTkButton(frame_controls, text="🔑 1. Conectar FB", command=self.iniciar_login, fg_color="#1877f2", hover_color="#1154a4", height=40, font=ctk.CTkFont(size=13, weight="bold"))
        self.btn_login.pack(side="left", padx=4, pady=10)

        self.btn_start = ctk.CTkButton(frame_controls, text="🚀 2. Publicar en Grupos", command=self.iniciar_campana, fg_color="#27ae60", hover_color="#1e8449", height=40, font=ctk.CTkFont(size=13, weight="bold"))
        self.btn_start.pack(side="left", padx=4, pady=10)

        self.btn_mode_247 = ctk.CTkButton(frame_controls, text="⚡ 3. MODO 24/7 (Publicar + Responder)", command=self.iniciar_modo_247, fg_color="#8e44ad", hover_color="#732d91", height=40, font=ctk.CTkFont(size=13, weight="bold"))
        self.btn_mode_247.pack(side="left", padx=4, pady=10)

        self.btn_stop = ctk.CTkButton(frame_controls, text="⏹️ Detener", command=self.detener_campana, fg_color="#c0392b", hover_color="#962d22", height=40, state="disabled")
        self.btn_stop.pack(side="left", padx=4, pady=10)

    def log(self, mensaje):
        print(str(mensaje))
        if hasattr(self, "txt_log") and self.txt_log is not None:
            try:
                self.txt_log.insert("end", str(mensaje) + "\n")
                self.txt_log.see("end")
            except Exception:
                pass

    def obtener_directorio_perfil(self):
        perfil = self.combo_perfiles.get() if hasattr(self, "combo_perfiles") else "Perfil 1"
        perfil_clean = perfil.lower().replace(" ", "_")
        return f"./fb_chrome_profile_{perfil_clean}"

    def al_cambiar_perfil(self, nuevo_perfil):
        self.config_data["current_profile"] = nuevo_perfil
        self.guardar_configuracion()
        self.log(f"👤 Cambiado a {nuevo_perfil} (Carpeta de sesión: {self.obtener_directorio_perfil()})")

    def extraer_urls_validas(self, texto_grupos=""):
        """
        Extrae URLs válidas de grupos de Facebook del texto de la UI o lee directamente del archivo grupos.txt.
        """
        urls = []
        if texto_grupos:
            for line in texto_grupos.splitlines():
                line_clean = line.strip()
                if line_clean and not line_clean.startswith("#") and "facebook.com/groups" in line_clean:
                    if not line_clean.startswith("http"):
                        line_clean = "https://" + line_clean.lstrip("/")
                    urls.append(line_clean)

        if not urls and os.path.exists(GRUPOS_FILE):
            with open(GRUPOS_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    l = line.strip()
                    if l and not l.startswith("#") and "facebook.com/groups" in l:
                        urls.append(l)

        return urls

    def iniciar_modo_247(self):
        if self.is_running:
            return

        self.guardar_configuracion()
        self.guardar_grupos_a_archivo()

        mensaje = self.txt_mensaje.get("1.0", "end-1c").strip()
        if not mensaje:
            mensaje = self.config_data.get("message_template", "")

        if not mensaje:
            messagebox.showwarning("Atención", "Escribe un mensaje en la pestaña de campaña antes de iniciar el Modo 24/7.")
            return

        grupos = self.extraer_urls_validas(self.txt_grupos.get("1.0", "end-1c"))

        if not grupos:
            messagebox.showwarning("Atención", "No hay URLs válidas de grupos en la lista. Agrega al menos un grupo en la pestaña 'Lista de Grupos'.")
            return

        self.stop_event.clear()
        self.is_running = True

        self.btn_start.configure(state="disabled")
        self.btn_login.configure(state="disabled")
        self.btn_mode_247.configure(state="disabled")
        self.btn_stop.configure(state="normal")

        img_path = self.config_data.get("image_path", "")
        min_d = int(self.entry_min_delay.get())
        max_d = int(self.entry_max_delay.get())
        dir_local = getattr(self, "entry_resp_dir", None)
        tel_local = getattr(self, "entry_resp_tel", None)
        
        direccion = dir_local.get().strip() if dir_local else DIRECCION_DEFECTO
        telefonos = tel_local.get().strip() if tel_local else TELEFONOS_DEFECTO

        def run_247_thread():
            try:
                ejecutar_modo_continuo_24_7(
                    lista_grupos=grupos,
                    mensaje=mensaje,
                    imagen_path=img_path,
                    direccion=direccion,
                    telefonos=telefonos,
                    min_delay=min_d,
                    max_delay=max_d,
                    user_data_dir=self.obtener_directorio_perfil(),
                    callback_log=self.log,
                    stop_event=self.stop_event
                )
            finally:
                self.is_running = False
                self.after(0, self.finalizar_campana)

        threading.Thread(target=run_247_thread, daemon=True).start()

    # ---------------- ACCIONES DE AUTOMATIZACIÓN ----------------
    def iniciar_login(self):
        perfil_actual = self.combo_perfiles.get()
        self.log(f"🌐 Abriendo navegador para conectar {perfil_actual} de Facebook...")
        threading.Thread(target=abrir_navegador_para_login, args=(self.obtener_directorio_perfil(), self.log), daemon=True).start()

    def iniciar_campana(self):
        if self.is_running:
            return

        # Guardar configuraciones
        self.guardar_configuracion()
        self.guardar_grupos_a_archivo()

        mensaje = self.txt_mensaje.get("1.0", "end-1c").strip()
        if not mensaje:
            messagebox.showwarning("Atención", "Escribe un mensaje antes de iniciar.")
            return

        texto_grupos = self.txt_grupos.get("1.0", "end-1c")
        grupos = self.extraer_urls_validas(texto_grupos)

        if not grupos:
            messagebox.showwarning("Atención", "No hay URLs válidas de grupos de Facebook en la lista.")
            return

        self.stop_event.clear()
        self.is_running = True

        self.btn_start.configure(state="disabled")
        self.btn_login.configure(state="disabled")
        self.btn_stop.configure(state="normal")

        img_path = self.config_data.get("image_path", "")
        min_d = int(self.entry_min_delay.get())
        max_d = int(self.entry_max_delay.get())

        def run_thread():
            try:
                ejecutar_automatizacion(
                    lista_grupos=grupos,
                    mensaje=mensaje,
                    imagen_path=img_path,
                    min_delay=min_d,
                    max_delay=max_d,
                    user_data_dir=self.obtener_directorio_perfil(),
                    callback_log=self.log,
                    stop_event=self.stop_event
                )
            finally:
                self.is_running = False
                self.after(0, self.finalizar_campana)

        threading.Thread(target=run_thread, daemon=True).start()

    def detener_campana(self):
        if self.is_running:
            self.log("⏳ Solicitando detención de la campaña...")
            self.stop_event.set()

    def finalizar_campana(self):
        self.btn_start.configure(state="normal")
        self.btn_login.configure(state="normal")
        self.btn_mode_247.configure(state="normal")
        self.btn_stop.configure(state="disabled")
        self.log("🏁 Proceso finalizado.")

if __name__ == "__main__":
    app = FBAutomatorApp()
    app.mainloop()
