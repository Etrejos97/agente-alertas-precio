from django.db import models
from pricing.models import DecisionMejorPrecio


class EstadoMonitoreo(models.Model):
    ESTADO_OK = "ok"
    ESTADO_SIN_CAMBIO = "sin_cambio"
    ESTADO_ERROR = "error"
    ESTADOS = [
        (ESTADO_OK, "Alerta enviada"),
        (ESTADO_SIN_CAMBIO, "Sin cambio de precio"),
        (ESTADO_ERROR, "Error en el ciclo"),
    ]

    decision = models.ForeignKey(
        DecisionMejorPrecio,
        on_delete=models.CASCADE,
        related_name="estados_monitoreo",
        null=True,
        blank=True,
        help_text="Decisión evaluada en este ciclo. Nula si hubo error antes de llegar a pricing.",
    )
    fecha_hora = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default=ESTADO_SIN_CAMBIO)
    detalle = models.TextField(
        blank=True,
        default="",
        help_text="Mensaje adicional: descripción del error o razón del sin_cambio.",
    )

    class Meta:
        verbose_name = "Estado de monitoreo"
        verbose_name_plural = "Estados de monitoreo"
        ordering = ["-fecha_hora"]

    def __str__(self):
        producto = self.decision.producto.nombre if self.decision else "Sin producto"
        return f"[{self.estado}] {producto} — {self.fecha_hora:%Y-%m-%d %H:%M}"