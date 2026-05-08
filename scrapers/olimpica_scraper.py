from .base_scraper import BaseScraper
import logging

logger = logging.getLogger(__name__)


class OlimpicaScraper(BaseScraper):
    """
    Scraper para la tienda Olímpica.
    URL base: https://www.olimpica.com
    """

    def buscar_producto(self, palabras_clave: list) -> list:
        # TODO: Implementar en Fase 2
        logger.info('OlimpicaScraper: buscar_producto aún no implementado')
        return []