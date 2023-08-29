from uno import UnoEnv
from sb3_contrib.ppo_mask import MaskablePPO
import numpy as np


def mask_fn(env) -> np.ndarray:
    return env.valid_mask(little_help=True)


def test_trained_agent():
    env = UnoEnv()
    model = MaskablePPO.load("ppo_uno")  # Load the trained model

    obs, _ = env.reset()
    done = False
    total_reward = 0

    while not done:
        action, _ = model.predict(obs)  # Predict the action using the model
        obs, reward, done, _trash, info = env.step(action)
        total_reward += reward

        # Optional: Print some information for debugging
        print(
            f"Action: {action}, Reward: {reward}, Total Reward: {total_reward}, Info: {info}"
        )

    print(f"Episode finished with total reward: {total_reward}")


def play_with_agent():
    env = UnoEnv(n_players=2)
    model = MaskablePPO.load("ppo_uno")  # Load the trained model

    obs, _ = env.reset()
    done = False
    total_reward = 0

    while not done:
        env.observation_to_human(obs)
        if env.actual_player == 1:
            action, _ = model.predict(
                obs, action_masks=mask_fn(env)
            )  # Predict the action using the model
            obs, reward, done, _trash, info = env.step(action)
            total_reward += reward

            # Optional: Print some information for debugging
            print(
                f"Action: {action}, Reward: {reward}, Total Reward: {total_reward}, Info: {info}"
            )
        else:
            action = int(input("Enter your action: "))
            obs, reward, done, _tuncated, info = env.step(action)
            print(f"Action: {action}, Reward: {reward}, Info: {info}")


play_with_agent()
