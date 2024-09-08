"""
This is a playgorund that (will) contain usefull functions to play with UNO agents in the terminal
By : Sebastian Mora (@Bastian1110)
"""

from single_agent.uno import UnoEnv
from sb3_contrib.ppo_mask import MaskablePPO
import numpy as np


def ppo_test_trained_agent(model, mask):
    env = UnoEnv()
    model = MaskablePPO.load(model)

    obs, _ = env.reset()
    done = False
    total_reward = 0

    while not done:
        action, _ = model.predict(obs, action_masks=env.valid_mask(little_help=mask))
        obs, reward, done, _truncated, info = env.step(action)
        total_reward += reward
        print(
            f"Action: {action}, Reward: {reward}, Total Reward: {total_reward}, Info: {info}"
        )

    print(f"Episode finished with total reward: {total_reward}")


def ppo_play_with_agent(model, mask):
    env = UnoEnv(n_players=2)
    model = MaskablePPO.load(model)

    obs, _ = env.reset()
    done = False
    total_reward = 0

    while not done:
        env.observation_to_human(obs)
        if env.actual_player == 1:
            action, _ = model.predict(
                obs, action_masks=env.valid_mask(little_help=mask)
            )
            obs, reward, done, _trash, info = env.step(action)
            total_reward += reward

            print(
                f"Action: {action}, Reward: {reward}, Total Reward: {total_reward}, Info: {info}"
            )
        else:
            action = int(input("Enter your action: "))
            obs, reward, done, _tuncated, info = env.step(action)
            print(f"Action: {action}, Reward: {reward}, Info: {info}")


import argparse

parser = argparse.ArgumentParser(
    description="This is a playgorund that (will) contain usefull function to play with UNO agents"
)

parser.add_argument("-m", "--model", type=str, help="Model path")
parser.add_argument(
    "-t",
    "--type",
    choices=["ppo_normal", "ppo_valid"],
    help="Type of UNO agent you are running",
)
parser.add_argument(
    "-i",
    "--interactive",
    action="store_true",
    help="Simulate a human-interactive episode",
)


if __name__ == "__main__":
    args = parser.parse_args()
    if not args.model or not args.type:
        print("Missig parameters MODEL or TYPE, use --h for help")
        quit()
    print(f"Karten master playground 🌊")
    if args.type == "ppo_normal":
        print(f"Loading model : {args.model}")
        print(f"Interpreting as  : normal ppo")
        if not args.interactive:
            print("Simulating an entire episode")
            ppo_test_trained_agent(args.model, False)
            quit()
        print("Interactive episode")
        ppo_play_with_agent(args.model, False)

    if args.type == "ppo_valid":
        print(f"Loading model : {args.model}")
        print(f"Interpreting as  : valid ppo")
        if not args.interactive:
            print("Simulating an entire episode")
            ppo_test_trained_agent(args.model, True)
            quit()
        print("Interactive episode")
        ppo_play_with_agent(args.model, True)
