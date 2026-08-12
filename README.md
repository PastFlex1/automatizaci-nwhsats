# 🚀 FB AutoPost Pro - Automatizador de Ventas en Facebook

Herramienta profesional en Python para automatizar publicaciones en **Grupos de Facebook** con diseño moderno en `CustomTkinter`, tecnología `Playwright`, soporte de **Spintax** anti-bloqueos y generador de anuncios de venta persuasivos.

---

## 📁 Archivos del Proyecto

- 🖥️ **`app_gui.py`**: Interfaz Gráfica de Usuario (GUI) para controlar el automatizador.
- ⚡ **`automatizador.py`**: Motor principal de automatización con Playwright.
- 🎲 **`spintax_helper.py`**: Módulo que procesa variaciones aleatorias del texto (`{opción1|opción2}`).
- ✨ **`generador_copy.py`**: Generador de anuncios persuasivos con estructura AIDA.
- 📋 **`grupos.txt`**: Archivo de texto con las URLs de los grupos de Facebook donde publicar.
- ⚙️ **`config.json`**: Ajustes de tiempos de espera e imagen seleccionada.
- 🚀 **`ejecutar.bat`**: Ejecutable rápido para iniciar la app con doble clic.

---

## 🛠️ Cómo Usar el Automatizador Paso a Paso

### 1. Iniciar la Aplicación
Haz doble clic en **`ejecutar.bat`** o ejecuta en tu terminal:
```bash
python app_gui.py
```

### 2. Conectar tu Cuenta de Facebook (Solo 1 Vez)
1. En la aplicación, haz clic en el botón azul **`🔑 1. Conectar Facebook`**.
2. Se abrirá una ventana de navegador. Inicia sesión en tu cuenta de Facebook normalmente.
3. Una vez dentro de Facebook, cierra la ventana del navegador. **Tus cookies y sesión quedarán guardadas automáticamente de forma segura en la carpeta `fb_user_data`.**

### 3. Configurar tu Anuncio y Grupos
- **Mensaje**: Puedes escribir tu anuncio usando **Spintax**. Por ejemplo:
  `{¡Hola!|Buenas tardes} {tengo en venta|ofrezco} {excelentes productos|los mejores servicios}...`
- **Generador de Copys**: Ve a la pestaña **"✨ Generador de Anuncios IA"** para usar plantillas ya listas o crear un anuncio persuasivo en segundos.
- **Imagen**: Haz clic en **"🖼️ Seleccionar Imagen"** si deseas adjuntar un flyer o foto de tu producto.
- **Grupos**: En la pestaña **"📋 Lista de Grupos"**, pega los enlaces de los grupos de Facebook a los que perteneces (ejemplo: `https://www.facebook.com/groups/ventaslocales`).

### 4. Iniciar la Campaña
1. Haz clic en el botón verde **`🚀 2. Iniciar Publicaciones`**.
2. El sistema irá publicando grupo por grupo respetando las pausas de seguridad (45 a 90 segundos aleatorios) para proteger tu cuenta contra bloqueos por spam.
3. Podrás ver el progreso en tiempo real en la consola inferior de la app.

---

## 🛡️ Consejos para Evitar Bloqueos de Facebook
1. **Usa Spintax**: Siempre varía saludos y frases en tu texto.
2. **Pausas Humanas**: No reduzcas el tiempo de espera por debajo de 45 segundos.
3. **Grupos Relevantes**: Asegúrate de estar unido a los grupos antes de publicar.
