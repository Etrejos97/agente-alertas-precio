@echo off
start "Django" cmd /k "cd /d %~dp0 && call venv\Scripts\activate.bat && python manage.py runserver"
start "Celery Worker" cmd /k "cd /d %~dp0 && call venv\Scripts\activate.bat && celery -A config worker --loglevel=info --pool=solo --concurrency=1"
start "Celery Beat" cmd /k "cd /d %~dp0 && call venv\Scripts\activate.bat && celery -A config beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler"