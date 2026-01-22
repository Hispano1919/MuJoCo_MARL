"""
robot_types.py - Tipos base de robots con comportamiento común
Autor: Tu Nombre
Fecha: [Fecha]
"""

import mujoco
import numpy as np
import cv2

class RobotType:
    """Clase base abstracta para todos los tipos de robots."""
    
    def __init__(self, name):
        self.name = name
        self.renderer = None
    
    def generate_xml_body(self, robot_config):
        """Genera el XML del cuerpo del robot - debe ser implementado por subclases."""
        raise NotImplementedError("Subclases deben implementar generate_xml_body")
    
    def generate_sensors_xml(self, robot_name):
        """Genera XML de sensores específicos para este tipo de robot."""
        return ""
    
    def generate_actuators_xml(self, robot_name):
        """Genera XML de actuadores específicos para este tipo de robot."""
        return ""
    
    def init_controller(self, model, data, robot_name, robot_config):
        """Inicializa un controlador específico para este tipo de robot."""
        raise NotImplementedError("Subclases deben implementar init_controller")
    
    def get_sensor_names(self, robot_name):
        """Devuelve nombres de sensores para este tipo de robot."""
        return []
    
    def get_actuator_names(self, robot_name):
        """Devuelve nombres de actuadores para este tipo de robot."""
        return []