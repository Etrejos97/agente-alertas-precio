from django.contrib import admin
from .models import EstadoMonitoreo


@admin.register(EstadoMonitoreo)
class EstadoMonitoreoAdmin(admin.ModelAdmin):
    list_display = ("estado", "fecha_hora", "get_producto", "detalle_corto")
    list_filter = ("estado",)
    search_fields = ("detalle", "decision__producto__nombre")
    readonly_fields = ("fecha_hora",)

    @admin.display(description="Producto")
    def get_producto(self, obj):
        if obj.decision:
            return obj.decision.producto.nombre
        return "—"

    @admin.display(description="Detalle")
    def detalle_corto(self, obj):
        return obj.detalle[:80] + "..." if len(obj.detalle) > 80 else obj.detalle