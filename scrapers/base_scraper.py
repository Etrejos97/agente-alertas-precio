import re
import requests
import unicodedata
from abc import ABC, abstractmethod
import logging


logger = logging.getLogger(__name__)


HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/120.0.0.0 Safari/537.36'
    )
}


TIMEOUT = 10  # segundos


class BaseScraper(ABC):
    """
    Clase base abstracta para todos los scrapers del sistema.
    Cada tienda debe heredar de esta clase e implementar sus métodos.
    """

    def __init__(self, url_base: str):
        self.url_base = url_base
        self.session = requests.Session()
        self.session.headers.update(HEADERS)

    @abstractmethod
    def buscar_producto(self, palabras_clave: list) -> list:
        """
        Busca un producto en la tienda usando las palabras clave.

        Args:
            palabras_clave: lista de dicts con 'palabra' y 'es_obligatoria'

        Returns:
            Lista de dicts con los resultados encontrados. Cada dict tiene:
            {
                'nombre_encontrado': str,
                'precio_base': float,
                'precio_efectivo': float,
                'medio_pago': str o None,
                'disponible': bool,
                'url_producto': str
            }
        """
        pass

    @staticmethod
    def _normalizar(texto: str) -> str:
        """Convierte a minúsculas, elimina tildes y normaliza espacios."""
        texto = ''.join(
            c for c in unicodedata.normalize('NFD', texto.lower())
            if unicodedata.category(c) != 'Mn'
        )
        texto = re.sub(r'\s+', ' ', texto).strip()
        return texto

    @staticmethod
    def _normalizar_unidades(texto: str) -> str:
        """
        Normaliza formatos de unidades para comparar mejor:
        900ml -> 900 ml, 1000gr -> 1000 gr, 1l -> 1 l, etc.
        """
        texto = BaseScraper._normalizar(texto)

        texto = re.sub(r'(\d)(ml|gr|g|kg|l|lt)\b', r'\1 \2', texto)
        texto = re.sub(r'(\d)\s+(ml|gr|g|kg|l|lt)\b', r'\1 \2', texto)

        texto = texto.replace("lts", "lt")
        texto = texto.replace("litros", "litro")

        texto = re.sub(r'\s+', ' ', texto).strip()
        return texto

    @staticmethod
    def _generar_variantes_equivalentes(texto: str) -> set[str]:
        """
        Genera variantes equivalentes de presentación sin romper
        la comparación literal ya existente.

        Ejemplos:
        - 900 ml -> {'900 ml'}
        - 1000 ml -> {'1000 ml', '1 l', '1 lt'}
        - 1 l -> {'1 l', '1 lt', '1000 ml'}
        - 1000 g -> {'1000 g', '1 kg'}
        - 1 kg -> {'1 kg', '1000 g'}
        """
        base = BaseScraper._normalizar_unidades(texto)
        variantes = {base}

        equivalencias = [
            (r'\b1000 ml\b', ['1 l', '1 lt']),
            (r'\b1 l\b', ['1000 ml', '1 lt']),
            (r'\b1 lt\b', ['1000 ml', '1 l']),
            (r'\b1000 g\b', ['1 kg']),
            (r'\b1 kg\b', ['1000 g']),
        ]

        pendientes = {base}
        procesadas = set()

        while pendientes:
            actual = pendientes.pop()
            if actual in procesadas:
                continue
            procesadas.add(actual)

            for patron, reemplazos in equivalencias:
                if re.search(patron, actual):
                    for reemplazo in reemplazos:
                        nuevo = re.sub(patron, reemplazo, actual)
                        nuevo = BaseScraper._normalizar_unidades(nuevo)
                        if nuevo not in variantes:
                            variantes.add(nuevo)
                            pendientes.add(nuevo)

        return variantes

    def esta_disponible(self, texto_pagina: str) -> bool:
        """
        Verifica si un producto está disponible revisando
        palabras clave de agotado en el texto de la página.
        """
        palabras_agotado = [
            'agotado', 'sin stock', 'no disponible',
            'out of stock', 'sold out', 'no hay existencias'
        ]
        texto_lower = texto_pagina.lower()
        return not any(p in texto_lower for p in palabras_agotado)

    def coincide_con_palabras_clave(
        self, nombre_encontrado: str, palabras_clave: list
    ) -> bool:
        """
        Verifica si el nombre encontrado en la tienda coincide
        con las palabras clave del producto.

        Regla RN01: todas las palabras obligatorias deben aparecer.
        Normaliza tildes, espacios y formatos de unidades, y además
        acepta equivalencias controladas como 1000 ml = 1 l,
        1000 g = 1 kg.
        """
        nombre_norm = self._normalizar_unidades(nombre_encontrado)

        obligatorias = [
            p['palabra']
            for p in palabras_clave
            if p['es_obligatoria']
        ]

        for palabra in obligatorias:
            variantes = self._generar_variantes_equivalentes(palabra)
            if not any(variante in nombre_norm for variante in variantes):
                return False

        return True

    def get_pagina(self, url: str) -> requests.Response | None:
        """
        Realiza una petición GET a la URL indicada.
        Retorna el Response o None si falla.
        """
        try:
            response = self.session.get(url, timeout=TIMEOUT)
            response.raise_for_status()
            return response
        except requests.exceptions.Timeout:
            logger.error(f'Timeout al consultar: {url}')
            return None
        except requests.exceptions.ConnectionError:
            logger.error(f'Error de conexión al consultar: {url}')
            return None
        except requests.exceptions.HTTPError as e:
            logger.error(f'Error HTTP {e.response.status_code} al consultar: {url}')
            return None
        except Exception as e:
            logger.error(f'Error inesperado al consultar {url}: {e}')
            return None