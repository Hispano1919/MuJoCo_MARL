import functools
import gymnasium
from gymnasium.spaces import Box, Dict
from pettingzoo import ParallelEnv
from pettingzoo.utils import wrappers

class MultiRobotEnv(ParallelEnv):
    metadata = {"render_modes": ["human", "rgb_array"], "name": "mujoco_marl_v0"}

    def __init__(self, robot_configs, type_manager):
        super().__init__()
        self.robot_configs = robot_configs
        self.type_manager = type_manager
        
        # 1. Definir nombres de agentes
        self.agents = [cfg['name'] for cfg in robot_configs]
        self.possible_agents = self.agents[:]
        
        # 2. Configurar MuJoCo (inicialización similar a tu main)
        self.xml_string = generate_robot_xml(self.robot_configs, self.type_manager)
        self.model = mujoco.MjModel.from_xml_string(self.xml_string)
        self.data = mujoco.MjData(self.model)
        
        # 3. Inicializar controladores (para acceder a sensores)
        self.controllers = {}
        for config in robot_configs:
            name = config['name']
            # Reutilizamos tu lógica de controladores actual
            if config['type'] == 'basico':
                from basic_robot import BasicRobotController
                self.controllers[name] = BasicRobotController(self.model, self.data, name, config)
            # ... agregar otros tipos

    @functools.lru_cache(maxsize=None)
    def observation_space(self, agent):
        # Ejemplo: Distancia LiDAR (1 valor) + Posición (3 valores)
        return Box(low=-np.inf, high=np.inf, shape=(4,), dtype=np.float32)

    @functools.lru_cache(maxsize=None)
    def action_space(self, agent):
        # Ejemplo: Velocidad ruedas Izq/Der
        return Box(low=-5.0, high=5.0, shape=(2,), dtype=np.float32)

    def reset(self, seed=None, options=None):
        mujoco.mj_resetData(self.model, self.data)
        
        observations = {agent: self._get_obs(agent) for agent in self.agents}
        infos = {agent: {} for agent in self.agents}
        return observations, infos

    def _get_obs(self, agent):
        # Usamos tus métodos actuales del controlador
        ctrl = self.controllers[agent]
        dist = ctrl.get_lidar_distance() or 2.0 # Valor por defecto
        pos = self.data.body(agent).xpos # Posición real del robot
        return np.array([dist, pos[0], pos[1], pos[2]], dtype=np.float32)

    def step(self, actions):
        # 1. Aplicar acciones a los actuadores de MuJoCo
        for agent, action in actions.items():
            # Aquí mapeas la acción al motor correspondiente
            # Ejemplo simplificado:
            ctrl = self.controllers[agent]
            if hasattr(ctrl, 'set_wheel_velocities'):
                ctrl.set_wheel_velocities(action[0], action[1])
        
        # 2. Avanzar la física
        mujoco.mj_step(self.model, self.data)
        
        # 3. Calcular recompensas, terminaciones y observaciones
        observations = {a: self._get_obs(a) for a in self.agents}
        
        # Ejemplo de recompensa: +1 por moverse, -100 por chocar
        rewards = {}
        terminations = {a: False for a in self.agents}
        truncations = {a: False for a in self.agents}
        
        for a in self.agents:
            dist = self.controllers[a].get_lidar_distance() or 2.0
            rewards[a] = 0.1 # Recompensa por sobrevivir
            if dist < 0.2: # Colisión inminente
                rewards[a] = -1.0
                # terminations[a] = True # Opcional: terminar si choca
        
        infos = {a: {} for a in self.agents}
        
        return observations, rewards, terminations, truncations, infos

    def render(self):
        # Aquí puedes integrar tu lógica de OpenCV o el viewer de MuJoCo
        pass