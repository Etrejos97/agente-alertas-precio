"""
Orquesta la ejecución de todos los scrapers para un producto
y guarda los ResultadoEncontrado en la base de datos.
"""

import logging
import unicodedata
from scrapers import ExitoScraper, OlimpicaScraper, CarullaScraper
from pricing.models import ConsultaPrecio, ResultadoEncontrado


def normalizar(texto: str) -> str:
    """Convierte a minúsculas y elimina tildes para comparación."""
    return ''.join(
        c for c in unicodedata.normalize('NFD', texto.lower())
        if unicodedata.category(c) != 'Mn'
    )


logger = logging.getLogger(__name__)


SCRAPERS_DISPONIBLES = {
    "exito": ExitoScraper,
    "olimpica": OlimpicaScraper,
    "carulla": CarullaScraper,
}


def ejecutar_scraping_producto(producto) -> None:
    """
    Ejecuta el scraping en todas las tiendas configuradas para el producto
    y guarda los resultados en ResultadoEncontrado.
    Cada scraper filtra internamente por palabras clave, incluyendo
    normalización de unidades (ej: 1L ↔ 1000 ml), por lo que el runner
    no re-filtra para evitar descartar resultados válidos.
    """
    palabras_clave = list(
        producto.palabras_clave.values("palabra", "es_obligatoria")
    )

    if not palabras_clave:
        logger.warning("El producto '%s' no tiene palabras clave definidas.", producto.nombre)
        return

    from stores.models import Tienda
    tiendas = Tienda.objects.all()

    for tienda in tiendas:
        nombre_tienda = normalizar(tienda.nombre)
        scraper_clase = SCRAPERS_DISPONIBLES.get(nombre_tienda)

        if scraper_clase is None:
            logger.warning("No hay scraper registrado para '%s'.", nombre_tienda)
            continue

        consulta = ConsultaPrecio.objects.create(
            producto=producto,
            tienda=tienda,
            estado="exitosa",
        )

        try:
            scraper = scraper_clase()
            resultados = scraper.buscar_producto(palabras_clave)

            # Deduplicar: quedarse con el de menor precio_efectivo por nombre
            vistos = {}
            for r in resultados:
                nombre = r["nombre_encontrado"].lower().strip()
                if nombre not in vistos or r["precio_efectivo"] < vistos[nombre]["precio_efectivo"]:
                    vistos[nombre] = r
            resultados = list(vistos.values())

            for r in resultados:
                ResultadoEncontrado.objects.create(
                    consulta=consulta,
                    nombre_encontrado=r["nombre_encontrado"],
                    precio_base=r["precio_base"],
                    precio_efectivo=r["precio_efectivo"],
                    medio_pago=r.get("medio_pago", ""),
                    disponible=r.get("disponible", True),
                    url_producto=r["url_producto"],
                )

            logger.info(
                "%d resultados para '%s' en '%s'.",
                len(resultados), producto.nombre, tienda.nombre,
            )

        except Exception as exc:
            consulta.estado = "error"
            consulta.save()
            logger.error("Error en scraper '%s' para '%s': %s", nombre_tienda, producto.nombre, exc)