import ray
from ray.rllib.algorithms import PPOConfig, PPO
from ray.rllib.policy.policy import PolicySpec
from ray.tune.logger import pretty_print
from uno import UnoEnv
import ray.tune as tune 
import gymnasium as gym
import os
import ray
from ray.rllib.algorithms import ppo
from ray.rllib.policy.policy import PolicySpec
from ray.tune import register_env
from ray.rllib.models import ModelCatalog
from agent import TorchActionMaskModel

tune.register_env("uno_multiagent", lambda config: UnoEnv(config))
ModelCatalog.register_custom_model("custom_action_mask_model", TorchActionMaskModel)

def mapping_fn(agent_id, *args, **kwargs):
    return "alpha" if agent_id == 1 else "bravo"

config = (
    PPOConfig()
    .framework("torch")
    .environment("uno_multiagent", disable_env_checking=True)
    .multi_agent(
        policies={
            "alpha" : PolicySpec(config={"gamma": 0.85, "model": {
                        "custom_model": "custom_action_mask_model",
                    },}),
            "bravo" : PolicySpec(config={"gamma": 0.95, "model": {
                        "custom_model": "custom_action_mask_model",
                    },}),
        },
        policy_mapping_fn=mapping_fn
    )
    .rollouts(num_rollout_workers=0) 

)

algo = PPO(config)

for i in range(100):
    result = algo.train()
    print(pretty_print(result))

    if i % 10 == 0:
        checkpoint = algo.save("./models/KartenmasterV2.0")
        print("Checkpoint saved at", checkpoint)
