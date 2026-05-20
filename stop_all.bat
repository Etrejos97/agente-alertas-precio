@echo off
echo Cerrando procesos de Django y Celery...

taskkill /F /IM python.exe /T >nul 2>&1
taskkill /F /IM celery.exe /T >nul 2>&1

echo Procesos detenidos.
pause