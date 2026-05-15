import logging
import re
import time
import urllib.parse
from typing import Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class CarullaScraper(BaseScraper):
    BASE_URL = "https://www.carulla.com"
    SEARCH_URL = "https://www.carulla.com/api/catalog_system/pub/products/search/{term}"
    DETAIL_URL = "https://www.carulla.com/api/catalog_system/pub/products/search/"
    PAGE_SIZE = 49
    REQUEST_DELAY = 0.3

    HEADERS = {
        "Accept": "application/json",
        "Accept-Language": "es-CO,es;q=0.9",
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "X-Vtex-Use-Https": "true",
        "Referer": BASE_URL + "/",
    }

    def __init__(self, url_base: str = BASE_URL):
        super().__init__(url_base=url_base)
        self.session.headers.update(self.HEADERS)
        self.session.mount(
            "https://",
            HTTPAdapter(
                max_retries=Retry(
                    total=3,
                    backoff_factor=1.0,
                    status_forcelist=[429, 500, 502, 503, 504],
                    allowed_methods=["GET"],
                )
            ),
        )

    def _limpiar_texto(self, texto: str) -> str:
        if not texto:
            return ""
        return re.sub(r"\s+", " ", texto).strip()

    def _construir_url_producto(self, product: dict) -> str:
        link = product.get("link") or ""
        if link:
            if link.startswith("http"):
                link = re.sub(r"https://secure\.carulla\.com", self.BASE_URL, link)
                return link
            return urllib.parse.urljoin(self.BASE_URL, link)

        link_text = product.get("linkText") or ""
        if link_text:
            return f"{self.BASE_URL}/{link_text}/p"

        product_id = product.get("productId") or ""
        if product_id:
            return f"{self.BASE_URL}/{product_id}/p"

        return self.BASE_URL

    def _extraer_medios_de_pago(self, installments: list) -> str:
        if not installments:
            return ""
        vistos = []
        for inst in installments:
            nombre = self._limpiar_texto(inst.get("PaymentSystemName") or "")
            if nombre and nombre not in vistos:
                vistos.append(nombre)
        return ", ".join(vistos)

    def _extraer_precios_y_disponibilidad(self, items: list) -> tuple[float, float, bool, str]:
        precio_base = 0.0
        precio_efectivo = 0.0
        disponible = False
        medio_pago = ""

        for item in items:
            sellers = item.get("sellers") or []
            for seller in sellers:
                oferta = seller.get("commertialOffer") or {}

                price = oferta.get("Price") or 0
                list_price = oferta.get("ListPrice") or 0
                qty = oferta.get("AvailableQuantity") or 0
                is_avail = oferta.get("IsAvailable")
                installments = oferta.get("Installments") or []

                if not price:
                    continue

                precio_efectivo = float(price)
                precio_base = float(list_price) if list_price >= price else float(price)
                disponible = bool(is_avail) or (isinstance(qty, (int, float)) and qty > 0)
                medio_pago = self._extraer_medios_de_pago(installments)
                return precio_base, precio_efectivo, disponible, medio_pago

        return precio_base, precio_efectivo, disponible, medio_pago

    def _buscar_productos(self, termino: str, desde: int = 0) -> list[dict]:
        url = self.SEARCH_URL.format(term=urllib.parse.quote(termino))
        params = {"_from": desde, "_to": desde + self.PAGE_SIZE}
        try:
            resp = self.session.get(url, params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            return data if isinstance(data, list) else []
        except requests.RequestException as exc:
            logger.warning("Error buscando '%s' en Carulla: %s", termino, exc)
            return []

    def _obtener_detalle(self, product_id: str) -> Optional[dict]:
        params = {"fq": f"productId:{product_id}"}
        try:
            resp = self.session.get(self.DETAIL_URL, params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            if isinstance(data, list) and data:
                return data[0]
        except requests.RequestException as exc:
            logger.warning("Error obteniendo detalle del productId %s: %s", product_id, exc)
        return None

    def buscar_producto(self, palabras_clave: list) -> list[dict]:
        if not palabras_clave:
            return []

        termino = " ".join([p["palabra"] for p in palabras_clave])
        resultados = []
        ids_procesados = set()

        for offset in range(0, 200, self.PAGE_SIZE + 1):
            lote = self._buscar_productos(termino, desde=offset)
            if not lote:
                break

            for product in lote:
                product_id = str(product.get("productId") or "")
                nombre_raw = product.get("productName") or ""
                nombre = self._limpiar_texto(nombre_raw)

                if not nombre or not product_id:
                    continue

                if product_id in ids_procesados:
                    continue
                ids_procesados.add(product_id)

                if not self.coincide_con_palabras_clave(nombre, palabras_clave):
                    continue

                time.sleep(self.REQUEST_DELAY)
                detalle = self._obtener_detalle(product_id)
                fuente = detalle or product
                items = fuente.get("items") or product.get("items") or []

                precio_base, precio_efectivo, disponible, medio_pago = (
                    self._extraer_precios_y_disponibilidad(items)
                )

                if not self.esta_disponible("disponible" if disponible else "agotado"):
                    continue

                url_producto = self._construir_url_producto(fuente)

                resultados.append(
                    {
                        "nombre_encontrado": nombre,
                        "precio_base": precio_base,
                        "precio_efectivo": precio_efectivo,
                        "medio_pago": self._limpiar_texto(medio_pago),
                        "disponible": disponible,
                        "url_producto": url_producto,
                    }
                )

            if len(lote) < self.PAGE_SIZE:
                break

        logger.info("[CarullaScraper] Búsqueda '%s' → %d productos válidos", termino, len(resultados))
        return resultados