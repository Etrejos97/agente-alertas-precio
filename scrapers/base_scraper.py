import requests
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
        """
        nombre_lower = nombre_encontrado.lower()
        obligatorias = [
            p['palabra'].lower()
            for p in palabras_clave
            if p['es_obligatoria']
        ]
        return all(palabra in nombre_lower for palabra in obligatorias)

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