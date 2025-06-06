#!/bin/bash

# Activar entorno virtual
source ./venv/scripts/activate

# Ejecutar el servidor Python
python server.py

# Evitar que la ventana se cierre automáticamente (esperar entrada del usuario)
read -p "Presiona Enter para salir..."
