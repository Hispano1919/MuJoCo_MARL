"""
__init__.py - Paquete para simulación multi-robot
"""

from .robot_type_manager import RobotTypeManager
from .robot_design import generate_robot_xml, save_robot_xml

__all__ = ['RobotTypeManager', 'generate_robot_xml', 'save_robot_xml']