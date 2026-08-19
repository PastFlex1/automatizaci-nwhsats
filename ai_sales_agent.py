import os
import json
import urllib.request
import urllib.error

OLLAMA_URL = "http://localhost:11434/api/generate"

# Cargar Modelo desde config.json
def _get_ollama_model():
    config_file = "config.json"
    if os.path.exists(config_file):
        with open(config_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("ollama_model", "llama3.1")
    return "llama3.1"

def _query_ollama(prompt):
    model = _get_ollama_model()
    data = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    
    req = urllib.request.Request(OLLAMA_URL, data=json.dumps(data).encode("utf-8"), headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            return res_data.get("response", "").strip()
    except Exception as e:
        print(f"Error conectando con Ollama local ({OLLAMA_URL}): {e}")
        return None

def generar_respuesta_ventas(mensaje_cliente, contexto_producto="", direccion="", telefonos=""):
    """
    Genera una respuesta inteligente de ventas utilizando IA Local (Ollama).
    """
    prompt = f"""
    Eres un vendedor experto de alto nivel (High Ticket) para una fábrica de equipos gastronómicos en acero inoxidable (APM Inox) en Ecuador.
    Tu objetivo no es solo dar información, sino CALIFICAR al cliente y guiarlo hacia una cotización.
    
    El cliente escribió el siguiente mensaje:
    "{mensaje_cliente}"
    
    Contexto del producto en el que está interesado (si lo hay): {contexto_producto}
    
    INSTRUCCIONES:
    1. Responde de forma amable, persuasiva y concisa (máximo 3 párrafos cortos).
    2. No des un precio exacto de inmediato a menos que el cliente sea muy insistente. Menciona que hacemos cotizaciones a medida.
    3. Haz 1 o 2 preguntas de calificación para entender su necesidad (ej. ¿En qué ciudad estás? ¿Es para un local nuevo o renovación? ¿Qué medidas aproximadas buscas?).
    4. Proporciona los siguientes datos de contacto sutilmente al final: 
       📍 Dirección: {direccion}
       📞 WhatsApp: {telefonos}
       
    Escribe únicamente la respuesta que le enviarías al cliente, sin introducciones ni comentarios adicionales.
    """

    respuesta_ia = _query_ollama(prompt)
    if respuesta_ia:
        return respuesta_ia
    
    # Fallback si falla Ollama
    from auto_responder import generar_texto_respuesta
    return generar_texto_respuesta(direccion, telefonos)


def analizar_intencion_cliente(mensaje_cliente):
    """
    Analiza el mensaje y devuelve el estado del lead: 'Caliente', 'Tibio', 'Frío'.
    """
    if not mensaje_cliente.strip():
        return "Nuevo"

    prompt = f"""
    Analiza la intención de compra en el siguiente mensaje de un cliente que pregunta por equipos gastronómicos industriales:
    "{mensaje_cliente}"
    
    Clasifícalo ESTRICTAMENTE en una de las siguientes tres categorías (responde SOLO con la palabra, sin puntos ni texto extra):
    Caliente (quiere comprar ya, pide cotización formal, pregunta medios de pago, da medidas exactas)
    Tibio (hace preguntas sobre características, pide precios, pregunta por envíos)
    Frío (solo dice "precio", "info", un punto ".", o un saludo sin preguntar nada más)
    """

    resultado = _query_ollama(prompt)
    if resultado:
        resultado = resultado.strip().lower()
        if "caliente" in resultado:
            return "Venta Cerrada" # O 'Cotizado' dependiendo de la etapa
        elif "tibio" in resultado:
            return "Interesado"
        else:
            return "Nuevo" # Frío

    return "Nuevo"


def generar_copy_marketplace(producto_base):
    """
    Genera un anuncio de alto rendimiento para FB Marketplace utilizando Spintax y Ollama.
    """
    prompt = f"""
    Eres un experto en Copywriting y ventas digitales. Genera una publicación persuasiva y de alto rendimiento para Facebook Marketplace para el siguiente producto: "{producto_base}".
    El producto es un equipo gastronómico industrial fabricado en acero inoxidable de excelente calidad, hecho en Ecuador.
    
    El texto debe estar en formato SPINTAX usando las llaves {{opcion1|opcion2}} para que el sistema pueda rotar los mensajes.
    
    La estructura obligatoria es:
    1. Título llamativo (con Spintax) usando emojis de urgencia o beneficio.
    2. Párrafo introductorio conectando con el problema del dueño de un restaurante (falta de espacio, equipos que se dañan rápido, salubridad).
    3. Beneficios clave (viñetas).
    4. Llamado a la acción (Call to action) pidiendo que comenten "INFO" o envíen un mensaje privado.
    
    Genera solo el texto en formato Spintax listo para copiar y pegar, sin introducciones tuyas.
    """

    resultado = _query_ollama(prompt)
    if resultado:
        return resultado
        
    return f"Vendo {producto_base}. Excelente calidad."
