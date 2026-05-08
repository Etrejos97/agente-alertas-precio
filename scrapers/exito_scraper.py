from .base_scraper import BaseScraper
import logging

logger = logging.getLogger(__name__)


class ExitoScraper(BaseScraper):
    """
    Scraper para la tienda Éxito.
    URL base: https://www.exito.com
    """

    def buscar_producto(self, palabras_clave: list) -> list:
        # TODO: Implementar en Fase 2
        logger.info('ExitoScraper: buscar_producto aún no implementado')
        return []