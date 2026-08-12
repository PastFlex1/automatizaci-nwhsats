"""
Modulo de Generacion de Copys Persuasivos de Ventas para Grupos de Facebook.
Utiliza estructuras probadas (AIDA, Problema-Solución, Oferta Irresistible) con formato Spintax
para maximizar respuestas y clientes potenciales.
"""

PLANTILLAS = {
    "servicios": {
        "titulo": "Servicios Profesionales / Oficios / Consultoría",
        "plantilla": (
            "{¡Hola a todos!|Buenas tardes|Atención comunidad|Saludos}\n\n"
            "{¿Estás buscando|¿Necesitas|¿Requieres} {un servicio profesional|un especialista de confianza|ayuda experta} para {tu hogar|tu negocio|tus proyectos}? 🛠️✨\n\n"
            "{Ofrezco|Brindo|Pongo a su disposición} {atención personalizada|garantía de calidad|los mejores precios del mercado} en {el sector|esta área}.\n\n"
            "✅ {Trabajos garantizados|Atención rápida e inmediata|Presupuesto sin compromiso}\n"
            "✅ {Excelentes precios|Descuentos especiales|Calidad comprobada}\n"
            "✅ {Disponibilidad inmediata|Atención 24/7|Servicio a domicilio}\n\n"
            "📲 {Escríbeme al privado|Contáctame por inbox|Envíame un mensaje de WhatsApp} {para más información|para agendar tu cita|para cotizar sin costo}.\n\n"
            "👇 {¡Déjame un comentario o un mensaje y te respondo al instante!|¡No dejes pasar esta oportunidad!}"
        )
    },
    "productos": {
        "titulo": "Venta de Productos / Artículos / Ropa / Tecnología",
        "plantilla": (
            "{¡NUEVO INGRESO!|¡OFERTA ESPECIAL!|¡EN VENTA!|¡ATENCIÓN!} 🚨🛒\n\n"
            "{Tengo disponible|A la venta|Remate imperdible de} {excelentes productos|artículos de primera calidad|stock exclusivo} {al mejor precio|a precio de remate}.\n\n"
            "✨ {Producto 100% garantizado|Ideal para regalo o uso personal|Entrega inmediata y segura}\n"
            "📦 {Envíos a domicilio|Entregas en puntos medios|Stock limitado}\n"
            "💰 {Aceptamos todos los medios de pago|Precio especial por liquidación|Descuento si llevas más de uno}\n\n"
            "📲 {Respondo mensajes directos|Mándame Inbox ahora mismo|Pide el catálogo al privado}.\n\n"
            "👉 {¡Comenta YO si te interesa y te mando info!|¡Pide el tuyo antes de que se agoten!}"
        )
    },
    "oferta": {
        "titulo": "Oferta / Descuento / Promoción Limitada",
        "plantilla": (
            "{🔥 ¡PROMO IMPERDIBLE! 🔥|⚡ ¡SOLO POR ESTA SEMANA! ⚡|💥 ¡SUPER DESCUENTO! 💥}\n\n"
            "{¿Quieres ahorrar dinero|Buscas la mejor oferta|Aprovecha antes de que finalice}? {Te ofrecemos|Tenemos para ti} {un descuento exclusivo|una promoción imperdible}.\n\n"
            "🎁 {Obtén precio especial|Incluye regalo adicional|Garantía de satisfacción}\n"
            "⏰ {Válido solo por pocos días|Cupos/Stock limitado}\n\n"
            "👇 {Comenta 'INFORMACIÓN' o escríbeme al privado|Da clic en enviar mensaje para reservar tu lugar|Envía inbox ahora mismo}.\n\n"
            "🚀 {¡Respondo de inmediato!|¡Aprovecha hoy mismo!}"
        )
    },
    "negocio_local": {
        "titulo": "Negocio Local / Comida / Tienda Física",
        "plantilla": (
            "{¡Hola vecinos y amigos!|Buenas a la comunidad|Atención barrio} 👋📍\n\n"
            "{¿Ya conocen|Visítanos en|Prueba lo mejor de} {nuestro local|nuestro emprendimiento}? {Te ofrecemos|Contamos con} {la mejor atención|los mejores productos de la zona|sabores e ingredientes de calidad}.\n\n"
            "📍 {Ubicación accesible|Atención de Lunes a Domingo|Contamos con delivery}\n"
            "🛵 {Servicio a domicilio rápido|Pide por WhatsApp}\n\n"
            "💬 {Mándanos un mensaje inbox para enviarte el menú/catálogo|Escríbenos para consultar disponibilidad}.\n\n"
            "¡Los esperamos! ❤️"
        )
    }
}

def obtener_plantillas():
    return PLANTILLAS

def generar_copy_personalizado(tipo_negocio: str, producto_servicio: str, contacto: str, beneficios: str) -> str:
    """
    Genera un copy personalizado con Spintax incorporado.
    """
    copy = (
        "{¡Hola a todos!|Buenas tardes comunidad|Atención vecinos} 👋\n\n"
        f"{{Si estás buscando|Si necesitas|¿Buscas}} **{producto_servicio}**, {{tengo una excelente noticia para ti|te puedo ayudar|tenemos la solución ideal}}.\n\n"
        f"{{Ofrezco|Brindo|Pongo a su disposición}} {producto_servicio} {{con la mejor calidad y servicio|al mejor precio|con garantía total}}.\n\n"
        "⭐ **Beneficios principales:**\n"
    )
    
    if beneficios:
        items = [b.strip() for b in beneficios.split('\n') if b.strip()]
        for item in items:
            copy += f"✅ {{ {item} | Excelente {item} }}\n"
    else:
        copy += "✅ {Atención rápida y personalizada|Servicio eficiente}\n"
        copy += "✅ {Precios justos y accesibles|La mejor relación calidad-precio}\n"
        copy += "✅ {Garantía y confianza comprobada|Satisfacción garantizada}\n"

    copy += (
        "\n📲 **¿Cómo contactar?**\n"
        f"{{Escríbeme por Inbox|Mándame un mensaje al privado|Contáctame directamente}} {{o comunícate a|a través de}}: **{contacto}**.\n\n"
        "👇 {{¡Deja tu comentario abajo y te respondo rápido!|¡Pide más detalles por mensaje privado!}}"
    )
    return copy
