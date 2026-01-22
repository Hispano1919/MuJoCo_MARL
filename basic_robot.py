"""
basic_robot.py - Robot básico diferencial con torre de sensores
Versión con importación robusta
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

class BasicRobot(RobotType):
    """Robot básico diferencial con torre de sensores."""
    
    def __init__(self):
        super().__init__('basico')
    
    def generate_xml_body(self, robot_config):
        """Genera XML para el robot básico."""
        name = robot_config['name']
        pos = robot_config.get('pos', [0, 0, 0.1])
        color = robot_config.get('color', [0, 0.6, 0, 1])
        color_str = f"{color[0]} {color[1]} {color[2]} {color[3]}"
        
        return f'''
        <!-- Robot: {name} (Tipo: básico) -->
        <body name="{name}_base" pos="{pos[0]} {pos[1]} {pos[2]}">
            <freejoint/> 
            <geom name="{name}_base_visual" type="box" size="0.3 0.2 0.1" pos="0 0 0.05" rgba="{color_str}" mass="15" contype="0" conaffinity="0"/>
            
            <!-- Torre de sensores -->
            <body name="{name}_sensor_tower" pos="0.1 0 0.175">
                <geom type="cylinder" size="0.05 0.02" rgba="1 1 1 1" mass="0.1"/>
                <site name="{name}_lidar_site" pos="0.05 0 0" /> 
                <camera name="{name}_robot_camera" pos="0.05 0 0.02" quat="0.5 0.5 -0.5 -0.5" />
            </body>

            <!-- Ruedas -->
            <body name="{name}_left_wheel" pos="-0.15 0.23 0" quat="0.7071 0.7071 0 0">
                <joint name="{name}_base_left_wheel_joint" type="hinge" axis="0 0 1" damping="0.5"/>
                <geom type="cylinder" size="0.1 0.025" rgba="0.7 0.7 0.7 1" friction="1.5" mass="1"/>
            </body>
            <body name="{name}_right_wheel" pos="-0.15 -0.23 0" quat="0.7071 0.7071 0 0">
                <joint name="{name}_base_right_wheel_joint" type="hinge" axis="0 0 1" damping="0.5"/>
                <geom type="cylinder" size="0.1 0.025" rgba="0.7 0.7 0.7 1" friction="1.5" mass="1"/>
            </body>
            
            <!-- Rueda loca -->
            <body name="{name}_caster_wheels" pos="0.2 0 -0.05">
                <geom type="sphere" size="0.05" rgba="0.7 0.7 0.7 1" friction="0.005" mass="0.5"/>
            </body>
        </body>'''
    
    def generate_sensors_xml(self, robot_name):
        return f'''        <rangefinder name="distancia_{robot_name}" site="{robot_name}_lidar_site" />'''
    
    def generate_actuators_xml(self, robot_name):
        return f'''        <velocity name="motor_izquierdo_{robot_name}" joint="{robot_name}_base_left_wheel_joint" kv="20" forcerange="-10 10"/>
        <velocity name="motor_derecho_{robot_name}" joint="{robot_name}_base_right_wheel_joint" kv="20" forcerange="-10 10"/>'''


class BasicRobotController:
    """Controlador para robot básico."""
    
    def __init__(self, model, data, robot_name, robot_config):
        self.model = model
        self.data = data
        self.name = robot_name
        self.config = robot_config
        self.renderer = None
        
        # IDs de sensores y actuadores
        self.lidar_id = mujoco.mj_name2id(
            model, mujoco.mjtObj.mjOBJ_SENSOR, f'distancia_{robot_name}'
        )
        self.ctrl_left_idx = mujoco.mj_name2id(
            model, mujoco.mjtObj.mjOBJ_ACTUATOR, f'motor_izquierdo_{robot_name}'
        )
        self.ctrl_right_idx = mujoco.mj_name2id(
            model, mujoco.mjtObj.mjOBJ_ACTUATOR, f'motor_derecho_{robot_name}'
        )
    
    def init_renderer(self, width=640, height=480):
        self.renderer = mujoco.Renderer(self.model, height, width)
    
    def get_lidar_distance(self):
        if self.lidar_id != -1:
            return self.data.sensordata[self.lidar_id]
        return None
    
    def set_wheel_velocities(self, left_vel, right_vel):
        if self.ctrl_left_idx != -1:
            self.data.ctrl[self.ctrl_left_idx] = left_vel
        if self.ctrl_right_idx != -1:
            self.data.ctrl[self.ctrl_right_idx] = right_vel
    
    def get_camera_image(self):
        if self.renderer is None:
            self.init_renderer()
        
        try:
            self.renderer.update_scene(self.data, camera=f"{self.name}_robot_camera")
            img = self.renderer.render()
            return cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        except:
            return np.zeros((480, 640, 3), dtype=np.uint8)