"""
simulation.py - Simulación principal de robots en MuJoCo
Versión simplificada para evitar problemas de importación
Autor: Tu Nombre
Fecha: [Fecha]
"""

import os
import sys
import time
import cv2
import numpy as np
import mujoco
import mujoco.viewer

# Configurar path para importaciones
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importar módulos locales de manera robusta
def import_local_module(module_name):
    """Importa un módulo local de manera robusta."""
    try:
        # Intento 1: Importación normal
        return __import__(module_name)
    except ImportError:
        try:
            # Intento 2: Ejecutar el archivo directamente
            with open(f"{module_name}.py", 'r') as f:
                code = f.read()
            exec(code, globals())
            return sys.modules.get(module_name, None)
        except Exception as e:
            print(f"No se pudo importar {module_name}: {e}")
            return None

# Importar módulos
robot_design_module = import_local_module('robot_design')
robot_type_manager_module = import_local_module('robot_type_manager')
basic_robot_module = import_local_module('basic_robot')
prueba_robot_module = import_local_module('prueba_robot')

if all(m is not None for m in [robot_design_module, robot_type_manager_module]):
    from robot_design import generate_robot_xml, save_robot_xml
    from robot_type_manager import RobotTypeManager
else:
    print("Error: No se pudieron importar los módulos necesarios.")
    sys.exit(1)

# Configurar entorno de visualización
os.environ["MUJOCO_GL"] = "glfw"

def create_control_panel(controllers, simulation_time, paused):
    """Crea el panel de control."""
    panel = np.zeros((180, 800, 3), dtype=np.uint8)
    
    # Título
    cv2.putText(panel, "PANEL DE CONTROL - SIMULACIÓN MULTIROBOT", 
                (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
    
    # Instrucciones
    cv2.putText(panel, "Controles:", (20, 60), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    cv2.putText(panel, "  'q' - Salir", (20, 80), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    cv2.putText(panel, "  'p' - Pausar/Reanudar", (20, 100), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    
    # Estado
    status_color = (0, 0, 255) if paused else (0, 255, 0)
    cv2.putText(panel, f"Estado: {'PAUSADO' if paused else 'EJECUTANDO'}", 
                (400, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.6, status_color, 2)
    cv2.putText(panel, f"Tiempo: {simulation_time:.1f}s", 
                (400, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    
    # Información de robots
    cv2.putText(panel, f"Robots: {len(controllers)}", (400, 140), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    
    return panel

def main():
    """Función principal simplificada."""
    
    print("\n" + "="*50)
    print("SIMULACIÓN MULTIROBOT - INICIANDO")
    print("="*50)
    
    # Crear gestor de tipos
    print("\n1. Inicializando gestor de tipos de robots...")
    type_manager = RobotTypeManager()
    
    # Configuración de robots (versión simplificada)
    robot_configs = [
        {
            'name': 'explorer',
            'type': 'basico',
            'pos': [0, 1.5, 0.1],
            'color': [0, 0.6, 0, 1],
        },
        {
            'name': 'guardian', 
            'type': 'basico',
            'pos': [0, -1.5, 0.1],
            'color': [0, 0, 1, 1],
        },
        {
            'name': 'cube_bot',
            'type': 'prueba',
            'pos': [1.5, 0, 0.1],
            'color': [0.8, 0.2, 0.2, 1],
        },
    ]
    
    print(f"\n2. Configurando {len(robot_configs)} robots...")
    
    # Generar XML
    print("3. Generando XML del escenario...")
    xml_string = generate_robot_xml(robot_configs, type_manager)
    
    # Guardar XML para referencia
    with open("simulacion_actual.xml", "w") as f:
        f.write(xml_string)
    print("   XML guardado en: simulacion_actual.xml")
    
    # Cargar modelo en MuJoCo
    print("4. Cargando modelo en MuJoCo...")
    try:
        model = mujoco.MjModel.from_xml_string(xml_string)
        data = mujoco.MjData(model)
        print("   Modelo cargado correctamente.")
    except Exception as e:
        print(f"   ERROR al cargar modelo: {e}")
        print("   Intentando cargar desde archivo...")
        model = mujoco.MjModel.from_xml_path("simulacion_actual.xml")
        data = mujoco.MjData(model)
    
    # Crear controladores simples (sin usar el sistema de tipos complejo)
    print("\n5. Creando controladores simples...")
    controllers = {}
    
    for config in robot_configs:
        robot_name = config['name']
        robot_type = config.get('type', 'basico')
        
        # Controlador simple basado en tipo
        if robot_type == 'basico':
            # Para robot básico
            from basic_robot import BasicRobotController
            controller = BasicRobotController(model, data, robot_name, config)
        elif robot_type == 'prueba':
            # Para robot de prueba
            from prueba_robot import PruebaRobotController
            controller = PruebaRobotController(model, data, robot_name, config)
        else:
            print(f"   ERROR: Tipo desconocido '{robot_type}' para robot '{robot_name}'")
            continue
        
        controller.init_renderer()
        controllers[robot_name] = controller
        print(f"   Controlador creado para {robot_name} ({robot_type})")
    
    print(f"\n6. Iniciando simulación con {len(controllers)} robots...")
    
    # Variables de control
    paused = False
    simulation_time = 0.0
    
    # Crear ventanas
    cv2.namedWindow("Panel de Control", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Panel de Control", 800, 180)
    
    for robot_name in controllers.keys():
        cv2.namedWindow(f"Cámara - {robot_name}", cv2.WINDOW_NORMAL)
        cv2.resizeWindow(f"Cámara - {robot_name}", 640, 480)
    
    # Lógica simple de control para cada robot
    def simple_control(controller, robot_type):
        """Lógica de control simple."""
        distancia = controller.get_lidar_distance()
        
        if distancia is None:
            if robot_type == 'basico':
                controller.set_wheel_velocities(0, 0)
            elif robot_type == 'prueba':
                controller.set_wheel_velocity(0)
            return "DETENIDO (sin sensor)"
        
        if robot_type == 'basico':
            if distancia < 0.6:
                controller.set_wheel_velocities(-2.0, 2.0)
                return "GIRANDO"
            else:
                controller.set_wheel_velocities(2.0, 2.0)
                return "AVANZANDO"
        
        elif robot_type == 'prueba':
            if distancia < 0.8:
                controller.set_wheel_velocity(0)
                return "DETENIDO"
            else:
                controller.set_wheel_velocity(3.0)
                return "AVANZANDO"
        
        return "DESCONOCIDO"
    
    # Iniciar simulador MuJoCo
    with mujoco.viewer.launch_passive(model, data) as viewer:
        print("\n7. Simulación activa. Presiona 'q' para salir.")
        
        try:
            while viewer.is_running():
                step_start = time.time()
                
                if not paused:
                    # Actualizar cada robot
                    for robot_name, controller in controllers.items():
                        robot_type = controller.config.get('type', 'basico')
                        
                        # Aplicar control
                        estado = simple_control(controller, robot_type)
                        
                        # Obtener y mostrar imagen
                        img = controller.get_camera_image()
                        if img is not None and img.size > 0:
                            cv2.putText(img, f"{robot_name} ({robot_type})", 
                                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                                        0.8, (0, 255, 255), 2)
                            cv2.putText(img, f"Estado: {estado}", 
                                        (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 
                                        0.7, (0, 255, 0), 2)
                            
                            distancia = controller.get_lidar_distance()
                            if distancia:
                                cv2.putText(img, f"LiDAR: {distancia:.2f}m", 
                                            (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 
                                            0.7, (255, 255, 255), 2)
                            
                            cv2.imshow(f"Cámara - {robot_name}", img)
                    
                    # Paso de simulación
                    mujoco.mj_step(model, data)
                    viewer.sync()
                    simulation_time += model.opt.timestep
                
                # Panel de control
                panel = create_control_panel(controllers, simulation_time, paused)
                cv2.imshow("Panel de Control", panel)
                
                # Control de teclado
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    print("\nSaliendo de la simulación...")
                    break
                elif key == ord('p'):
                    paused = not paused
                    print(f"Simulación {'PAUSADA' if paused else 'REANUDADA'}")
                elif key == ord('r'):
                    mujoco.mj_resetData(model, data)
                    print("Posiciones reiniciadas")
                
                # Mantener tiempo real
                elapsed = time.time() - step_start
                if elapsed < model.opt.timestep:
                    time.sleep(model.opt.timestep - elapsed)
        
        except KeyboardInterrupt:
            print("\nSimulación interrumpida.")
        
        finally:
            cv2.destroyAllWindows()
            print("\n" + "="*50)
            print("SIMULACIÓN FINALIZADA")
            print(f"Tiempo: {simulation_time:.1f}s, Robots: {len(controllers)}")
            print("="*50)

if __name__ == "__main__":
    main()