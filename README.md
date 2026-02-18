# MuJoCo_MARL

Proyecto para simulación y entrenamiento **multiagente** de robots en MuJoCo, con dos flujos principales:

- **Simulación interactiva** con cámaras por robot y panel de control (`simulation.py`).
- **Entrenamiento RL** con PettingZoo + SuperSuit + Stable-Baselines3 (`train.py`).

---

## Características principales

- Arquitectura modular por tipo de robot mediante `RobotTypeManager`.
- Generación dinámica de escenas MuJoCo desde configuración de robots (`Modelos/robot_design.py`).
- Entorno multiagente compatible con `ParallelEnv` de PettingZoo (`Entornos/environment.py`).
- Soporte inicial para tipos de robot:
  - `basico`
  - `prueba`
- Controladores con acceso a:
  - actuadores de rueda
  - sensor tipo rangefinder/LiDAR
  - cámara del robot
- Flujo de entrenamiento con PPO para política compartida entre agentes.

---

## Estructura del proyecto

```text
MuJoCo_MARL/
├── simulation.py                     # Simulación interactiva con visor MuJoCo + panel OpenCV
├── train.py                          # Entrenamiento y evaluación con PPO
├── simulacion_actual.xml             # XML generado de la última simulación
├── requeriments.txt                  # Dependencias de Python
├── Entornos/
│   └── environment.py                # Entorno multiagente (PettingZoo ParallelEnv)
├── Modelos/
│   ├── robot_design.py               # Generador de XML MuJoCo multi-robot
│   ├── robot_type_manager.py         # Registro/carga de tipos de robot
│   ├── basic_robot.py                # Tipo/controlador robot diferencial
│   └── prueba_robot.py               # Tipo/controlador robot de prueba
└── protipe files/
    ├── custom_robot_template.py      # Plantilla para crear nuevos robots
    └── config_multi_type.json        # Ejemplo de configuración de varios robots
```

---

## Requisitos

1. Python 3.10+ recomendado.
2. MuJoCo instalado y funcional.
3. Dependencias del archivo `requeriments.txt`.

Instalación:

```bash
python -m venv .venv
source .venv/bin/activate   # En Windows: .venv\Scripts\activate
pip install -r requeriments.txt
```

> Nota: En Linux, si el render no inicia, revisa drivers OpenGL/GLFW y configuración de MuJoCo.

---

## Uso rápido

### 1) Simulación interactiva

```bash
python simulation.py
```

Qué hace:

- Construye una escena MuJoCo a partir de una lista de robots.
- Guarda el XML de la escena en `simulacion_actual.xml`.
- Abre el visor de MuJoCo y ventanas OpenCV por robot.

Controles en ejecución:

- `q`: salir
- `p`: pausar/reanudar
- `r`: reiniciar posiciones

---

### 2) Entrenamiento + evaluación RL

```bash
python train.py
```

Qué hace:

1. Crea `CustomEnvironment` sin render para entrenar.
2. Lo adapta a SB3 con SuperSuit.
3. Entrena PPO.
4. Guarda el modelo en `mujoco_multiagent_policy.zip`.
5. Lanza una visualización de evaluación (`render_mode="human"`).

---

## Cómo modificar el proyecto

## A) Cambiar los robots de la simulación

Edita `robot_configs` dentro de `simulation.py`.

Ejemplo de entrada:

```python
robot_configs = [
    {
        'name': 'explorer',
        'type': 'basico',
        'pos': [0, 1.5, 0.1],
        'color': [0, 0.6, 0, 1],
    },
    {
        'name': 'guardian',
        'type': 'prueba',
        'pos': [1.5, -1.0, 0.1],
        'color': [0.2, 0.2, 0.9, 1],
    },
]
```

Campos importantes por robot:

- `name`: identificador único (se usa para nombrar sensores/actuadores/joints)
- `type`: tipo registrado en `RobotTypeManager`
- `pos`: posición inicial `[x, y, z]`
- `color`: color RGBA `[r, g, b, a]`

---

## B) Cambiar lógica de entrenamiento

En `train.py` puedes modificar, por ejemplo:

- `total_timesteps` en `model.learn(...)`
- hiperparámetros PPO (`learning_rate`, `batch_size`, `gamma`)
- wrappers de vectorización de SuperSuit

También puedes pasar una configuración propia al entorno:

```python
env = CustomEnvironment(robot_configs=mi_config, render_mode=None)
```

---

## C) Crear un nuevo tipo de robot

Usa `protipe files/custom_robot_template.py` como base:

1. Copia el archivo (por ejemplo `Modelos/mi_robot.py`).
2. Implementa la clase del tipo y su controlador:
   - `generate_xml_body(...)`
   - `generate_sensors_xml(...)`
   - `generate_actuators_xml(...)`
   - `init_controller(...)`
3. Registra el nuevo tipo en `Modelos/robot_type_manager.py` o cárgalo dinámicamente.

Carga dinámica (ejemplo):

```python
type_manager.load_custom_type(
    "Modelos/mi_robot.py",
    "MiRobot",
    "mi_tipo"
)
```

Luego úsalo en la configuración:

```json
{
  "name": "mi_robot_1",
  "type": "mi_tipo",
  "pos": [0.0, 0.0, 0.1],
  "color": [0.5, 0.3, 0.8, 1.0]
}
```

---

## Troubleshooting básico

- Si falla la creación del modelo, revisa `simulacion_actual.xml` para detectar errores de sintaxis o nombres.
- Si un robot no responde, valida que los nombres de actuadores/joints/sensores coincidan entre:
  - XML generado
  - controlador del robot
  - entorno (`Entornos/environment.py`)
- Si no hay visualización, valida instalación de MuJoCo + OpenGL/GLFW.

---

## Próximas mejoras sugeridas

- Centralizar configuración en un JSON único y cargarlo tanto en `simulation.py` como en `train.py`.
- Añadir tests de sanidad para validar XML generado y espacios de observación/acción.
- Estandarizar nombres de joints/sensores para facilitar agregar nuevos tipos de robot.

