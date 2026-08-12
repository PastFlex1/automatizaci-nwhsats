import re
import random

def parse_spintax(text: str) -> str:
    """
    Procesa texto con formato Spintax como:
    "{¡Hola!|Buenas tardes|Atención} {ofrezco|tengo disponible} {un servicio|un producto}..."
    Soporta anidación básica de variantes.
    """
    pattern = re.compile(r'\{([^{}]+)\}')
    while True:
        match = pattern.search(text)
        if not match:
            break
        options = match.group(1).split('|')
        choice = random.choice(options)
        text = text[:match.start()] + choice + text[match.end():]
    return text

if __name__ == "__main__":
    test_text = "{¡Hola!|Buenas tardes|Saludos} a todos. {Tengo|Ofrezco} {una gran oferta|excelentes productos} para {incrementar tus ventas|tu negocio}."
    print("Prueba 1:", parse_spintax(test_text))
    print("Prueba 2:", parse_spintax(test_text))
    print("Prueba 3:", parse_spintax(test_text))
