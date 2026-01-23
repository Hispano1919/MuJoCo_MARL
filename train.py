import numpy as np
import gymnasium as gym
from stable_baselines3 import PPO
import supersuit as ss
import os

# Importamos tu entorno (asegúrate de que el archivo se llame environment.py o ajusta el import)
from environment import CustomEnvironment 

def train():
    # 1. Crear el entorno
    # No usamos render_mode='human' aquí para que entrene rápido sin ventanas
    env = CustomEnvironment(render_mode=None)

    # 2. Wrapper de SuperSuit para compatibilidad con Stable Baselines 3
    # concat_vec_envs_v1: Toma todos los agentes y los pone en un solo "batch" vectorizado.
    # Esto permite que SB3 entrene una sola política para todos los agentes a la vez.
    env = ss.pettingzoo_env_to_vec_env_v1(env)
    
    # Concatenamos los entornos para correrlos en paralelo (simulamos 1 entorno con N agentes)
    env = ss.concat_vec_envs_v1(env, 1, num_cpus=0, base_class='stable_baselines3')

    # 3. Definir el modelo PPO
    # MlpPolicy: Red neuronal densa estándar (no usamos imágenes, sino vectores numéricos)
    model = PPO(
        "MlpPolicy", 
        env, 
        verbose=1, 
        learning_rate=0.0003,
        batch_size=256,
        gamma=0.99  # Factor de descuento
    )

    print("--- Comenzando el entrenamiento ---")
    # Entrenamos por 100,000 pasos (ajusta esto según necesites)
    model.learn(total_timesteps=100000)
    print("--- Entrenamiento finalizado ---")

    # 4. Guardar el modelo
    model.save("mujoco_multiagent_policy")
    print("Modelo guardado como 'mujoco_multiagent_policy.zip'")
    
    env.close()

def eval_and_render():
    """
    Carga el modelo entrenado y lo visualiza.
    """
    print("--- Iniciando Visualización ---")
    
    # Creamos el entorno DE NUEVO, esta vez con render_mode='human'
    env = CustomEnvironment(render_mode="human")
    
    # Aplicamos EL MISMO wrapper. Es crucial que la estructura sea idéntica al entrenamiento
    env = ss.pettingzoo_env_to_vec_env_v1(env)
    env = ss.concat_vec_envs_v1(env, 1, num_cpus=0, base_class='stable_baselines3')

    # Cargamos el modelo
    model = PPO.load("mujoco_multiagent_policy")

    obs = env.reset()
    
    try:
        while True:
            # El modelo predice la acción
            # deterministic=True hace que el robot use lo mejor que aprendió sin explorar
            action, _states = model.predict(obs, deterministic=True)
            
            obs, rewards, dones, infos = env.step(action)
            
            # En entornos vectorizados, 'dones' es un array. Si alguno termina, reiniciamos manual o automáticamente
            # SuperSuit reinicia automáticamente los sub-entornos, así que solo renderizamos.
            env.render()
            
    except KeyboardInterrupt:
        print("Deteniendo visualización...")
    finally:
        env.close()

if __name__ == "__main__":
    # Paso 1: Entrenar
    train()
    
    # Paso 2: Ver el resultado
    eval_and_render()