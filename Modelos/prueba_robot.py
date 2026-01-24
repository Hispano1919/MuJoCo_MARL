"""
prueba_robot.py - Robot de prueba: cubo con una rueda
Autor: Tu Nombre
Fecha: [Fecha]
"""

import mujoco
import numpy as np
import cv2

# Definición de la clase base si no está disponible
try:
    from robot_types import RobotType
except ImportError:
    # Definición local si no se puede importar
    class RobotType:
        def __init__(self, name):
            self.name = name

class PruebaRobot(RobotType):
    """Robot de prueba simple: cubo con una rueda."""
    
    def __init__(self):
        super().__init__('prueba')
    
    def generate_xml_body(self, robot_config):
        """
        Genera XML para el robot de prueba.
        
        Args:
            robot_config: Diccionario con configuración del robot
        """
        name = robot_config['name']
        pos = robot_config.get('pos', [0, 0, 0.1])
        color = robot_config.get('color', [0.8, 0.2, 0.2, 1])  # Rojo por defecto
        color_str = f"{color[0]} {color[1]} {color[2]} {color[3]}"
        
        return f'''
        <!-- Robot: {name} (Tipo: prueba) -->
        <body name="{name}_base" pos="{pos[0]} {pos[1]} {pos[2]}">
            <freejoint/> 
            <!-- Cubo principal -->
            <geom name="{name}_cubo" type="box" size="0.2 0.2 0.2" pos="0 0 0.2" rgba="{color_str}" mass="8" contype="0" conaffinity="0"/>
            
            <!-- Rueda única -->
            <body name="{name}_rueda" pos="0 0 0" quat="0.7071 0.7071 0 0">
                <joint name="{name}_rueda_joint" type="hinge" axis="0 0 1" damping="0.5"/>
                <geom type="cylinder" size="0.15 0.03" rgba="0.3 0.3 0.3 1" friction="1.5" mass="2"/>
            </body>
            
            <!-- Sensor LiDAR simple -->
            <site name="{name}_lidar_site" pos="0.25 0 0.2" />
            
            <!-- Cámara frontal -->
            <camera name="{name}_robot_camera" pos="0.2 0 0.25" quat="0.5 0.5 -0.5 -0.5" />
        </body>'''
    
    def generate_sensors_xml(self, robot_name):
        """Genera XML para sensores del robot de prueba."""
        return f'''        <rangefinder name="distancia_{robot_name}" site="{robot_name}_lidar_site" />'''
    
    def generate_actuators_xml(self, robot_name):
        """Genera XML para actuadores del robot de prueba."""
        return f'''        <velocity name="motor_{robot_name}" joint="{robot_name}_rueda_joint" kv="15" forcerange="-8 8"/>'''
    
    def init_controller(self, model, data, robot_name, robot_config):
        """Inicializa el controlador específico para robot de prueba."""
        return PruebaRobotController(model, data, robot_name, robot_config)
    
    def get_sensor_names(self, robot_name):
        return [f'distancia_{robot_name}']
    
    def get_actuator_names(self, robot_name):
        return [f'motor_{robot_name}']


class PruebaRobotController:
    """Controlador específico para robot de prueba."""
    
    def __init__(self, model, data, robot_name, robot_config):
        self.model = model
        self.data = data
        self.name = robot_name
        self.config = robot_config
        self.renderer = None
        
        # Inicializar IDs
        self.lidar_id = mujoco.mj_name2id(
            model, mujoco.mjtObj.mjOBJ_SENSOR, f'distancia_{robot_name}'
        )
        self.ctrl_idx = mujoco.mj_name2id(
            model, mujoco.mjtObj.mjOBJ_ACTUATOR, f'motor_{robot_name}'
        )
    
    def init_renderer(self, width=640, height=480):
        """Inicializa el renderizador."""
        self.renderer = mujoco.Renderer(self.model, height, width)
    
    def get_lidar_distance(self):
        """Obtiene distancia del LiDAR."""
        if self.lidar_id != -1:
            return self.data.sensordata[self.lidar_id]
        return None
    
    def set_wheel_velocity(self, velocity):
        """Establece velocidad de la rueda."""
        if self.ctrl_idx != -1:
            self.data.ctrl[self.ctrl_idx] = velocity
    
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
            'type': 'prueba',
            'lidar_distance': self.get_lidar_distance(),
            'has_lidar': self.lidar_id != -1,
            'has_actuator': self.ctrl_idx != -1
        }