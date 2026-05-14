import re
import time
import logging
from urllib.parse import urlencode, quote_plus
from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class ExitoScraper(BaseScraper):

    BASE_URL = "https://www.exito.com"

    def __init__(self):
        super().__init__(url_base=self.BASE_URL)

    def _build_search_url(self, palabras_clave: list) -> str:
        palabras = [p['palabra'] for p in palabras_clave]
        query = " ".join(palabras)
        params = {"q": query, "sort": "score_desc", "fuzzy": "0"}
        return f"{self.BASE_URL}/s?{urlencode(params, quote_via=quote_plus)}"

    @staticmethod
    def _limpiar_precio(texto: str) -> float:
        texto = texto.strip().replace("$", "").replace(" ", "")
        texto = texto.replace(".", "")
        texto = texto.replace(",", ".")
        try:
            return float(texto)
        except ValueError:
            return 0.0

    def _get_html_con_playwright(self, url: str) -> str:
        try:
            from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
        except ImportError:
            logger.error('Playwright no instalado. Ejecuta: pip install playwright && playwright install chromium')
            return ""

        html = ""
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
                locale="es-CO",
            )
            page = context.new_page()
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=30_000)
                page.wait_for_selector("h3", timeout=15_000)
                time.sleep(2)
                html = page.content()
            except PWTimeout:
                html = page.content()
            except Exception as e:
                logger.error(f'Error Playwright al consultar {url}: {e}')
            finally:
                browser.close()

        return html

    def _parsear_productos(self, html: str) -> list:
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html, "html.parser")
        productos = []

        links_nombre = [
            a for a in soup.find_all("a", href=re.compile(r"/.+/p$"))
            if a.find("h3")
        ]

        for link in links_nombre:
            try:
                dato = self._extraer_dato_producto(link)
                if dato:
                    productos.append(dato)
            except Exception as e:
                logger.warning(f'Error extrayendo producto: {e}')
                continue

        return productos

    def _extraer_dato_producto(self, link_nombre) -> dict | None:
        h3 = link_nombre.find("h3")
        if not h3:
            return None
        nombre = h3.get_text(strip=True)
        if not nombre:
            return None

        href = link_nombre.get("href", "")
        if not href:
            return None
        url_producto = href if href.startswith("http") else f"{self.BASE_URL}{href}"

        textos = []
        tiene_agregar = False
        tiene_modal = False
        nodo = link_nombre.next_sibling
        limite = 40

        while nodo and limite > 0:
            limite -= 1
            if hasattr(nodo, 'name') and nodo.name:
                if nodo.name == "a" and nodo.find("h3"):
                    break
                if nodo.name == "button":
                    texto_btn = nodo.get_text(strip=True)
                    if "lista de deseos" in texto_btn.lower():
                        break
                    if texto_btn.lower() == "agregar":
                        tiene_agregar = True
                        textos.append("__AGREGAR__")
                        nodo = nodo.next_sibling
                        continue
                    if texto_btn == "Modal opener":
                        tiene_modal = True
                        textos.append("__MODAL__")
                        nodo = nodo.next_sibling
                        continue
                t = nodo.get_text(strip=True)
                if t:
                    textos.append(t)
            elif isinstance(nodo, str):
                t = nodo.strip()
                if t:
                    textos.append(t)
            nodo = nodo.next_sibling

        RE_NUMERO = re.compile(r'^\d{1,3}(\.\d{3})*$')
        numeros = [t for t in textos if RE_NUMERO.match(t)]

        if tiene_modal and len(numeros) >= 2:
            precio_base = self._limpiar_precio(numeros[0])
            precio_efectivo = self._limpiar_precio(numeros[1])
        elif numeros:
            precio_base = self._limpiar_precio(numeros[0])
            precio_efectivo = precio_base
        else:
            precio_base = 0.0
            precio_efectivo = 0.0

        texto_bloque = " ".join(textos)
        disponible = tiene_agregar and self.esta_disponible(texto_bloque)

        medio_pago = ""
        for keyword in ["tarjeta éxito", "tarjeta exito", "nequi", "daviplata", "pse"]:
            if keyword in texto_bloque.lower():
                medio_pago = keyword.title()
                break

        return {
            'nombre_encontrado': nombre,
            'precio_base':       precio_base,
            'precio_efectivo':   precio_efectivo,
            'medio_pago':        medio_pago,
            'disponible':        disponible,
            'url_producto':      url_producto,
        }

    def buscar_producto(self, palabras_clave: list) -> list:
        url_busqueda = self._build_search_url(palabras_clave)
        logger.info(f'ExitoScraper buscando: {url_busqueda}')

        html = self._get_html_con_playwright(url_busqueda)
        if not html:
            return []

        todos = self._parsear_productos(html)

        resultados = [
            p for p in todos
            if self.coincide_con_palabras_clave(p['nombre_encontrado'], palabras_clave)
            and p['disponible']
        ]

        logger.info(f'ExitoScraper: {len(resultados)} resultados válidos')
        return resultados