import numpy as np

from sb3_contrib.common.maskable.policies import MaskableActorCriticPolicy
from sb3_contrib.common.wrappers import ActionMasker
from sb3_contrib.ppo_mask import MaskablePPO

from uno import UnoEnv


def mask_fn(env) -> np.ndarray:
    return env.valid_mask(little_help=False)


env = UnoEnv()
env = ActionMasker(env, mask_fn)

model = MaskablePPO(MaskableActorCriticPolicy, env, verbose=1)
model.learn(5_000_000)

model.save("ppo_uno")
