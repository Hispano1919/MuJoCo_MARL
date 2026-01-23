"""
robot_design.py - Diseñador principal de escenas con múltiples robots
Autor: Tu Nombre
Fecha: [Fecha]
"""

from robot_type_manager import RobotTypeManager

def generate_robot_xml(robot_configs, type_manager=None):
    """
    Genera XML de MuJoCo con múltiples robots de diferentes tipos.
    
    Args:
        robot_configs: Lista de diccionarios con configuración de cada robot.
            Cada diccionario debe contener:
            - 'name': nombre del robot
            - 'type': tipo de robot (ej: 'basico', 'prueba')
            - 'pos': posición inicial [x, y, z]
            - 'color': color RGBA [r, g, b, a]
        type_manager: Instancia de RobotTypeManager. Si es None, se crea una.
    
    Returns:
        String con el XML completo de MuJoCo
    """
    if type_manager is None:
        type_manager = RobotTypeManager()
    
    # Encabezado XML con assets
    xml_parts = ['''<mujoco model="multi_robot">
    <compiler angle="radian" meshdir="assets" />
    <option gravity="0 0 -9.81" timestep="0.002" iterations="50" />

    <asset>
        <material name="grey" rgba="0.7 0.7 0.7 1" />
        <material name="white" rgba="1 1 1 1" />
        <texture name="grid" type="2d" builtin="checker" rgb1=".1 .2 .3" rgb2=".2 .3 .4" width="300" height="300" mark="edge" markrgb=".2 .3 .4"/>
        <material name="grid" texture="grid" texrepeat="1 1" texuniform="true"/>
    </asset>

    <visual>
        <headlight ambient="0.4 0.4 0.4" diffuse="0.8 0.8 0.8"/>
    </visual>

    <worldbody>
        <light pos="0 0 3" dir="0 0 -1" directional="true"/>
        <geom name="floor" type="plane" size="5 5 .05" material="grid" friction="1 0.005 0.0001" contype="1" conaffinity="1"/>
        <body name="box_obstacle_1" pos="0 5 0.2" >
            <geom type="box" size="5 0.2 0.2" rgba="1 0 0 1" contype="3" conaffinity="3"/>
        </body>
        <body name="box_obstacle_2" pos="0 -5 0.2" >
            <geom type="box" size="5 0.2 0.2" rgba="1 0 0 1" contype="3" conaffinity="3"/>
        </body>
        <body name="box_obstacle_3" pos="5 0 0.2" >
            <geom type="box" size="0.2 5 0.2" rgba="1 0 0 1" contype="3" conaffinity="3"/>
        </body>
        <body name="box_obstacle_4" pos="-5 0 0.2" >
            <geom type="box" size="0.2 5 0.2" rgba="1 0 0 1" contype="3" conaffinity="3"/>
        </body>
        ''']

    # Listas para sensores y actuadores
    sensors_xml = []
    actuators_xml = []
    
    # Agregar cuerpos de robots
    for config in robot_configs:
        robot_name = config['name']
        robot_type = config.get('type', 'basico')
        
        # Obtener el tipo de robot
        robot_type_instance = type_manager.get_type(robot_type)
        if not robot_type_instance:
            print(f"Error: Tipo '{robot_type}' no encontrado para robot '{robot_name}'")
            continue
        
        # Generar XML del cuerpo del robot
        robot_xml = robot_type_instance.generate_xml_body(config)
        xml_parts.append(robot_xml)
        
        # Acumular sensores y actuadores
        sensor_xml = robot_type_instance.generate_sensors_xml(robot_name)
        if sensor_xml:
            sensors_xml.append(sensor_xml)
        
        actuator_xml = robot_type_instance.generate_actuators_xml(robot_name)
        if actuator_xml:
            actuators_xml.append(actuator_xml)
    
    xml_parts.append('''    </worldbody>''')
    
    # Sección de sensores
    if sensors_xml:
        xml_parts.append('''    <sensor>''')
        xml_parts.extend(sensors_xml)
        xml_parts.append('''    </sensor>''')
    
    # Sección de actuadores
    if actuators_xml:
        xml_parts.append('''    <actuator>''')
        xml_parts.extend(actuators_xml)
        xml_parts.append('''    </actuator>''')
    
    xml_parts.append('''</mujoco>''')
    
    return '\n'.join(xml_parts)

def save_robot_xml(xml_string, filename="robots_generated.xml"):
    """
    Guarda el XML generado en un archivo.
    
    Args:
        xml_string: String con el XML
        filename: Nombre del archivo de salida
    """
    with open(filename, "w") as f:
        f.write(xml_string)
    print(f"XML guardado en: {filename}")