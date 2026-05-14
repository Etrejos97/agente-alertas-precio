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
| Scraping | BeautifulSoup + Requests |
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
EMAIL_DESTINATARIO=tucorreo@gmail.com
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

**8. Levantar el servidor**
```bash
python manage.py runserver
```

Panel de administración: http://127.0.0.1:8000/admin

## Estructura del proyecto

```
agente_precios/
├── config/          → Configuración Django, Celery
├── products/        → Modelos Producto y PalabraClave
├── stores/          → Modelo Tienda
├── scrapers/        → BaseScraper y scrapers por tienda
├── .env             → Variables de entorno (no se sube)
└── requirements.txt
```

## Estado del desarrollo

- [x] Fase 1 — Configuración y estructura base
- [ ] Fase 2 — Scrapers por tienda
- [ ] Fase 3 — Motor de precios y comparación
- [ ] Fase 4 — Tarea periódica y notificaciones
- [ ] Fase 5 — Integración y pruebas finales
