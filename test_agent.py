from uno import UnoEnv
from stable_baselines3 import PPO


def test_trained_agent():
    env = UnoEnv()
    model = PPO.load("ppo_uno")  # Load the trained model

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
    env = UnoEnv()
    model = PPO.load("ppo_uno")  # Load the trained model

    obs, _ = env.reset()
    done = False
    total_reward = 0

    while not done:
        env.observation_to_human(obs)
        if env.actual_player == 1:
            action, _ = model.predict(obs)  # Predict the action using the model
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
