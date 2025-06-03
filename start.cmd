@echo off
REM Activar entorno virtual
call .\venv\Scripts\activate.bat

REM Ejecutar el servidor Python
python main.py

REM Evitar que la ventana se cierre automáticamente
timeout /t -1
