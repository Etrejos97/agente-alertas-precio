# Guía de Demostración — Agente de Alertas de Precio
**MVP Académico | Tecnológico de Antioquia | Redes de Datos | Mayo 2026**

---

## Antes de empezar

Verificar que estén corriendo:

| Servicio | Puerto | Cómo verificar |
|---|---|---|
| PostgreSQL | 5433 | Servicios de Windows |
| Memurai (Redis) | 6379 | Ícono en bandeja del sistema |

---

## Paso 1 — Levantar el proyecto

Desde la raíz del proyecto ejecutar:
```
start_all.bat
```

Se abren 3 ventanas automáticamente:

| Ventana | Proceso | Señal de OK |
|---|---|---|
| Terminal 1 | Django | `Starting development server at http://127.0.0.1:8000/` |
| Terminal 2 | Celery Worker | `celery@EDISON ready.` |
| Terminal 3 | Celery Beat | `beat: Starting...` |

---

## Paso 2 — Panel de administración

Abrir en el navegador: `http://127.0.0.1:8000/admin`

Secciones a mostrar:
- **Products → Productos**: los 3 productos con sus palabras clave
- **Stores → Tiendas**: Éxito, Olímpica y Carulla activas
- **Pricing → Consultas de precio**: historial de cada consulta por tienda y fecha
- **Pricing → Resultados encontrados**: precios reales extraídos de cada página
- **Pricing → Decisiones de mejor precio**: comparación con justificación automática
- **Notifications → Notificaciones correo**: cada correo enviado con fecha y estado

---

## Paso 3 — Ver que el agente ha estado funcionando

Para demostrar que el agente corrió de forma autónoma:

- **Pricing → Consultas de precio**: cada fila tiene fecha y hora exacta. Varias filas con horas distintas confirman que el ciclo horario corrió solo.
- **Pricing → Decisiones de mejor precio**: muestra qué tienda ganó, a qué precio y si hubo cambio en cada ciclo.
- **Notifications → Notificaciones correo**: cada correo enviado queda registrado con tipo (`alerta` o `resumen`).

> Este historial es la evidencia de que el agente trabajó de manera autónoma.

---

## Paso 4 — Demostrar el ciclo completo en vivo

Si el profesor quiere ver el agente consultar, comparar y decidir en tiempo real, ejecutar en terminal con venv activo:

```bash
python manage.py shell
```

Dentro del shell:
```python
from monitoring.tasks import ciclo_monitoreo
ciclo_monitoreo.delay()
```

Salir del shell:
```python
exit()
```

**Qué se ve en la ventana del worker:**
1. `Task monitoring.tasks.ciclo_monitoreo [...] received` — la tarea entró a la cola
2. `Procesando producto: [nombre]` — el agente inicia con cada producto
3. `[CarullaScraper] Búsqueda → N productos válidos` — scraping ejecutado
4. `Decisión tomada para [producto]: [Tienda] — $[precio] | Cambio: True/False`
5. `Task ... succeeded in Xs` — ciclo terminado exitosamente

> ⚠️ **Importante**: el correo de alerta **solo se envía si el precio o la tienda ganadora cambió** respecto al ciclo anterior. Si los precios no cambiaron, el agente trabaja correctamente pero no envía correo automático. Esto es el comportamiento esperado según las reglas de negocio.

---

## Paso 5 — Forzar correo en vivo si no hubo cambios

### Opción A — Correo resumen (más rápida, recomendada)

Envía inmediatamente un correo con el estado actual de todos los productos sin importar si hubo cambios:

```bash
python manage.py enviar_resumen
```

El correo llega en segundos con tabla comparativa de los 3 productos, tienda ganadora, precio y medio de pago.

### Opción B — Forzar correo de alerta borrando el historial

Si se necesita ver específicamente el correo de alerta automático, borrar las decisiones anteriores para que el agente las trate como nuevas. Ejecutar en el Django shell:

```python
from pricing.models import DecisionMejorPrecio
DecisionMejorPrecio.objects.all().delete()
```

Luego volver a disparar el ciclo (Paso 4). Como no hay decisión anterior con qué comparar, el agente detecta todo como cambio nuevo y envía el correo de alerta por cada producto.

> ⚠️ Usar solo para demostración. Borrar las decisiones elimina el historial de comparación. Después de la demo volver a correr el ciclo para regenerar los registros.

---

## Paso 6 — Apagar el proyecto

```
stop_all.bat
```

Cierra automáticamente Django, Celery Worker y Celery Beat.

---

## Resumen de comandos

| Comando | Dónde | Para qué |
|---|---|---|
| `start_all.bat` | Explorador / raíz | Levanta Django + Worker + Beat |
| `stop_all.bat` | Explorador / raíz | Apaga todos los procesos |
| `python manage.py shell` + `ciclo_monitoreo.delay()` | Terminal con venv activo | Dispara el ciclo completo en vivo |
| `python manage.py enviar_resumen` | Terminal con venv activo | Envía correo con estado actual sin esperar cambios |
| `DecisionMejorPrecio.objects.all().delete()` | Django shell | Borra historial para forzar correo de alerta en demo |
| `http://127.0.0.1:8000/admin` | Navegador | Panel con todos los datos y registros históricos |
