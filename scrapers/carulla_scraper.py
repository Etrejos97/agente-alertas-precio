from .base_scraper import BaseScraper
import logging

logger = logging.getLogger(__name__)


class CarullaScraper(BaseScraper):
    """
    Scraper para la tienda Carulla.
    URL base: https://www.carulla.com
    """

    def buscar_producto(self, palabras_clave: list) -> list:
        # TODO: Implementar en Fase 2
        logger.info('CarullaScraper: buscar_producto aún no implementado')
        return []