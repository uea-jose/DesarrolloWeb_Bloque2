@echo off
REM Ejecuta la inicialización de la BD usando Python y .env
REM Requiere Python instalado y las dependencias en requirements.txt
python -m pip install -r requirements.txt
python setup_db.py
pause
