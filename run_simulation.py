#!/usr/bin/env python3
"""
run_simulation.py - Script simplificado para ejecutar la simulación
Úsalo si simulation.py tiene problemas de importación
"""

import os
import sys

# Agregar directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importar después de configurar el path
from simulation import main

if __name__ == "__main__":
    print("Ejecutando simulación desde run_simulation.py...")
    main()