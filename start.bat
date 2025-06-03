@echo off
REM Activar entorno virtual
call .\venv\Scripts\activate.bat

REM Ejecutar el script Python
python main.py

REM Mantener la ventana abierta para ver cualquier salida o error
pause
