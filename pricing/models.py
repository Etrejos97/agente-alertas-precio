from django.db import models
from products.models import Producto
from stores.models import Tienda


class ConsultaPrecio(models.Model):
    ESTADO_CHOICES = [
        ('exitosa', 'Exitosa'),
        ('sin_resultado', 'Sin resultado'),
        ('error', 'Error'),
    ]
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='consultas')
    tienda = models.ForeignKey(Tienda, on_delete=models.CASCADE, related_name='consultas')
    fecha_hora = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='exitosa')

    class Meta:
        verbose_name = 'Consulta de precio'
        verbose_name_plural = 'Consultas de precio'
        ordering = ['-fecha_hora']

    def __str__(self):
        return f"{self.producto} | {self.tienda} | {self.fecha_hora:%d/%m/%Y %H:%M} | {self.estado}"


class ResultadoEncontrado(models.Model):
    consulta = models.ForeignKey(ConsultaPrecio, on_delete=models.CASCADE, related_name='resultados')
    nombre_encontrado = models.CharField(max_length=255)
    precio_base = models.DecimalField(max_digits=12, decimal_places=2)
    precio_efectivo = models.DecimalField(max_digits=12, decimal_places=2)
    medio_pago = models.CharField(max_length=100, blank=True, default='')
    disponible = models.BooleanField(default=True)
    url_producto = models.URLField(max_length=500, blank=True, default='')

    class Meta:
        verbose_name = 'Resultado encontrado'
        verbose_name_plural = 'Resultados encontrados'

    def __str__(self):
        return f"{self.nombre_encontrado} — ${self.precio_efectivo}"


class DecisionMejorPrecio(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='decisiones')
    resultado_ganador = models.ForeignKey(ResultadoEncontrado, on_delete=models.CASCADE, related_name='decisiones')
    fecha_hora = models.DateTimeField(auto_now_add=True)
    justificacion = models.TextField()
    hubo_cambio = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Decisión de mejor precio'
        verbose_name_plural = 'Decisiones de mejor precio'
        ordering = ['-fecha_hora']

    def __str__(self):
        cambio = '🔔 Cambio' if self.hubo_cambio else '➖ Sin cambio'
        return f"{self.producto} | {cambio} | {self.fecha_hora:%d/%m/%Y %H:%M}"