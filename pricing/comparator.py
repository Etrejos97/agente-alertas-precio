import logging
from decimal import Decimal
from .models import ResultadoEncontrado, DecisionMejorPrecio

logger = logging.getLogger(__name__)


class Comparador:

    def comparar(self, producto, resultados: list) -> DecisionMejorPrecio | None:

        disponibles = [r for r in resultados if r.disponible]

        if not disponibles:
            logger.warning(f'No hay resultados disponibles para: {producto.nombre}')
            return None

        ganador = min(disponibles, key=lambda r: r.precio_efectivo)

        # ← NUEVO: calcular tiendas sin resultados
        from stores.models import Tienda
        tiendas_con_resultado = {r.consulta.tienda.nombre for r in disponibles}
        todas_tiendas = set(Tienda.objects.values_list("nombre", flat=True))
        tiendas_sin_resultado = todas_tiendas - tiendas_con_resultado

        justificacion = self._generar_justificacion(ganador, disponibles, tiendas_sin_resultado)
        hubo_cambio = self._evaluar_cambio(producto, ganador)

        decision = DecisionMejorPrecio.objects.create(
            producto=producto,
            resultado_ganador=ganador,
            justificacion=justificacion,
            hubo_cambio=hubo_cambio,
        )

        logger.info(
            f'Decisión tomada para {producto.nombre}: '
            f'{ganador.consulta.tienda.nombre} — ${ganador.precio_efectivo} '
            f'| Cambio: {hubo_cambio}'
        )
        return decision

    def _generar_justificacion(
        self, ganador: ResultadoEncontrado, disponibles: list, tiendas_sin_resultado: set = None
    ) -> str:

        tienda_ganadora = ganador.consulta.tienda.nombre
        precio = ganador.precio_efectivo

        if ganador.medio_pago:
            intro = (
                f'{tienda_ganadora} tiene el menor precio efectivo '
                f'(${precio} con {ganador.medio_pago}).'
            )
        else:
            intro = (
                f'{tienda_ganadora} tiene el menor precio efectivo (${precio}).'
            )

        otros = [r for r in disponibles if r != ganador]
        if not otros:
            comparativo = ''
        else:
            comparativo = ' Comparativo: ' + ', '.join(
                f"{r.consulta.tienda.nombre} ${r.precio_efectivo}"
                + (f" con {r.medio_pago}" if r.medio_pago else '')
                for r in sorted(otros, key=lambda r: r.precio_efectivo)
            ) + '.'

        # ← NUEVO: agregar tiendas sin resultado
        sin_resultado = ''
        if tiendas_sin_resultado:
            nombres = ', '.join(sorted(tiendas_sin_resultado))
            sin_resultado = f' Sin resultados en: {nombres}.'

        return intro + comparativo + sin_resultado

    def _evaluar_cambio(self, producto, ganador: ResultadoEncontrado) -> bool:

        decision_anterior = (
            DecisionMejorPrecio.objects
            .filter(producto=producto)
            .order_by('-fecha_hora')
            .first()
        )

        if not decision_anterior:
            return True

        precio_anterior = decision_anterior.resultado_ganador.precio_efectivo
        tienda_anterior = decision_anterior.resultado_ganador.consulta.tienda

        precio_actual = ganador.precio_efectivo
        tienda_actual = ganador.consulta.tienda

        precio_cambio = precio_actual != precio_anterior
        tienda_cambio = tienda_actual != tienda_anterior

        return precio_cambio or tienda_cambio