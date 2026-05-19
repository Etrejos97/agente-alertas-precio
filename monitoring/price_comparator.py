import logging
from pricing.models import ResultadoEncontrado, DecisionMejorPrecio

logger = logging.getLogger(__name__)


def evaluar_producto(producto) -> dict:
    try:
        nueva_decision = (
            DecisionMejorPrecio.objects.filter(producto=producto)
            .order_by("-fecha_hora")
            .first()
        )

        if nueva_decision is None:
            return {
                "cambio": False,
                "decision": None,
                "error": "No hay decisiones registradas aún para este producto.",
            }

        return {
            "cambio": nueva_decision.hubo_cambio,
            "decision": nueva_decision,
            "error": None,
        }

    except Exception as exc:
        logger.exception("Error al evaluar producto '%s': %s", producto.nombre, exc)
        return {"cambio": False, "decision": None, "error": str(exc)}