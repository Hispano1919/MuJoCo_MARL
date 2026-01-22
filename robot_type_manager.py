"""
robot_type_manager.py - Gestor centralizado de tipos de robots
Autor: Tu Nombre
Fecha: [Fecha]
"""

import importlib
import os
import sys

class RobotTypeManager:
    """Gestor que carga y administra diferentes tipos de robots."""
    
    def __init__(self):
        self.robot_types = {}
        self.load_builtin_types()
    
    def load_builtin_types(self):
        """Carga los tipos de robots incluidos por defecto."""
        try:
            # Cargar tipos básicos dinámicamente
            self._load_type_module('basic_robot', 'BasicRobot', 'basico')
            self._load_type_module('prueba_robot', 'PruebaRobot', 'prueba')
            print(f"Tipos de robots básicos cargados correctamente.")
            print(f"Tipos disponibles: {list(self.robot_types.keys())}")
        except Exception as e:
            print(f"Error cargando tipos básicos: {e}")
            print("Cargando tipos con importación directa...")
            self._load_types_directly()
    
    def _load_type_module(self, module_name, class_name, type_name):
        """Carga un módulo de tipo de robot dinámicamente."""
        try:
            module = importlib.import_module(module_name)
            robot_class = getattr(module, class_name)
            robot_instance = robot_class()
            self.register_type(type_name, robot_instance)
        except Exception as e:
            raise ImportError(f"Error cargando {module_name}: {e}")
    
    def _load_types_directly(self):
        """Carga tipos directamente (fallback)."""
        try:
            # Importación directa para evitar problemas de ruta
            exec(open('basic_robot.py').read(), globals())
            from basic_robot import BasicRobot
            self.register_type('basico', BasicRobot())
        except Exception as e:
            print(f"No se pudo cargar 'basico': {e}")
        
        try:
            exec(open('prueba_robot.py').read(), globals())
            from prueba_robot import PruebaRobot
            self.register_type('prueba', PruebaRobot())
        except Exception as e:
            print(f"No se pudo cargar 'prueba': {e}")
    
    def register_type(self, type_name, robot_type):
        """
        Registra un nuevo tipo de robot.
        
        Args:
            type_name: Nombre del tipo (ej: 'basico', 'prueba')
            robot_type: Instancia de RobotType
        """
        self.robot_types[type_name] = robot_type
        print(f"Tipo de robot registrado: '{type_name}'")
    
    def get_type(self, type_name):
        """
        Obtiene un tipo de robot por nombre.
        
        Args:
            type_name: Nombre del tipo
            
        Returns:
            Instancia de RobotType o None si no existe
        """
        if type_name not in self.robot_types:
            print(f"Advertencia: Tipo '{type_name}' no encontrado. Usando 'basico'.")
            type_name = 'basico'
        
        return self.robot_types.get(type_name)
    
    def list_types(self):
        """Lista todos los tipos de robots disponibles."""
        return list(self.robot_types.keys())
    
    def load_custom_type(self, module_path, class_name, type_name):
        """
        Carga un tipo de robot personalizado desde un módulo.
        
        Args:
            module_path: Ruta al archivo .py
            class_name: Nombre de la clase del robot
            type_name: Nombre para registrar el tipo
        """
        try:
            # Asegurarse de que la ruta esté en sys.path
            module_dir = os.path.dirname(os.path.abspath(module_path))
            if module_dir not in sys.path:
                sys.path.insert(0, module_dir)
            
            # Importar dinámicamente
            module_name = os.path.basename(module_path).replace('.py', '')
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            
            # Instanciar la clase
            robot_class = getattr(module, class_name)
            robot_instance = robot_class()
            
            # Registrar el tipo
            self.register_type(type_name, robot_instance)
            print(f"Tipo personalizado '{type_name}' cargado desde {module_path}")
            
        except Exception as e:
            print(f"Error cargando tipo personalizado: {e}")