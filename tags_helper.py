import random

# Pool de hashtags altamente relevantes para APM Inox y ventas en Ecuador
TAGS_POOL = [
    "#AceroInoxidable",
    "#APMInox",
    "#Quito",
    "#Cotocollao",
    "#HornosIndustriales",
    "#CocinasIndustriales",
    "#Gondolas",
    "#Estanterias",
    "#CampanasDeExtraccion",
    "#FabricantesEcuador",
    "#RestaurantesQuito",
    "#GastronomiaEcuador",
    "#EquiposHosteleria",
    "#MueblesAmedida",
    "#EmprendedoresEcuador",
    "#OfertasQuito"
]

# Lista exacta de 20 hashtags optimizados específicamente para Ecuador
TAGS_ECUADOR_20 = [
    "#AceroInoxidableEcuador",
    "#APMInox",
    "#QuitoEcuador",
    "#CotocollaoQuito",
    "#HornosIndustrialesEcuador",
    "#CocinasIndustrialesQuito",
    "#GondolasEcuador",
    "#EstanteriasQuito",
    "#CampanasDeExtraccion",
    "#FabricantesEcuador",
    "#RestaurantesQuito",
    "#GastronomiaEcuador",
    "#EquiposHosteleriaEcuador",
    "#MueblesEnInox",
    "#EmprendedoresEcuador",
    "#OfertasQuito",
    "#VentasEcuador",
    "#NegociosQuito",
    "#VentasQuito",
    "#EcuadorEnviando"
]

# 20 Palabras clave de etiquetas de producto para Marketplace (Ecuador)
TAGS_MARKETPLACE_KEYWORDS = [
    "acero inoxidable",
    "hornos industriales",
    "cocinas industriales",
    "gondolas",
    "estanterias",
    "campanas de extraccion",
    "muebles a medida",
    "restaurantes quito",
    "cotocollao",
    "equipos cocina",
    "quito ecuador",
    "fabricantes ecuador",
    "hosteleria ecuador",
    "gastronomia quito",
    "negocios ecuador",
    "muebles inox",
    "equipos gastronomicos",
    "envios ecuador",
    "ofertas quito",
    "apm inox"
]

def obtener_tags_aleatorios_antiban() -> str:
    """
    Genera hashtags aleatorios con lógica anti-bloqueo para Grupos:
    - 40% de probabilidad de NO agregar ningún hashtag.
    - 60% de probabilidad de agregar entre 2 y 4 hashtags aleatorios del pool.
    """
    probabilidad = random.random()
    if probabilidad < 0.40:
        return ""
    
    cantidad = random.randint(2, 4)
    tags_elegidos = random.sample(TAGS_POOL, cantidad)
    return " ".join(tags_elegidos)

def obtener_20_tags_ecuador() -> str:
    """
    Retorna el bloque exacto de 20 hashtags enfocados en Ecuador.
    """
    return " ".join(TAGS_ECUADOR_20)

def obtener_tags_marketplace():
    """
    Retorna las 20 palabras clave para el campo de etiquetas de producto en Marketplace.
    """
    return TAGS_MARKETPLACE_KEYWORDS

if __name__ == "__main__":
    print("20 Hashtags Ecuador:")
    print(obtener_20_tags_ecuador())
