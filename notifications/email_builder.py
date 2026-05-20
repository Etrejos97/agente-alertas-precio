from datetime import datetime, timezone, timedelta

ZONA_COLOMBIA = timezone(timedelta(hours=-5))


def _resaltar_tiendas(justificacion: str) -> str:
    """Envuelve en <strong> los nombres de tiendas conocidas."""
    for tienda in ["Olímpica", "Éxito", "Carulla"]:
        justificacion = justificacion.replace(tienda, f"<strong>{tienda}</strong>")
    return justificacion


def construir_correo_alerta(decision) -> dict:
    ganador = decision.resultado_ganador
    producto = decision.producto
    tienda = ganador.consulta.tienda
    fecha = decision.fecha_hora.astimezone(ZONA_COLOMBIA).strftime("%d/%m/%Y a las %I:%M %p")

    precio_base = f"${ganador.precio_base:,.0f}".replace(",", ".")
    precio_efectivo = f"${ganador.precio_efectivo:,.0f}".replace(",", ".")
    medio = ganador.medio_pago or "No especificado"

    asunto = (
        f"[Alerta de Precio] {producto.nombre} — "
        f"Mejor precio: {precio_efectivo} en {tienda.nombre}"
    )

    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #222; max-width: 600px; margin: auto;">
        <h2 style="color: #1a7a2e;">🛒 Alerta de Precio — {producto.nombre}</h2>
        <table style="width:100%; border-collapse: collapse;">
            <tr style="background:#f0f7f0;">
                <td style="padding:8px; font-weight:bold;">Tienda ganadora</td>
                <td style="padding:8px;">{tienda.nombre}</td>
            </tr>
            <tr>
                <td style="padding:8px; font-weight:bold;">Precio efectivo</td>
                <td style="padding:8px; color:#1a7a2e; font-size:1.2em;">{precio_efectivo}</td>
            </tr>
            <tr style="background:#f0f7f0;">
                <td style="padding:8px; font-weight:bold;">Precio base</td>
                <td style="padding:8px;">{precio_base}</td>
            </tr>
            <tr>
                <td style="padding:8px; font-weight:bold;">Medio de pago</td>
                <td style="padding:8px;">{medio}</td>
            </tr>
            <tr style="background:#f0f7f0;">
                <td style="padding:8px; font-weight:bold;">Nombre en tienda</td>
                <td style="padding:8px;">{ganador.nombre_encontrado}</td>
            </tr>
            <tr>
                <td style="padding:8px; font-weight:bold;">Enlace</td>
                <td style="padding:8px;">
                    <a href="{ganador.url_producto}" style="color:#1a7a2e;">Ver en {tienda.nombre}</a>
                </td>
            </tr>
        </table>
        <h3 style="margin-top:24px;">📊 Justificación</h3>
        <p style="background:#f9f9f9; padding:12px; border-left: 4px solid #1a7a2e;">
            {_resaltar_tiendas(decision.justificacion)}
        </p>
        <p style="color:#999; font-size:0.85em; margin-top:32px;">
            Consultado el {fecha}<br>
            Generado automáticamente por el Agente de Alertas de Precio — TDEA.
        </p>
    </body>
    </html>
    """
    return {"asunto": asunto, "html": html}


def construir_correo_resumen(decisiones: list) -> dict:
    ahora_colombia = datetime.now(ZONA_COLOMBIA)
    fecha = ahora_colombia.strftime("%d/%m/%Y a las %I:%M %p")
    asunto = f"[Resumen de Precios] Estado actual — {ahora_colombia.strftime('%d/%m/%Y')}"

    filas = ""
    for decision in decisiones:
        ganador = decision.resultado_ganador
        tienda = ganador.consulta.tienda
        precio = f"${ganador.precio_efectivo:,.0f}".replace(",", ".")
        medio = ganador.medio_pago or "—"
        filas += f"""
        <tr>
            <td style="padding:8px; border-bottom:1px solid #eee;">{decision.producto.nombre}</td>
            <td style="padding:8px; border-bottom:1px solid #eee;">{tienda.nombre}</td>
            <td style="padding:8px; border-bottom:1px solid #eee; color:#1a7a2e;">{precio}</td>
            <td style="padding:8px; border-bottom:1px solid #eee;">{medio}</td>
            <td style="padding:8px; border-bottom:1px solid #eee;">
                <a href="{ganador.url_producto}" style="color:#1a7a2e;">Ver</a>
            </td>
        </tr>
        """

    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #222; max-width: 700px; margin: auto;">
        <h2 style="color: #1a7a2e;">📋 Resumen de Precios Actuales</h2>
        <p>Estado del monitoreo al {fecha}</p>
        <table style="width:100%; border-collapse: collapse; margin-top:16px;">
            <thead>
                <tr style="background:#1a7a2e; color:white;">
                    <th style="padding:10px; text-align:left;">Producto</th>
                    <th style="padding:10px; text-align:left;">Tienda</th>
                    <th style="padding:10px; text-align:left;">Precio</th>
                    <th style="padding:10px; text-align:left;">Medio de pago</th>
                    <th style="padding:10px; text-align:left;">Enlace</th>
                </tr>
            </thead>
            <tbody>{filas}</tbody>
        </table>
        <p style="color:#999; font-size:0.85em; margin-top:32px;">
            Generado el {fecha} — Agente de Alertas de Precio, MVP académico TDEA.
        </p>
    </body>
    </html>
    """
    return {"asunto": asunto, "html": html}