from django.contrib import admin
from .models import Producto, PalabraClave


class PalabraClaveInline(admin.TabularInline):
    model = PalabraClave
    extra = 2
    fields = ['palabra', 'es_obligatoria']


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'activo', 'fecha_creacion']
    list_filter = ['activo']
    search_fields = ['nombre']
    list_editable = ['activo']
    inlines = [PalabraClaveInline]


@admin.register(PalabraClave)
class PalabraClaveAdmin(admin.ModelAdmin):
    list_display = ['palabra', 'producto', 'es_obligatoria']
    list_filter = ['es_obligatoria', 'producto']
    search_fields = ['palabra']