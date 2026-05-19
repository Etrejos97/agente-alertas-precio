from django.contrib import admin
from .models import NotificacionCorreo


@admin.register(NotificacionCorreo)
class NotificacionCorreoAdmin(admin.ModelAdmin):
    list_display = ("tipo", "destinatario", "estado", "fecha_envio", "decision")
    list_filter = ("tipo", "estado")
    search_fields = ("destinatario", "mensaje_error")
    readonly_fields = ("fecha_envio",)