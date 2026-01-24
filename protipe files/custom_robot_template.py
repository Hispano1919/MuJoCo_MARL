"""
custom_robot_template.py - Plantilla para crear nuevos tipos de robots
Autor: Tu Nombre
Fecha: [Fecha]

Instrucciones:
1. Copia este archivo con un nuevo nombre (ej: 'mi_robot.py')
2. Cambia el nombre de la clase (ej: 'MiRobot' y 'MiRobotController')
3. Implementa los métodos requeridos
4. Registra el nuevo tipo en robot_type_manager.py o carga dinámicamente
"""

from robot_types import RobotType
import mujoco
import numpy as np
import cv2

class MiRobotTemplate(RobotType):
    """Plantilla para nuevo tipo de robot."""
    
    def __init__(self):
        super().__init__('mi_tipo')  # Cambiar 'mi_tipo' por el nombre del tipo
    
    def generate_xml_body(self, robot_config):
        """
        Genera XML para el cuerpo del robot.
        
        Args:
            robot_config: Diccionario con configuración del robot
        """
        name = robot_config['name']
        pos = robot_config.get('pos', [0, 0, 0.1])
        color = robot_config.get('color', [0.5, 0.5, 0.5, 1])
        color_str = f"{color[0]} {color[1]} {color[2]} {color[3]}"
        
        # TODO: Implementar diseño XML del robot
        return f'''
        <!-- Robot: {name} (Tipo: mi_tipo) -->
        <body name="{name}_base" pos="{pos[0]} {pos[1]} {pos[2]}">
            <freejoint/> 
            <!-- Aquí va la geometría del robot -->
            <geom name="{name}_cuerpo" type="box" size="0.2 0.2 0.2" rgba="{color_str}" mass="5"/>
            
            <!-- Ejemplo: sensor -->
            <site name="{name}_sensor_site" pos="0.2 0 0.1" />
            
            <!-- Ejemplo: cámara -->
            <camera name="{name}_robot_camera" pos="0.15 0 0.15" quat="0.5 0.5 -0.5 -0.5" />
        </body>'''
    
    def generate_sensors_xml(self, robot_name):
        """Genera XML para sensores del robot."""
        # TODO: Agregar sensores necesarios
        return f'''        <rangefinder name="distancia_{robot_name}" site="{robot_name}_sensor_site" />'''
    
    def generate_actuators_xml(self, robot_name):
        """Genera XML para actuadores del robot."""
        # TODO: Agregar actuadores necesarios
        return f'''        <velocity name="motor_{robot_name}" joint="{robot_name}_motor_joint" kv="10" forcerange="-5 5"/>'''
    
    def init_controller(self, model, data, robot_name, robot_config):
        """Inicializa el controlador específico para este robot."""
        return MiRobotTemplateController(model, data, robot_name, robot_config)


class MiRobotTemplateController:
    """Controlador específico para el nuevo tipo de robot."""
    
    def __init__(self, model, data, robot_name, robot_config):
        self.model = model
        self.data = data
        self.name = robot_name
        self.config = robot_config
        self.renderer = None
        
        # TODO: Inicializar IDs de sensores y actuadores
        # self.sensor_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_SENSOR, f'sensor_{robot_name}')
        # self.actuator_idx = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_ACTUATOR, f'actuator_{robot_name}')
    
    def init_renderer(self, width=640, height=480):
        """Inicializa el renderizador."""
        self.renderer = mujoco.Renderer(self.model, height, width)
    
    def get_sensor_data(self):
        """Obtiene datos de sensores."""
        # TODO: Implementar lectura de sensores
        return None
    
    def set_actuator(self, value):
        """Controla los actuadores."""
        # TODO: Implementar control de actuadores
        pass
    
    def get_camera_image(self):
        """Obtiene imagen de la cámara."""
        if self.renderer is None:
            self.init_renderer()
        
        try:
            self.renderer.update_scene(self.data, camera=f"{self.name}_robot_camera")
            img = self.renderer.render()
            return cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        except:
            return np.zeros((480, 640, 3), dtype=np.uint8)
    
    def detect_red(self, img_bgr):
        """Detecta color rojo en la imagen."""
        if img_bgr is None or img_bgr.size == 0:
            return False, np.zeros((480, 640), dtype=np.uint8)
        
        hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
        mask_red1 = cv2.inRange(hsv, np.array([0, 150, 50]), np.array([10, 255, 255]))
        mask_red2 = cv2.inRange(hsv, np.array([170, 150, 50]), np.array([180, 255, 255]))
        mask_red = cv2.bitwise_or(mask_red1, mask_red2)
        
        return np.sum(mask_red > 0) > 1000, mask_red
    
    def get_info(self):
        """Obtiene información del robot."""
        return {
            'name': self.name,
            'type': self.config.get('type', 'mi_tipo'),
            'sensor_data': self.get_sensor_data()
        }