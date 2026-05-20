@echo off
cd /d %~dp0
call venv\Scripts\activate.bat
celery -A config beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
pause