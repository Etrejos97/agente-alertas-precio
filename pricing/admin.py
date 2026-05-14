from django.contrib import admin
from .models import ConsultaPrecio, ResultadoEncontrado, DecisionMejorPrecio


class ResultadoInline(admin.TabularInline):
    model = ResultadoEncontrado
    extra = 0
    readonly_fields = ('nombre_encontrado', 'precio_base', 'precio_efectivo', 'medio_pago', 'disponible', 'url_producto')


@admin.register(ConsultaPrecio)
class ConsultaPrecioAdmin(admin.ModelAdmin):
    list_display = ('producto', 'tienda', 'fecha_hora', 'estado')
    list_filter = ('estado', 'tienda', 'producto')
    inlines = [ResultadoInline]


@admin.register(ResultadoEncontrado)
class ResultadoEncontradoAdmin(admin.ModelAdmin):
    list_display = ('nombre_encontrado', 'precio_base', 'precio_efectivo', 'medio_pago', 'disponible')
    list_filter = ('disponible',)


@admin.register(DecisionMejorPrecio)
class DecisionMejorPrecioAdmin(admin.ModelAdmin):
    list_display = ('producto', 'resultado_ganador', 'fecha_hora', 'hubo_cambio')
    list_filter = ('hubo_cambio', 'producto')
    readonly_fields = ('fecha_hora',)