import gymnasium as gym
from uno import UnoEnv
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
from time import time

vec_env = make_vec_env(UnoEnv, n_envs=4)

model = PPO("MlpPolicy", vec_env, verbose=1)

start = time()
model.learn(10000000)
end = time()
print(f"Total minutes : {(end - start) / 60}")
model.save(f"ppo_uno")
