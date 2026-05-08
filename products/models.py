from django.db import models


class Producto(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class PalabraClave(models.Model):
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name='palabras_clave'
    )
    palabra = models.CharField(max_length=100)
    es_obligatoria = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Palabra clave'
        verbose_name_plural = 'Palabras clave'

    def __str__(self):
        tipo = 'Obligatoria' if self.es_obligatoria else 'Opcional'
        return f'{self.palabra} ({tipo}) — {self.producto.nombre}'