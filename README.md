# Agente de Alertas de Precio

Proyecto académico — Asignatura: Redes de Datos
Institución: Tecnológico de Antioquia  
Versión: 1.0 — MVP | Mayo 2026

## ¿Qué hace?

Sistema que monitorea automáticamente los precios de productos alimenticios
en las páginas web de Éxito, Olímpica y Carulla. Cuando detecta el mejor
precio o un cambio relevante, envía una notificación por correo electrónico
con la justificación de la decisión.

## Stack tecnológico

| Componente | Tecnología |
|---|---|
| Backend | Django 5.2 + Python 3.12 |
| Base de datos | PostgreSQL 17 |
| Tareas periódicas | Celery + django-celery-beat |
| Cola de mensajes | Redis (Memurai en Windows) |
| Scraping | BeautifulSoup + Requests + Playwright |
| Correo | Brevo API |
| Variables de entorno | python-decouple |

## Requisitos previos

- Python 3.12
- PostgreSQL 17 (puerto 5433)
- Memurai (Redis para Windows)
- Git

## Instalación local

**1. Clonar el repositorio**
```bash
git clone https://github.com/Etrejos97/agente-alertas-precio.git
cd agente-alertas-precio
```

**2. Crear y activar el entorno virtual**
```bash
python -m venv venv
source venv/Scripts/activate  # Git Bash
```

**3. Instalar dependencias**
```bash
pip install -r requirements.txt
```

**4. Crear el archivo `.env`** en la raíz del proyecto con este contenido:
```
SECRET_KEY=tu-clave-secreta
DEBUG=True
DATABASE_NAME=agente_precios_db
DATABASE_USER=agente_user
DATABASE_PASSWORD=agente1234
DATABASE_HOST=localhost
DATABASE_PORT=5433
CELERY_BROKER_URL=redis://localhost:6379/0
BREVO_API_KEY=tu-api-key
BREVO_SENDER_EMAIL=tucorreo@gmail.com
BREVO_SENDER_NAME=Agente de Precios
ALERT_RECIPIENT_EMAIL=tucorreo@gmail.com
```

**5. Crear la base de datos en PostgreSQL**
```sql
CREATE DATABASE agente_precios_db;
CREATE USER agente_user WITH PASSWORD 'agente1234';
GRANT ALL PRIVILEGES ON DATABASE agente_precios_db TO agente_user;
GRANT ALL ON SCHEMA public TO agente_user;
ALTER DATABASE agente_precios_db OWNER TO agente_user;
```

**6. Aplicar migraciones**
```bash
python manage.py migrate
```

**7. Crear superusuario**
```bash
python manage.py createsuperuser
```

## Levantar el proyecto

### Opción 1 — Script automático (recomendado en Windows)

Ejecuta `start_all.bat` desde la raíz del proyecto. Abre automáticamente tres ventanas:
- Django en `http://127.0.0.1:8000`
- Celery Worker
- Celery Beat

Para detener todo: ejecuta `stop_all.bat`.

### Opción 2 — Manual (tres terminales separadas)

```bash
# Terminal 1 — Django
python manage.py runserver

# Terminal 2 — Celery Worker
celery -A config worker --loglevel=info --pool=solo --concurrency=1

# Terminal 3 — Celery Beat
celery -A config beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

> **Nota:** En Windows es obligatorio usar `--pool=solo` para evitar errores de permisos con el pool `prefork` de Celery.

Panel de administración: http://127.0.0.1:8000/admin

## Comandos útiles

```bash
# Enviar correo resumen con el estado actual de todos los precios (demostración manual)
python manage.py enviar_resumen
```

## Estructura del proyecto

```
agente-alertas-precio/
├── config/          → Configuración Django y Celery
├── products/        → Modelos Producto y PalabraClave
├── stores/          → Modelo Tienda
├── scrapers/        → BaseScraper y scrapers por tienda (Carulla, Éxito, Olímpica)
├── pricing/         → Motor de comparación y decisión de mejor precio
├── monitoring/      → Tarea periódica ciclo_monitoreo (Celery) y comando enviar_resumen
├── notifications/   → Envío de alertas por correo (Brevo)
├── start_all.bat    → Levanta Django + Worker + Beat automáticamente
├── stop_all.bat     → Detiene todos los procesos
├── .env             → Variables de entorno (no se sube)
└── requirements.txt
```

## Estado del desarrollo

- [x] Fase 1 — Configuración y estructura base
- [x] Fase 2 — Scrapers por tienda (Carulla, Éxito, Olímpica)
- [x] Fase 3 — Motor de precios y comparación
- [x] Fase 4 — Tarea periódica y notificaciones por correo
- [x] Fase 5 — Integración, pruebas y automatización local
