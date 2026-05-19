import logging
from celery import shared_task
from decouple import config

from products.models import Producto
from scrapers.runner import ejecutar_scraping_producto
from monitoring.price_comparator import evaluar_producto
from monitoring.models import EstadoMonitoreo
from notifications.email_builder import construir_correo_alerta
from notifications.brevo_sender import enviar_correo
from notifications.models import NotificacionCorreo

logger = logging.getLogger(__name__)


@shared_task(name="monitoring.tasks.ciclo_monitoreo")
def ciclo_monitoreo():
    productos = Producto.objects.filter(activo=True)

    if not productos.exists():
        logger.warning("ciclo_monitoreo: no hay productos activos.")
        return

    destinatario = config("ALERT_RECIPIENT_EMAIL")

    for producto in productos:
        logger.info("Procesando producto: %s", producto.nombre)

        # Paso 1 — Scraping
        try:
            ejecutar_scraping_producto(producto)
        except Exception as exc:
            logger.error("Error en scraping de '%s': %s", producto.nombre, exc)
            EstadoMonitoreo.objects.create(
                decision=None,
                estado=EstadoMonitoreo.ESTADO_ERROR,
                detalle=f"Error en scraping: {exc}",
            )
            continue

        # Paso 2 — Comparación
        resultado = evaluar_producto(producto)

        if resultado["error"]:
            EstadoMonitoreo.objects.create(
                decision=None,
                estado=EstadoMonitoreo.ESTADO_ERROR,
                detalle=resultado["error"],
            )
            continue

        decision = resultado["decision"]

        # Paso 3 — Notificación si hubo cambio
        if resultado["cambio"]:
            correo = construir_correo_alerta(decision)
            envio = enviar_correo(destinatario, correo["asunto"], correo["html"])

            NotificacionCorreo.objects.create(
                decision=decision,
                destinatario=destinatario,
                tipo=NotificacionCorreo.TIPO_ALERTA,
                estado=(
                    NotificacionCorreo.ESTADO_ENVIADO
                    if envio["exito"]
                    else NotificacionCorreo.ESTADO_ERROR
                ),
                mensaje_error=envio["error"] or "",
            )

            EstadoMonitoreo.objects.create(
                decision=decision,
                estado=EstadoMonitoreo.ESTADO_OK,
                detalle="Alerta enviada correctamente." if envio["exito"] else f"Correo falló: {envio['error']}",
            )
        else:
            EstadoMonitoreo.objects.create(
                decision=decision,
                estado=EstadoMonitoreo.ESTADO_SIN_CAMBIO,
                detalle="Precio sin cambios respecto al ciclo anterior.",
            )

    logger.info("ciclo_monitoreo finalizado para %d productos.", productos.count())