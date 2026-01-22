# Simulación Multi-Robot en MuJoCo

Sistema modular para simular múltiples robots autónomos en MuJoCo.

## Estructura del Proyecto
proyecto_robots_modular/
├── robot_types.py           # Tipos base abstractos
├── robot_type_manager.py    # Gestor central de tipos
├── basic_robot.py           # Robot tipo 'basico' (diferencial)
├── prueba_robot.py          # Robot tipo 'prueba' (cubo con rueda)
├── custom_robot_template.py # Plantilla para nuevos tipos
├── robot_design.py          # Diseñador principal de escenas
├── simulation.py            # Simulación principal
├── config_multi_type.json   # Configuración de robots
├── requirements.txt         # Dependencias
└── README.md               # Documentación


## Instalación

1. Instalar MuJoCo desde: https://mujoco.org/download
2. Instalar dependencias de Python:
```bash
pip install -r requirements.txt

## Uso

python simulation.py


Cómo agregar un nuevo tipo de robot:

    Crear un nuevo archivo basado en custom_robot_template.py

    Implementar los métodos requeridos:

        generate_xml_body(): Diseño físico del robot

        generate_sensors_xml(): Sensores específicos

        generate_actuators_xml(): Actuadores específicos

        init_controller(): Controlador específico

    Registrar el nuevo tipo (opciones):

        Modificar robot_type_manager.py para cargarlo automáticamente

        O cargarlo dinámicamente en simulation.py:
    python

    type_manager.load_custom_type(
        "mi_robot.py", 
        "MiRobot", 
        "mi_tipo"
    )

    Usar en la configuración:

json

{
    "name": "mi_robot",
    "type": "mi_tipo",
    "pos": [0, 0, 0.1],
    "color": [0.5, 0.3, 0.8, 1]
}
