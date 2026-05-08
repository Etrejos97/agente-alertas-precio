from django.contrib import admin
from .models import Tienda


@admin.register(Tienda)
class TiendaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'url_base', 'activa']
    list_filter = ['activa']
    search_fields = ['nombre']
    list_editable = ['activa']