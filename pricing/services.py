import logging
from products.models import Producto
from stores.models import Tienda
from .models import ConsultaPrecio, ResultadoEncontrado
from .comparator import Comparador

logger = logging.getLogger(__name__)


def registrar_resultado(consulta: ConsultaPrecio, resultado_raw: dict) -> ResultadoEncontrado:
    
    return ResultadoEncontrado.objects.create(
        consulta=consulta,
        nombre_encontrado=resultado_raw.get('nombre_encontrado', ''),
        precio_base=resultado_raw.get('precio_base', 0),
        precio_efectivo=resultado_raw.get('precio_efectivo', 0),
        medio_pago=resultado_raw.get('medio_pago', ''),
        disponible=resultado_raw.get('disponible', True),
        url_producto=resultado_raw.get('url_producto', ''),
    )


def ejecutar_ciclo_producto(producto: Producto, tienda: Tienda, scraper, resultados_ciclo: list):
    
    palabras = list(
        producto.palabras_clave.values('palabra', 'es_obligatoria')
    )

    consulta = ConsultaPrecio.objects.create(
        producto=producto,
        tienda=tienda,
        estado='exitosa',
    )

    try:
        resultados_raw = scraper.buscar_producto(palabras)

        if not resultados_raw:
            consulta.estado = 'sin_resultado'
            consulta.save()
            logger.info(f'Sin resultado: {producto.nombre} en {tienda.nombre}')
            return

        for dato in resultados_raw:
            resultado = registrar_resultado(consulta, dato)
            if resultado.disponible:
                resultados_ciclo.append(resultado)

    except Exception as e:
        consulta.estado = 'error'
        consulta.save()
        logger.error(f'Error consultando {producto.nombre} en {tienda.nombre}: {e}')


def ejecutar_ciclo_completo():
    
    from scrapers.exito_scraper import ExitoScraper
    from scrapers.olimpica_scraper import OlimpicaScraper
    from scrapers.carulla_scraper import CarullaScraper
    from stores.models import Tienda

    SCRAPERS = {
        'Éxito': ExitoScraper,
        'Olímpica': OlimpicaScraper,
        'Carulla': CarullaScraper,
    }

    comparador = Comparador()
    productos = Producto.objects.filter(activo=True)
    tiendas = Tienda.objects.filter(activa=True)

    for producto in productos:
        resultados_ciclo = []

        for tienda in tiendas:
            ClaseScraper = SCRAPERS.get(tienda.nombre)
            if not ClaseScraper:
                logger.warning(f'No hay scraper registrado para: {tienda.nombre}')
                continue

            scraper = ClaseScraper(tienda.url_base)
            ejecutar_ciclo_producto(producto, tienda, scraper, resultados_ciclo)

        if resultados_ciclo:
            comparador.comparar(producto, resultados_ciclo)
        else:
            logger.warning(f'Ciclo sin resultados válidos para: {producto.nombre}')