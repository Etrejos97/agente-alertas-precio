@echo off
cd /d %~dp0
call venv\Scripts\activate.bat
celery -A config worker --loglevel=info --pool=solo --concurrency=1
pause