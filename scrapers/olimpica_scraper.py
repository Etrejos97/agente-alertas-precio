import logging
import time
import requests
from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)

BASE_URL = "https://www.olimpica.com"
IS_SEARCH_URL = BASE_URL + "/api/io/_v/api/intelligent-search/product_search/supermercado"

DEFAULT_HEADERS = {
    "Accept": "application/json",
    "Accept-Language": "es-CO,es;q=0.9",
    "Referer": BASE_URL + "/",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "x-vtex-locale": "es-CO",
    "x-vtex-currency": "COP",
}

PAGE_SIZE = 20
MAX_PAGES = 5
REQUEST_DELAY = 0.8


class OlimpicaScraper(BaseScraper):
    def __init__(self, url_base: str = BASE_URL):
        super().__init__(url_base=url_base)
        self.session.headers.update(DEFAULT_HEADERS)

    def buscar_producto(self, palabras_clave: list) -> list:
        palabras = [p["palabra"] for p in palabras_clave]
        query = " ".join(palabras)
        resultados = []

        for page in range(1, MAX_PAGES + 1):
            params = {
                "query": query,
                "count": PAGE_SIZE,
                "page": page,
                "locale": "es-CO",
                "hideUnavailableItems": "false",
                "sort": "",
                "operator": "and",
                "fuzzy": "0",
            }

            try:
                response = self.session.get(IS_SEARCH_URL, params=params, timeout=15)
                response.raise_for_status()
                data = response.json()
            except requests.RequestException as exc:
                logger.error("[OlimpicaScraper] Error en petición página %d: %s", page, exc)
                break
            except ValueError:
                logger.error("[OlimpicaScraper] Respuesta no es JSON en página %d", page)
                break

            productos = data.get("products", [])
            if not productos:
                break

            for producto in productos:
                resultado = self._parsear_producto(producto)
                if resultado is None:
                    continue

                if not self.coincide_con_palabras_clave(resultado["nombre_encontrado"], palabras_clave):
                    continue

                resultados.append(resultado)

            if len(productos) < PAGE_SIZE:
                break

            time.sleep(REQUEST_DELAY)

        logger.info("[OlimpicaScraper] Búsqueda '%s' → %d productos válidos", query, len(resultados))
        return resultados

    def _parsear_producto(self, producto: dict) -> dict | None:
        try:
            nombre = producto.get("productName", "").strip()
            link_relativo = producto.get("link", "")
            url_producto = BASE_URL + link_relativo if link_relativo else ""

            items = producto.get("items", [])
            if not items:
                return None

            sellers = items[0].get("sellers", [])
            if not sellers:
                return None

            oferta = sellers[0].get("commertialOffer", {})
            precio_efectivo = float(oferta.get("Price", 0) or 0)
            precio_base = float(oferta.get("ListPrice", precio_efectivo) or precio_efectivo)
            medio_pago = self._extraer_medio_pago(oferta)

            if not nombre or not url_producto:
                return None

            return {
                "nombre_encontrado": nombre,
                "precio_base": precio_base,
                "precio_efectivo": precio_efectivo,
                "medio_pago": medio_pago,
                "disponible": True,
                "url_producto": url_producto,
            }

        except (KeyError, IndexError, TypeError, ValueError) as exc:
            logger.warning("[OlimpicaScraper] Error parseando producto '%s': %s", producto.get("productName", "desconocido"), exc)
            return None

    @staticmethod
    def _extraer_medio_pago(oferta: dict) -> str:
        teasers = oferta.get("teasers", [])
        if not teasers:
            return "Cualquier medio"
        nombres_teaser = []
        for teaser in teasers:
            nombre = teaser.get("name", "").strip()
            if nombre:
                nombres_teaser.append(nombre)
        return " | ".join(nombres_teaser) if nombres_teaser else "Cualquier medio"