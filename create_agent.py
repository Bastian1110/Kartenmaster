"""
Script to train a UNO agent
By : Sebastian Mora (@bastian1110)
"""
import numpy as np
from sb3_contrib.common.maskable.policies import MaskableActorCriticPolicy
from sb3_contrib.common.wrappers import ActionMasker
from sb3_contrib.ppo_mask import MaskablePPO
from uno import UnoEnv
from time import time


# This part of the script trains a PPO for 1,000,000 steps,
def mask_fn(env) -> np.ndarray:
    return env.valid_mask(little_help=True)


print("Training new UNO agent")
print("Loading environment")
env = UnoEnv()
env = ActionMasker(env, mask_fn)

print("Training agent")
start = time()
model = MaskablePPO(MaskableActorCriticPolicy, env, verbose=1)
model.learn(1_000_000)
end = time()

model.save("./models/ppo_uno_help")
print(f"Agent trained in {(end - start) / 60} minutes")
