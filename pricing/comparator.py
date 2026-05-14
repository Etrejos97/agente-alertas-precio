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

        # RN05 — El ganador es el de menor precio efectivo
        ganador = min(disponibles, key=lambda r: r.precio_efectivo)

        justificacion = self._generar_justificacion(ganador, disponibles)
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
        self, ganador: ResultadoEncontrado, disponibles: list
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
            return intro

        comparativo = ' Comparativo: ' + ', '.join(
            f"{r.consulta.tienda.nombre} ${r.precio_efectivo}"
            + (f" con {r.medio_pago}" if r.medio_pago else '')
            for r in sorted(otros, key=lambda r: r.precio_efectivo)
        ) + '.'

        return intro + comparativo

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