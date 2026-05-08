from django.db import models


class Tienda(models.Model):
    nombre = models.CharField(max_length=100)
    url_base = models.URLField()
    activa = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Tienda'
        verbose_name_plural = 'Tiendas'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre