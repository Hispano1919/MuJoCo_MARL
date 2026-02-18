import numpy as np
import gymnasium as gym
from gymnasium import spaces
from pettingzoo import ParallelEnv
import mujoco

# Importamos tus herramientas (asumiendo que están en el mismo directorio)
from Modelos.robot_design import generate_robot_xml
from Modelos.robot_type_manager import RobotTypeManager

class CustomEnvironment(ParallelEnv):
    metadata = {
        "name": "mujoco_multiagent_v0",
        "render_modes": ["human", "rgb_array"],
    }

    def __init__(self, robot_configs=None, render_mode=None):
        """
        Inicializa el mundo de MuJoCo y define los espacios para PettingZoo.
        """
        self.viewer = None

        # 1. Configuración de los Robots
        self.type_manager = RobotTypeManager()
        if robot_configs is None:
            # Configuración por defecto si no se pasa ninguna
            self.robot_configs = [
                {'name': 'explorer', 'type': 'basico', 'pos': [0, 1.5, 0.1], 'color': [0, 0.6, 0, 1]},
                {'name': 'guardian', 'type': 'basico', 'pos': [0, -1.5, 0.1], 'color': [0, 0, 1, 1]},
            ]
        else:
            self.robot_configs = robot_configs

        # 2. Definición de Agentes
        self.agents = [cfg['name'] for cfg in self.robot_configs]
        self.possible_agents = self.agents[:]
        
        # 3. Carga del Modelo MuJoCo
        self.xml_string = generate_robot_xml(self.robot_configs, self.type_manager)
        self.model = mujoco.MjModel.from_xml_string(self.xml_string)
        self.data = mujoco.MjData(self.model)
        
        # 4. Configuración de Espacios (Observation & Action)
        # Asumiremos un LiDAR de 10 rayos + 2 valores de velocidad actual = 12 dimensiones
        num_lidar_rays = 1 
        obs_dim = num_lidar_rays + 2 
        
        # Espacio de Observación: Continuo (distancias y velocidades)
        self.observation_spaces = {
            agent: spaces.Box(low=0, high=np.inf, shape=(obs_dim,), dtype=np.float32)
            for agent in self.agents
        }

        # Espacio de Acción: Continuo (Velocidad rueda izquierda, Velocidad rueda derecha)
        # Rango de -1.0 a 1.0 (luego lo escalaremos en el step)
        self.action_spaces = {
            agent: spaces.Box(low=-10.0, high=10.0, shape=(2,), dtype=np.float32)
            for agent in self.agents
        }

        # 5. Atributos de Estado y Renderizado
        self.render_mode = render_mode
        self.simulation_time = 0.0

    def reset(self, seed=None, options=None):
            """
            Reinicia el entorno al estado inicial.
            """
            # 1. Manejar la semilla para reproducibilidad
            # 1. Configurar semilla (opcional pero recomendado)
            if seed is not None:
                np.random.seed(seed)

            # 2. Reiniciar los datos de la simulación de MuJoCo
            # Esto pone a los robots en sus posiciones iniciales definidas en el XML
            mujoco.mj_resetData(self.model, self.data)
            
            # Opcional: Si quieres aleatoriedad en el inicio, podrías modificar 
            # self.data.qpos aquí antes de llamar a mj_forward
            
            # 3. Sincronizar el estado de la simulación
            mujoco.mj_forward(self.model, self.data)
            
            self.agents = self.possible_agents[:]
            self.simulation_time = 0.0

            # 4. Obtener las observaciones iniciales para cada agente
            observations = {agent: self._get_obs(agent) for agent in self.agents}
            
            # 5. Diccionario de información extra (vacío por ahora)
            infos = {agent: {} for agent in self.agents}

            return observations, infos

    def step(self, actions):
            """
            Aplica las acciones, avanza la simulación y devuelve el nuevo estado.
            """
            # 1. Aplicar acciones a los motores de MuJoCo
            # Suponemos que cada robot tiene 2 actuadores (ruedas) definidos en el XML
            for agent_name, action in actions.items():
                # Buscamos el índice de los actuadores para este robot específico
                # Esto depende de cómo se nombraron en el XML generado
                # Por simplicidad, si el robot 'explorer' tiene actuadores 'explorer_left' y 'explorer_right'
                try:
                    # Obtenemos los IDs de los actuadores
                    left_wheel_id = mujoco.mj_name2id(self.model, mujoco.mjtObj.mjOBJ_ACTUATOR, f"motor_izquierdo_{agent_name}")
                    right_wheel_id = mujoco.mj_name2id(self.model, mujoco.mjtObj.mjOBJ_ACTUATOR, f"motor_derecho_{agent_name}")
                    
                    # Aplicamos la acción (escalada si es necesario)
                    # action[0] y action[1] están en rango [-1, 1] según nuestro action_space
                    self.data.ctrl[left_wheel_id] = action[0] * 10.0  # Ajusta el multiplicador de fuerza
                    self.data.ctrl[right_wheel_id] = action[1] * 10.0
                except:
                    # Si los nombres no coinciden exactamente, aquí iría tu lógica de mapeo
                    pass

            # 2. Avanzar la simulación física
            # Podemos hacer varios pasos internos para que la simulación sea más estable
            n_substeps = 5
            for _ in range(n_substeps):
                mujoco.mj_step(self.model, self.data)
            
            self.simulation_time += self.model.opt.timestep * n_substeps

            # 3. Preparar los diccionarios de retorno
            observations = {agent: self._get_obs(agent) for agent in self.agents}
            
            ##################################################################

            rewards = {}

            for agent in self.agents:
                reward = 0.0

                try:
                    lidar_id = mujoco.mj_name2id(self.model, mujoco.mjtObj.mjOBJ_SENSOR, f"distancia_{agent}")
                    adr = self.model.sensor_adr[lidar_id]
                    dim = self.model.sensor_dim[lidar_id]
                    distancias_lidar = self.data.sensordata[adr : adr + dim]
                    distancia_minima = np.min(distancias_lidar)
                except:
                    distancia_minima = 10.0 # Valor por defecto si falla

                # --- CÁLCULO DE VELOCIDAD LINEAL DESDE LAS RUEDAS ---
                try:
                    # Obtenemos los IDs de las articulaciones (joints) de las ruedas
                    j_left_id = mujoco.mj_name2id(self.model, mujoco.mjtObj.mjOBJ_JOINT, f"{agent}_left_wheel_joint")
                    j_right_id = mujoco.mj_name2id(self.model, mujoco.mjtObj.mjOBJ_JOINT, f"{agent}_right_wheel_joint")
                    
                    # Buscamos su dirección en el vector qvel (velocidades)
                    # jnt_dofadr nos da el índice exacto de la velocidad para esa articulación
                    v_left = self.data.qvel[self.model.jnt_dofadr[j_left_id]]
                    v_right = self.data.qvel[self.model.jnt_dofadr[j_right_id]]
                    
                    # Velocidad lineal aproximada (asumiendo radio de rueda r=1 para el ratio, 
                    # o multiplicando por el radio real si lo conoces)
                    wheel_radius = 0.1 # Ejemplo: 5cm
                    v_lineal = ((v_left + v_right) / 2.0) * wheel_radius
                except Exception as e:
                    v_lineal = 0.0

                # Condición 1: Bonus por estar cerca de un objeto (dist < 0.5)
                if distancia_minima < 0.5:
                    reward -= 1.0  # Bonus por proximidad
                
                # Condición 2: Sumar velocidad lineal (queremos que corra)
                # Solo premiamos velocidad positiva (hacia adelante)
                if v_lineal > 0:
                    reward += v_lineal * 0.5

                rewards[agent] = reward
                # ------------------------------------------
            
            ##################################################################

            # Terminaciones (si el episodio acaba por una condición lógica)
            is_terminations = v_lineal == 0
            terminations = {agent: is_terminations for agent in self.agents}
            
            # Truncamientos (si el episodio acaba por límite de tiempo)
            # Digamos que el episodio dura 20 segundos
            # is_truncated = self.simulation_time >= 20.0
            truncations = {agent: False for agent in self.agents}
            
            # Información adicional
            infos = {agent: {} for agent in self.agents}

            # 4. Gestión de agentes activos
            #if is_truncated:
            #    self.agents = []

            return observations, rewards, terminations, truncations, infos

    def render(self):
            """
            Renderiza la simulación usando el visor interactivo de MuJoCo.
            """
            if self.render_mode is None:
                return

            if self.render_mode == "human":
                if self.viewer is None:
                    # Lanzamos el visor pasivo (no bloqueante)
                    from mujoco import viewer
                    self.viewer = viewer.launch_passive(self.model, self.data)
                
                # Sincronizamos los datos actuales con la ventana
                self.viewer.sync()
                
            elif self.render_mode == "rgb_array":
                # Si necesitas capturar frames para video (opcional)
                renderer = mujoco.Renderer(self.model)
                renderer.update_scene(self.data)
                return renderer.render()

    def close(self):
        """Cierra el visor si existe."""
        if self.viewer is not None:
            self.viewer.close()

    def _get_obs(self, agent):
        """
        Extrae la observación actual de MuJoCo para un agente.
        """
        # Formato de observación esperado: [distancia_lidar, vel_izq, vel_der]
        # (para robots con una sola rueda, vel_der se deja en 0.0)
        obs = np.zeros(self.observation_space(agent).shape, dtype=np.float32)

        # 1) LiDAR: leemos el sensor por nombre y tomamos la distancia mínima
        try:
            lidar_id = mujoco.mj_name2id(
                self.model, mujoco.mjtObj.mjOBJ_SENSOR, f"distancia_{agent}"
            )
            if lidar_id != -1:
                adr = self.model.sensor_adr[lidar_id]
                dim = self.model.sensor_dim[lidar_id]
                lidar_values = self.data.sensordata[adr: adr + dim]
                obs[0] = float(np.min(lidar_values)) if dim > 0 else 0.0
        except Exception:
            obs[0] = 0.0

        # 2) Velocidades de ruedas/articulaciones
        # Soporte para nombres de joint del robot básico y de prueba.
        joint_name_candidates = [
            f"{agent}_base_left_wheel_joint",  # básico (izquierda)
            f"{agent}_base_right_wheel_joint",  # básico (derecha)
            f"{agent}_rueda_joint",            # prueba (rueda única)
        ]

        wheel_velocities = []
        for joint_name in joint_name_candidates:
            try:
                joint_id = mujoco.mj_name2id(
                    self.model, mujoco.mjtObj.mjOBJ_JOINT, joint_name
                )
                if joint_id != -1:
                    dof_adr = self.model.jnt_dofadr[joint_id]
                    wheel_velocities.append(float(self.data.qvel[dof_adr]))
            except Exception:
                continue

        if len(wheel_velocities) >= 2:
            obs[1] = wheel_velocities[0]
            obs[2] = wheel_velocities[1]
        elif len(wheel_velocities) == 1:
            # Robot de una sola rueda
            obs[1] = wheel_velocities[0]
            obs[2] = 0.0

        return obs

    def observation_space(self, agent):
        """Devuelve el espacio de observaciones para un agente específico."""
        return self.observation_spaces[agent]

    def action_space(self, agent):
        """Devuelve el espacio de acciones para un agente específico."""
        return self.action_spaces[agent]
