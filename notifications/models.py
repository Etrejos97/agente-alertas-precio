from django.db import models
from pricing.models import DecisionMejorPrecio


class NotificacionCorreo(models.Model):
    TIPO_ALERTA = "alerta"
    TIPO_RESUMEN = "resumen"
    TIPOS = [
        (TIPO_ALERTA, "Alerta de precio"),
        (TIPO_RESUMEN, "Resumen de estado"),
    ]

    ESTADO_ENVIADO = "enviado"
    ESTADO_ERROR = "error"
    ESTADOS = [
        (ESTADO_ENVIADO, "Enviado"),
        (ESTADO_ERROR, "Error"),
    ]

    decision = models.ForeignKey(
        DecisionMejorPrecio,
        on_delete=models.CASCADE,
        related_name="notificaciones",
        null=True,
        blank=True,
        help_text="Decisión que originó este correo. Nulo si es resumen general.",
    )
    destinatario = models.EmailField(help_text="Correo del destinatario.")
    fecha_envio = models.DateTimeField(auto_now_add=True)
    tipo = models.CharField(max_length=10, choices=TIPOS, default=TIPO_ALERTA)
    estado = models.CharField(max_length=10, choices=ESTADOS, default=ESTADO_ENVIADO)
    mensaje_error = models.TextField(blank=True, default="")

    class Meta:
        verbose_name = "Notificación de correo"
        verbose_name_plural = "Notificaciones de correo"
        ordering = ["-fecha_envio"]

    def __str__(self):
        return f"[{self.tipo}] → {self.destinatario} ({self.estado}) {self.fecha_envio:%Y-%m-%d %H:%M}"