from django.core.management.base import BaseCommand
from decouple import config
from products.models import Producto
from pricing.models import DecisionMejorPrecio
from notifications.brevo_sender import enviar_correo
from notifications.email_builder import construir_correo_resumen


class Command(BaseCommand):
    help = 'Envía un correo resumen con el estado actual de todos los precios'

    def handle(self, *args, **kwargs):
        productos = Producto.objects.filter(activo=True)
        decisiones = []

        for producto in productos:
            decision = (
                DecisionMejorPrecio.objects
                .filter(producto=producto)
                .order_by('-fecha_hora')
                .first()
            )
            if decision:
                decisiones.append(decision)

        if not decisiones:
            self.stdout.write(self.style.WARNING('No hay decisiones registradas aún.'))
            return

        correo = construir_correo_resumen(decisiones)
        destinatario = config('ALERT_RECIPIENT_EMAIL')
        resultado = enviar_correo(destinatario, correo['asunto'], correo['html'])

        if resultado['exito']:
            self.stdout.write(self.style.SUCCESS('Correo resumen enviado correctamente.'))
        else:
            self.stdout.write(self.style.ERROR(f"Error al enviar: {resultado['error']}"))